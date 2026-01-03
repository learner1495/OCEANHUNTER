import requests
import socket
import os
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

def check_port(ip, port):
    """Checks if a local port is open."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((ip, int(port)))
    sock.close()
    return result == 0

def test_connection(proxy_url, name):
    print(f"\n🔌 Testing Proxy: {name} -> {proxy_url}")
    proxies = {"http": proxy_url, "https": proxy_url}
    
    try:
        # 1. Test against generic Internet (IP Check)
        print("   Step 1: Pinging Global Internet (ip-api)...")
        resp = requests.get("http://ip-api.com/json", proxies=proxies, timeout=5)
        data = resp.json()
        print(f"   ✅ Internet OK! IP: {data.get('query')} ({data.get('countryCode')})")
        
        # 2. Test against Nobitex (Target)
        print("   Step 2: Pinging Nobitex API...")
        nobitex_url = "https://api.nobitex.ir/market/global-stats"
        resp_nobitex = requests.post(nobitex_url, proxies=proxies, verify=False, timeout=5)
        
        if resp_nobitex.status_code == 200:
            print("   ✅✅✅ NOBITEX CONNECTED SUCCESSFULLY! ✅✅✅")
            return True
        else:
            print(f"   ⚠️ Connected, but HTTP {resp_nobitex.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False

def main():
    print("-" * 50)
    print("🚀 OCEAN HUNTER V6.4 — PROXY AUTO-FIXER")
    print("-" * 50)

    # Candidates to check
    candidates = []
    
    # 1. Check Env Var Port (Likely wrong: 2081)
    env_port = os.getenv("PROXY_PORT")
    if env_port:
        candidates.append(("ENV_CONFIG", "127.0.0.1", int(env_port), "http"))

    # 2. Check Standard V2RayN HTTP (Best for Python)
    candidates.append(("V2RAY_HTTP", "127.0.0.1", 10809, "http"))
    
    # 3. Check Standard V2RayN SOCKS (Alternative)
    candidates.append(("V2RAY_SOCKS", "127.0.0.1", 10808, "socks5"))

    valid_proxy_found = False

    for name, ip, port, protocol in candidates:
        if check_port(ip, port):
            print(f"\n🔍 Port {port} ({name}) is OPEN.")
            
            # Construct proxy string
            if protocol == "socks5":
                # Ensure pysocks is installed for this, otherwise skip or fallback
                proxy_str = f"socks5h://{ip}:{port}"
            else:
                proxy_str = f"http://{ip}:{port}"

            if test_connection(proxy_str, name):
                valid_proxy_found = True
                print("\n" + "="*50)
                print(f"💡 FIX FOUND: Update your .env file to use PORT {port}")
                print(f"   Change PROXY_PORT={port}")
                print(f"   Change PROXY_TYPE={protocol.upper()}")
                print("="*50)
                break
        else:
            print(f"❌ Port {port} ({name}) is CLOSED (Not running).")

    if not valid_proxy_found:
        print("\n⚠️ NO WORKING PROXY FOUND.")
        print("   1. Ensure V2RayN is RUNNING.")
        print("   2. Ensure the bottom bar says 'Enable Tun' or 'System Proxy' is NOT needed, but the core must be running.")

if __name__ == "__main__":
    main()
