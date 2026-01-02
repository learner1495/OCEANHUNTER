# modules/network/dns_bypass.py
import socket
import subprocess
import re
import sys

# List of DNS servers to query specifically for Iranian domains
# 178.22.122.100 = Shecan
# 185.51.200.2   = Shecan Secondary
# 1.1.1.1        = Cloudflare (Sometimes works for Nobitex Global)
DNS_SERVERS = ["178.22.122.100", "185.51.200.2", "1.1.1.1", ""] # Empty string means system default

def query_dns(domain, server):
    """Run nslookup with a specific server"""
    try:
        cmd = f"nslookup {domain} {server}" if server else f"nslookup {domain}"
        print(f"   🔎 Asking {'System Default' if not server else server} for IP...")
        
        # Use shell=True to access system PATH
        result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        
        # Regex to find IP addresses
        ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", result)
        
        # Filter Logic:
        # 1. Ignore the DNS server's own IP (often appears in first 2 lines)
        # 2. Ignore local IPs
        valid_ips = []
        for ip in ips:
            if ip.startswith("192.168.") or ip.startswith("127.") or ip.startswith("10."):
                continue
            if server and ip == server:
                continue
            valid_ips.append(ip)
            
        if valid_ips:
            # The answer is usually at the end of the output
            found_ip = valid_ips[-1]
            print(f"      ✅ Found: {found_ip}")
            return found_ip
            
    except subprocess.CalledProcessError:
        print(f"      ❌ Server {server} failed to resolve.")
    except Exception as e:
        print(f"      ⚠️ Error: {e}")
    
    return None

def resolve_nobitex(domain="api.nobitex.ir"):
    """Iterates through DNS providers until an IP is found"""
    for dns_server in DNS_SERVERS:
        ip = query_dns(domain, dns_server)
        if ip:
            return ip
    return None

# --- MONKEY PATCH ---
REAL_GETADDRINFO = socket.getaddrinfo

# Cache the resolved IP to avoid querying every time
CACHED_IP = None

def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    global CACHED_IP
    
    if host == "api.nobitex.ir":
        print(f"   🛡️ Intercepted request for: {host}")
        
        if CACHED_IP:
            print(f"   ⚡ Using Cached IP: {CACHED_IP}")
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (CACHED_IP, port))]
            
        # Try to resolve
        resolved_ip = resolve_nobitex(host)
        
        if resolved_ip:
            print(f"   💉 Injecting Resolved IP: {resolved_ip}")
            CACHED_IP = resolved_ip
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (resolved_ip, port))]
        else:
            print("   ⚠️ All lookups failed. Letting Python try natively...")
        
    return REAL_GETADDRINFO(host, port, family, type, proto, flags)

def apply_patch():
    socket.getaddrinfo = patched_getaddrinfo
