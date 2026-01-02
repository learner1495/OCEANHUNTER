# modules/network/dns_bypass.py
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
        all_ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", result)
        
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
