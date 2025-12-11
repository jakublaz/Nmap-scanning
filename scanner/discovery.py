import subprocess
import os
import requests
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
    # TODO ADD request to run hosts to update ARP LIST
    """Ask MikroTik for ARP Table (With Active Fallback)"""
    print("[INFO] Fetching ARP table from MikroTik...")
    # This is with terse so that it only takes those who are not failed
    return _ssh_and_parse("/ip arp print terse without-paging where complete", "address")

def _ssh_and_parse(mikrotik_cmd, field_name):
    host = os.getenv("ROUTER_IP", "192.168.0.19")
    user = os.getenv("ROUTER_USER")
    password = os.getenv("ROUTER_PASS")

    if not user or not password:
        print("[ERROR] Credentials missing.")
        return None

    # Construct the SSH command
    # -o StrictHostKeyChecking=no prevents the "Are you sure?" prompt
    cmd = [
        "sshpass", "-p", password,
        "ssh", "-o", "StrictHostKeyChecking=no", 
        f"{user}@{host}", 
        mikrotik_cmd
    ]

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8")
        
        found_ips = []
        for line in output.splitlines():

            if "failed" in line or "incomplete" in line:
                continue
            # Split by space to find key=value pairs
            tokens = line.split()
            for token in tokens:
                if token.startswith(f"{field_name}="):
                    # Extract value after '='
                    ip = token.split("=", 1)[1]
                    # basic validation to ensure it looks like an IP
                    if ip.count('.') == 3:
                        found_ips.append(ip)

        unique_ips = list(set(found_ips))
        
        if not unique_ips:
            return None
            
        print(f"[INFO] SSH Success! Found {len(unique_ips)} hosts.")
        return " ".join(unique_ips)

    except subprocess.CalledProcessError as e:
        error_msg = e.output.decode('utf-8') if e.output else "No error output captured"
        print(f"[ERROR] SSH Connection Failed. Return Code: {e.returncode}")
        print(f"[ERROR] SSH Output: {error_msg}")
        # If SSH fails, we return None so the main script can try Fallback
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return None