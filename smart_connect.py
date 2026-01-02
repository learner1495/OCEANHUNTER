import requests
import socket
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def resolve_nobitex_ip():
    print("🔍 Attempting to resolve api.nobitex.ir IP...")
    
    # List of known Nobitex IPs (in case DNS fails completely)
    # These are ArvanCloud/Cloudflare IPs often used by Iranian sites
    backup_ips = ["185.143.233.5", "185.143.234.5", "104.26.12.16", "172.67.70.62"]
    
    try:
        # Try system DNS first
        addr_info = socket.getaddrinfo("api.nobitex.ir", 443)
        ip = addr_info[0][4][0]
        print(f"   ✅ System DNS found: {ip}")
        return ip
    except:
        print("   ⚠️ System DNS failed. Trying manual lookup...")
        # Since we can't query DNS, let's try a direct IP bypass
        # We will use one of the backup IPs
        print(f"   👉 Using Backup IP: {backup_ips[0]}")
        return backup_ips[0]

def main():
    print("-" * 50)
    print("🚀 OCEAN HUNTER V6.2 — SMART CONNECTION")
    print("-" * 50)
    
    target_ip = resolve_nobitex_ip()
    
    # We construct a URL using the IP, but tell the server we want "api.nobitex.ir"
    url = f"https://{target_ip}/market/global-stats"
    
    headers = {
        "Host": "api.nobitex.ir",  # CRITICAL: This tells the server who we are looking for
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*"
    }
    
    print(f"📡 Connecting to IP: {target_ip} (Host: api.nobitex.ir)...")
    
    try:
        response = requests.post(url, headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            print("\n" + "="*50)
            print("✅ SUCCESS! CONNECTION ESTABLISHED")
            print("="*50)
            print(f"Data Sample: {response.text[:200]}...")
        else:
            print(f"❌ Server Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("   This might mean the specific IP is blocked or SSL handshake failed.")

if __name__ == "__main__":
    main()
