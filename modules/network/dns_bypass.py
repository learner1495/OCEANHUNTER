# modules/network/dns_bypass.py
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
