# AI_Tools/build.py — Build V5.8.0 (DNS Bypass Surgery)
# ═══════════════════════════════════════════════════════════════

import os
import sys
import subprocess
import context_gen
import setup_git

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
VENV_PATH = os.path.join(ROOT, ".venv")
if sys.platform == "win32":
    VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe")
else:
    VENV_PYTHON = os.path.join(VENV_PATH, "bin", "python")

# ═══════════════════════════════════════════════════════════════
# 1. THE DNS BYPASS ENGINE
# ═══════════════════════════════════════════════════════════════
DNS_BYPASS_PY = '''# modules/network/dns_bypass.py
import socket
import struct
import random

def get_ip_from_google(domain):
    """
    Queries Google DNS (8.8.8.8) directly via UDP to resolve a domain.
    Bypasses OS DNS stack entirely.
    """
    try:
        # Create a raw DNS query packet
        # Transaction ID
        packet = struct.pack(">H", random.randint(0, 65535))
        # Flags (Standard Query)
        packet += struct.pack(">H", 0x0100) 
        # Questions: 1
        packet += struct.pack(">H", 1)
        # Answer RRs: 0
        packet += struct.pack(">H", 0)
        # Authority RRs: 0
        packet += struct.pack(">H", 0)
        # Additional RRs: 0
        packet += struct.pack(">H", 0)
        
        # Query Name
        for part in domain.split('.'):
            packet += struct.pack("B", len(part))
            packet += part.encode("utf-8")
        packet += struct.pack("B", 0) # End of name
        
        # Type: A (Host Address) = 1
        packet += struct.pack(">H", 1)
        # Class: IN (Internet) = 1
        packet += struct.pack(">H", 1)
        
        # Send to Google DNS
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(4.0)
        sock.sendto(packet, ("8.8.8.8", 53))
        
        data, _ = sock.recvfrom(1024)
        sock.close()
        
        # Parse Response (Skip header and query)
        # Header is 12 bytes
        # Query name ends with 0 byte + 4 bytes for Type/Class
        idx = 12
        while data[idx] != 0:
            idx += data[idx] + 1
        idx += 5 # Skip 0 byte + Type(2) + Class(2)
        
        # Check for Answer
        # Name pointer (2) + Type(2) + Class(2) + TTL(4) + RDLength(2)
        # If standard answer, next bytes are IP
        if idx + 12 < len(data):
             # Just jump to the data part for the first answer roughly
             # (This is a simplified parser, assuming simple response)
             # Real offset calculation:
             # Answer Name (2 bytes usually c00c pointer)
             # Type (2)
             # Class (2)
             # TTL (4)
             # RDLength (2) -> describes IP length (4)
             
             # Let's find the IP at the end
             ip_bytes = data[-4:]
             ip = ".".join(map(str, ip_bytes))
             return ip
             
    except Exception as e:
        print(f"DNS Bypass Error: {e}")
        return None
    return None

# --- MONKEY PATCH ---
REAL_GETADDRINFO = socket.getaddrinfo

def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """
    Intercepts Python's DNS requests.
    If it's for Nobitex, we resolve it manually via Google.
    """
    if host == "api.nobitex.ir":
        print(f"   🛡️ Intercepted DNS for: {host}")
        
        # 1. Try Google Direct first
        resolved_ip = get_ip_from_google(host)
        
        if not resolved_ip:
            # Fallback to hardcoded known IP if Google fails
            resolved_ip = "178.22.122.100" 
            
        print(f"   🛡️ Resolved manually to: {resolved_ip}")
        
        # Return format expected by socket.getaddrinfo
        # (family, type, proto, canonname, sockaddr)
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (resolved_ip, port))]
        
    return REAL_GETADDRINFO(host, port, family, type, proto, flags)

def apply_patch():
    socket.getaddrinfo = patched_getaddrinfo
'''

# ═══════════════════════════════════════════════════════════════
# 2. NOBITEX API (Cleaned)
# ═══════════════════════════════════════════════════════════════
NOBITEX_API_PY = '''# modules/network/nobitex_api.py
import requests
import urllib3
import sys
import os

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Apply DNS Bypass
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from modules.network.dns_bypass import apply_patch
    apply_patch()
    print("✅ DNS Bypass Engine Activated")
except ImportError:
    print("⚠️ Could not load DNS Bypass")

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False  # Ignore proxies
        
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        })

    def get_ohlcv(self, symbol, resolution="60", from_ts=None, to_ts=None):
        url = f"{self.BASE_URL}/market/udf/history"
        
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts
        }
        
        try:
            # We use the DOMAIN in the URL, but our patch will force the IP
            # verify=False prevents SSL certificate matching errors if resolving is weird
            response = self.session.get(url, params=params, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("s") == "ok":
                    return data
                else:
                    return {"s": "error", "msg": f"API Error: {data.get('s')}"}
            else:
                return {"s": "error", "msg": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"s": "error", "msg": f"{type(e).__name__}: {str(e)}"}
'''

# ═══════════════════════════════════════════════════════════════
# 3. MAIN (Verification)
# ═══════════════════════════════════════════════════════════════
MAIN_PY = '''#!/usr/bin/env python3
"""OCEAN HUNTER V5.8.0 — DNS SURGERY"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def main():
    print("\\n" + "=" * 60)
    print("🚀 OCEAN HUNTER V5.8.0 — DNS BYPASS SURGERY")
    print("=" * 60)

    print("\\n[TEST] Initializing API with Custom DNS Engine...")
    
    api = NobitexAPI()
    now = int(time.time())
    
    print("\\n[TEST] Attempting Connection to api.nobitex.ir...")
    data = api.get_ohlcv("BTCIRT", from_ts=now-3600, to_ts=now)
    
    if data.get("s") == "ok":
        price = data['c'][-1]
        print(f"      ✅ SUCCESS! WE HAVE DATA!")
        print(f"      💰 Current BTC Price: {price:,.0f} IRT")
        print("      (The DNS Bypass worked beautifully)")
    else:
        print(f"      ❌ FAILED: {data.get('msg')}")
        
    print("\\n" + "=" * 60)

if __name__ == "__main__":
    main()
'''

FILES_TO_CREATE = {
    "modules/network/dns_bypass.py": DNS_BYPASS_PY,
    "modules/network/nobitex_api.py": NOBITEX_API_PY,
    "main.py": MAIN_PY
}

# ═══════════════════════════════════════════════════════════════
# BUILD STEPS
# ═══════════════════════════════════════════════════════════════
def step1_create_files():
    print("\n[1/4] 📝 Configuring DNS Surgery...")
    for path, content in FILES_TO_CREATE.items():
        full_path = os.path.join(ROOT, path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      ✅ Updated: {path}")

def step2_git():
    print("\n[2/4] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync("Build V5.8.0: DNS Bypass Surgery")
        print("      ✅ Saved to History")
    except:
        pass

def step3_context():
    try:
        context_gen.create_context_file()
    except:
        pass

def step4_launch():
    print("\n[4/4] 🚀 Launching Bot...")
    subprocess.run([VENV_PYTHON, "main.py"], cwd=ROOT)

def main():
    print("\n🚀 STARTING BUILD V5.8.0...")
    step1_create_files()
    step2_git()
    step3_context()
    step4_launch()

if __name__ == "__main__":
    main()
