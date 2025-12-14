import subprocess
import os
import requests
import time
import ipaddress
import sys

# Disable warnings for self-signed certs on the router
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_auto_target():
    """
    1. Checks for 'AUTO' environment variable.
    """
    env_target = os.getenv("AUTO")
    if env_target:
        print(f"[LOGIC] Found 'AUTO' Env Variable: {env_target}")
        return env_target
    return None

def get_router_arp():
    """
    Main Orchestrator:
    1. Identify Interface for ROUTER_IP (e.g., ether1)
    2. Run IP Scan on that interface to populate ARP
    3. Fetch and Parse ARP Table
    """
    
    # 1. Configuration
    router_ip = os.getenv("ROUTER_IP", "192.168.0.19")
    subnet = os.getenv("AUTO") # e.g., 192.168.0.0/24

    # 2. IP Scan Logic (Only if we have a subnet to scan)
    if subnet:
        print(f"[LOGIC] Subnet found: {subnet}. Looking for interface...")
        
        # A. Find Interface (with retry)
        interface = _get_active_interface(router_ip)
        
        # B. Run Scan
        if interface:
            print(f"[INFO] Found Router IP {router_ip} on interface '{interface}'.")
            _run_ip_scan(interface, subnet)
        else:
            print(f"[WARN] Could not determine interface for {router_ip}. Skipping scan.")
    else:
        print("[INFO] 'AUTO' variable not set. Skipping IP Scan.")

    # 3. Fetch ARP Table
    print("[INFO] Fetching ARP table from MikroTik...")
    return _fetch_and_parse_arp()

def _get_active_interface(target_ip):
    """
    Runs '/ip address print terse' and parses it to find which 
    interface holds the target_ip.
    """
    # Try twice in case of network blips at container startup
    for attempt in range(2):
        raw_output = _ssh_exec("/ip address print terse")
        
        if not raw_output:
            time.sleep(1)
            continue

        for line in raw_output.splitlines():
            # Example: 0 D address=192.168.0.19/24 network=192.168.0.0 interface=ether1 ...
            if not line.strip(): 
                continue
                
            tokens = line.split()
            ip_match = False
            iface_name = None
            
            for token in tokens:
                if token.startswith("address="):
                    # Extract IP: "address=192.168.0.19/24" -> "192.168.0.19"
                    val = token.split("=", 1)[1]
                    current_ip = val.split("/")[0] 
                    if current_ip == target_ip:
                        ip_match = True
                
                if token.startswith("interface="):
                    iface_name = token.split("=", 1)[1]

            if ip_match and iface_name:
                return iface_name
        
    return None

def _run_ip_scan(interface, subnet):
    """
    Runs the MikroTik ip-scan tool for 10 seconds to populate ARP.
    """
    print(f"[INFO] Running IP Scan on {interface} for 10s...")
    # 'duration' ensures it stops automatically.
    cmd = f"/tool ip-scan interface={interface} address-range={subnet} duration=10s"
    
    # We ignore the output because we only want the side-effect (ARP population)
    _ssh_exec(cmd)

def _fetch_and_parse_arp():
    """
    Parses '/ip arp print' to get IP addresses.
    """
    mikrotik_cmd = "/ip arp print terse without-paging where complete"
    output = _ssh_exec(mikrotik_cmd)
    
    if not output:
        return None

    found_ips = []
    field_name = "address"

    for line in output.splitlines():
        if "failed" in line or "incomplete" in line:
            continue
        
        tokens = line.split()
        for token in tokens:
            if token.startswith(f"{field_name}="):
                ip = token.split("=", 1)[1]
                if ip.count('.') == 3:
                    found_ips.append(ip)

    unique_ips = list(set(found_ips))
    if unique_ips:
        print(f"[INFO] SSH Success! Found {len(unique_ips)} hosts.")
        return " ".join(unique_ips)
    return None

def _ssh_exec(mikrotik_cmd):
    """
    Helper: Connects via SSH and returns raw stdout string.
    """
    host = os.getenv("ROUTER_IP", "192.168.0.19")
    user = os.getenv("ROUTER_USER")
    password = os.getenv("ROUTER_PASS")

    if not user or not password:
        print("[ERROR] Credentials missing.")
        return None

    cmd = [
        "sshpass", "-p", password,
        "ssh", "-o", "StrictHostKeyChecking=no", 
        f"{user}@{host}", 
        mikrotik_cmd
    ]

    try:
        # Check_output waits for command to complete
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8")
    except subprocess.CalledProcessError as e:
        # ip-scan often returns non-zero when timed out or stopped, which is fine.
        # We only log ERROR if it's NOT the ip-scan command.
        if "ip-scan" not in mikrotik_cmd:
            print(f"[ERROR] SSH Command Failed: {mikrotik_cmd} (Exit Code: {e.returncode})")
        return None
    except Exception as e:
        print(f"[ERROR] SSH Error: {e}")
        return None