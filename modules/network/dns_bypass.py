# modules/network/dns_bypass.py
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
        ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", result)
        
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
