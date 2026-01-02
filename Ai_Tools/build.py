# AI_Tools/build.py — Build V5.8.1 (Hybrid Shell Resolver)
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
# 1. THE HYBRID RESOLVER (Shell + Hardcode Fallback)
# ═══════════════════════════════════════════════════════════════
DNS_BYPASS_PY = '''# modules/network/dns_bypass.py
import socket
import subprocess
import re
import sys

# Known working IP from previous logs (as a safety net)
# Nobitex often uses ArvanCloud/Cloudflare IPs in this range
FALLBACK_IP = "178.22.122.100" 

def get_ip_from_shell(domain):
    """
    Asks the Windows OS directly via nslookup command.
    This works because your CMD/PowerShell previously proved it can resolve the IP.
    """
    try:
        # Run nslookup
        print(f"   🔎 Asking Windows Shell for {domain} IP...")
        # We enforce using Google DNS (8.8.8.8) explicitly in the shell command to be sure
        result = subprocess.check_output(f"nslookup {domain} 8.8.8.8", shell=True, text=True)
        
        # Extract IP addresses using Regex
        # We look for lines that have 'Address:' or just IPs after the Name section
        ips = re.findall(r"\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b", result)
        
        # Filter out 8.8.8.8 (the DNS server) and local IPs
        valid_ips = [ip for ip in ips if not ip.startswith("8.8.8") and not ip.startswith("192.168") and not ip.startswith("127.")]
        
        if valid_ips:
            # Pick the last one (usually the actual answer, first one is often the DNS server)
            best_ip = valid_ips[-1]
            print(f"   ✅ Shell found IP: {best_ip}")
            return best_ip
            
    except Exception as e:
        print(f"   ⚠️ Shell lookup failed: {e}")
    
    return None

# --- MONKEY PATCH ---
REAL_GETADDRINFO = socket.getaddrinfo

def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    """
    Intercepts Python's DNS requests.
    """
    if host == "api.nobitex.ir":
        print(f"   🛡️ Intercepted DNS for: {host}")
        
        # 1. Try getting IP from Windows Shell (Most reliable in your case)
        resolved_ip = get_ip_from_shell(host)
        
        # 2. Fallback to Hardcoded if Shell fails
        if not resolved_ip:
            resolved_ip = FALLBACK_IP
            print(f"   ⚠️ Using Fallback Hardcoded IP: {resolved_ip}")
        else:
            print(f"   💉 Injecting IP: {resolved_ip}")

        # Return format expected by socket.getaddrinfo
        # (family, type, proto, canonname, sockaddr)
        # This TRICKS requests into connecting to the IP, but keeping the Host Header 'api.nobitex.ir'
        # This solves the 404 error we had in V5.7.7
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (resolved_ip, port))]
        
    return REAL_GETADDRINFO(host, port, family, type, proto, flags)

def apply_patch():
    socket.getaddrinfo = patched_getaddrinfo
'''

# ═══════════════════════════════════════════════════════════════
# 2. NOBITEX API (Same as before)
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
    print("✅ Hybrid DNS Resolver Activated")
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
            # We use the DOMAIN name here. The monkey patch handles the IP.
            print(f"   📡 Requesting: {url}")
            response = self.session.get(url, params=params, timeout=20, verify=False)
            
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
"""OCEAN HUNTER V5.8.1 — HYBRID RESOLVER"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def main():
    print("\\n" + "=" * 60)
    print("🚀 OCEAN HUNTER V5.8.1 — HYBRID SHELL RESOLVER")
    print("=" * 60)

    print("\\n[TEST] Initializing API...")
    
    api = NobitexAPI()
    now = int(time.time())
    
    print("\\n[TEST] Attempting Connection...")
    # Using BTCIRT as standard test
    data = api.get_ohlcv("BTCIRT", from_ts=now-3600, to_ts=now)
    
    if data.get("s") == "ok":
        price = data['c'][-1]
        print(f"\\n" + "=" * 60)
        print(f"✅ SUCCESS! CONNECTION ESTABLISHED!")
        print(f"💰 BTC Price: {price:,.0f} IRT")
        print("=" * 60)
    else:
        print(f"\\n❌ FAILED: {data.get('msg')}")
        
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
    print("\n[1/4] 📝 Configuring Hybrid Resolver...")
    for path, content in FILES_TO_CREATE.items():
        full_path = os.path.join(ROOT, path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      ✅ Updated: {path}")

def step2_git():
    print("\n[2/4] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync("Build V5.8.1: Hybrid Shell Resolver")
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
    print("\n🚀 STARTING BUILD V5.8.1...")
    step1_create_files()
    step2_git()
    step3_context()
    step4_launch()

if __name__ == "__main__":
    main()
