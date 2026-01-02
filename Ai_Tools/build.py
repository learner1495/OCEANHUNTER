# AI_Tools/build.py — Build V5.8.4 (DoH + Static Fallback)
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
# 1. DNS OVER HTTPS (DoH) ENGINE
# ═══════════════════════════════════════════════════════════════
DNS_BYPASS_PY = '''# modules/network/dns_bypass.py
import socket
import requests
import json
import random

# --- STATIC FALLBACK IPS ---
# These are known Cloudflare IPs often used by Nobitex.
# Used ONLY if DoH fails.
STATIC_NOBITEX_IPS = [
    "104.26.13.16",
    "104.26.12.16",
    "172.67.70.166"
]

def resolve_doh_google(domain):
    """Resolve IP using Google DNS-over-HTTPS (Bypasses UDP blocks)"""
    try:
        print(f"   ☁️  Requesting DoH from Google for {domain}...")
        url = f"https://dns.google/resolve?name={domain}&type=A"
        # We must disable proxy for the DNS lookup itself
        response = requests.get(url, timeout=5, proxies={"http": None, "https": None})
        
        if response.status_code == 200:
            data = response.json()
            if "Answer" in data:
                # Get the first A record
                for answer in data["Answer"]:
                    if answer["type"] == 1: # Type A
                        ip = answer["data"]
                        print(f"      ✅ DoH Success: {ip}")
                        return ip
    except Exception as e:
        print(f"      ⚠️ DoH Failed: {e}")
    return None

def get_static_ip():
    """Return a random known IP for Nobitex"""
    ip = random.choice(STATIC_NOBITEX_IPS)
    print(f"   ⚠️ Using Static Fallback IP: {ip}")
    return ip

# --- MONKEY PATCH ---
REAL_GETADDRINFO = socket.getaddrinfo
CACHED_IP = None

def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    global CACHED_IP
    
    if host == "api.nobitex.ir":
        print(f"   🛡️ Intercepted: {host}")
        
        if CACHED_IP:
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (CACHED_IP, port))]
            
        # 1. Try DoH (Best Method)
        resolved_ip = resolve_doh_google(host)
        
        # 2. Try Static Fallback (Last Resort)
        if not resolved_ip:
            resolved_ip = get_static_ip()
        
        if resolved_ip:
            print(f"   💉 Injecting: {resolved_ip}")
            CACHED_IP = resolved_ip
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (resolved_ip, port))]
        
    return REAL_GETADDRINFO(host, port, family, type, proto, flags)

def apply_patch():
    socket.getaddrinfo = patched_getaddrinfo
'''

# ═══════════════════════════════════════════════════════════════
# 2. NOBITEX API (Updated imports)
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
    print("✅ DoH DNS Engine Activated")
except ImportError as e:
    print(f"⚠️ Could not load DNS Bypass: {e}")

class NobitexAPI:
    BASE_URL = "https://api.nobitex.ir"

    def __init__(self):
        self.session = requests.Session()
        # CRITICAL: Disable proxies for the main connection too
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
            # verify=False is needed because we might be using a direct IP which doesn't match the SSL cert
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
"""OCEAN HUNTER V5.8.4 — DoH & STATIC"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.network.nobitex_api import NobitexAPI

def main():
    print("\\n" + "=" * 60)
    print("🚀 OCEAN HUNTER V5.8.4 — DoH & STATIC FALLBACK")
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
    print("\n[1/4] 📝 Configuring DoH Engine...")
    for path, content in FILES_TO_CREATE.items():
        full_path = os.path.join(ROOT, path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"      ✅ Updated: {path}")

def step2_git():
    print("\n[2/4] 🐙 Git Sync...")
    try:
        setup_git.setup()
        setup_git.sync("Build V5.8.4: DoH DNS Strategy")
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
    print("\n🚀 STARTING BUILD V5.8.4...")
    step1_create_files()
    step2_git()
    step3_context()
    step4_launch()

if __name__ == "__main__":
    main()
