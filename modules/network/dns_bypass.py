# modules/network/dns_bypass.py
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
