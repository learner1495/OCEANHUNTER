# AI_Tools/build.py — Build V5.8.3 (Precision Filter Strategy)
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
# 1. PRECISION DNS ENGINE (Core Fix Logic)
# ═══════════════════════════════════════════════════════════════
DNS_BYPASS_PY = '''# modules/network/dns_bypass.py
import socket
import subprocess
import re
import sys

# IPs of DNS Providers (WE MUST NOT CONNECT TO THESE)
# These are strictly prohibited from being returned as the target IP
BLACKLIST_IPS = [
    "178.22.122.100", # Shecan 1
    "185.51.200.2",   # Shecan 2
    "1.1.1.1",        # Cloudflare
    "8.8.8.8",        # Google
    "8.8.4.4",        # Google
    "10.10.34.35",    # Internal/VLAN often seen in VPNs
    "127.0.0.1",      # Localhost
    "0.0.0.0"
]

DNS_SERVERS = ["178.22.122.100", "185.51.200.2", ""]

def query_dns(domain, server):
    """Run nslookup with strict filtering"""
    try:
        cmd = f"nslookup {domain} {server}" if server else f"nslookup {domain}"
        print(f"   🔎 Asking {'System Default' if not server else server}...")
        
        # Run command
        result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        
        # Regex to find IP addresses
        all_ips = re.findall(r"\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b", result)
        
        valid_candidates = []
        for ip in all_ips:
            # 1. Filter out local network IPs
            if ip.startswith("192.168.") or ip.startswith("10."):
                continue
                
            # 2. Filter out BLACKLISTED IPs (The DNS servers themselves)
            if ip in BLACKLIST_IPS:
                continue
                
            # 3. Filter out the server we just asked (double check)
            if server and ip == server:
                continue
                
            valid_candidates.append(ip)
            
        if valid_candidates:
            # In nslookup output, the 'Address' of the target is usually the LAST one mentioned
            # specifically under "Non-authoritative answer"
            best_ip = valid_candidates[-1]
            print(f"      ✅ Valid IP Found: {best_ip}")
            return best_ip
        else:
            print("      ⚠️ No valid non-DNS IPs found in output.")
            
    except subprocess.CalledProcessError:
        print(f"      ❌ Lookup failed.")
    except Exception as e:
        print(f"      ⚠️ Error: {e}")
    
    return None

def resolve_nobitex(domain="api.nobitex.ir"):
    """Iterates through DNS providers until a NON-BLACKLIST IP is found"""
    for dns_server in DNS_SERVERS:
        ip = query_dns(domain, dns_server)
        if ip:
            return ip
    return None

# --- MONKEY PATCH ---
REAL_GETADDRINFO = socket.getaddrinfo
CACHED_IP = None

def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    global CACHED_IP
    
    if host == "api.nobitex.ir":
        print(f"   🛡️ Intercepted: {host}")
        
        if CACHED_IP:
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (CACHED_IP, port))]
            
        resolved_ip = resolve_nobitex(host)
        
        if resolved_ip:
            print(f"   💉 Injecting: {resolved_ip}")
            CACHED_IP = resolved_ip
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (resolved_ip, port))]
        else:
            print("   ⚠️ Resolution failed. Fallback to native.")
        
    return REAL_GETADDRINFO(host, port, family, type, proto, flags)

def apply_patch():
    socket.getaddrinfo = patched_getaddrinfo
'''

# ═══════════════════════════════════════════════════════════════
# 2. NOBITEX API (Standard)
# ═══════════════════════════════════════════════════════════════
NOBITEX_API_PY = '''# modules/network/nobitex_api.py
import requests
import urllib3
import sys
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Apply Patch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from modules.network.dns_bypass import apply_patch
    apply_patch()
    print("✅ Precision DNS Engine Activated")
except ImportError:
    print("⚠️ Could not load DNS Bypass")

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False 
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        })

    def get_ohlcv(self, symbol, resolution="60", from_ts=None, to_ts=None):
        url = f"{self.BASE_URL}/market/udf/history"
        params = {"symbol": symbol, "resolution": resolution, "from": from_ts, "to": to_ts}
        
        try:
            print(f"   📡 Connecting to {url} ...")
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
# 3. MAIN TEST
# ═══════════════════════════════════════════════════════════════
MAIN_PY = '''#!/usr/bin/env python3
"""OCEAN HUNTER V5.8.3 — PRECISION FILTER"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def main():
    print("\\n" + "=" * 60)
    print("🚀 OCEAN HUNTER V5.8.3 — PRECISION FILTER")
    print("=" * 60)

    print("\\n[TEST] Initializing...")
    api = NobitexAPI()
    now = int(time.time())
    
    # Try BTCIRT
    data = api.get_ohlcv("BTCIRT", from_ts=now-3600, to_ts=now)
    
    if data.get("s") == "ok":
        price = data['c'][-1]
        print(f"\\n" + "=" * 60)
        print(f"✅ CONNECTION SUCCESSFUL!")
        print(f"💰 BTC Price: {price:,.0f} IRT")
        print("=" * 60)
    else:
        print(f"\\n❌ FAILED: {data.get('msg')}")

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
    print("\n[1/4] 📝 Configuring Precision Filter...")
    for path, content in FILES_TO_CREATE.items():
        full_path = os.path.join(ROOT, path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      ✅ Updated: {path}")

def step2_git():
    print("\n[2/4] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync("Build V5.8.3: Precision DNS Filter")
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
    print("\n🚀 STARTING BUILD V5.8.3...")
    step1_create_files()
    step2_git()
    step3_context()
    step4_launch()

if __name__ == "__main__":
    main()
