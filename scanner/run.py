import os
import sys
from datetime import datetime, timezone
import time
import nmap
import socket
from presets import PRESETS
from parser import run_scan
from summary import generate_summary
from diff import generate_diff
from emailer import send_email
from cli import get_args
from logic import resolve_target, resolve_flags
from cleaner import run_cleanup

SUMMARY_DIR = "/summary"
DATA_DIR = "/data"
# --- HELPER: Sanitize Target for Filename ---
def sanitize_target(target_str):
    # Turns "192.168.0.0/24" into "192-168-0-0-24"
    # Turns "192.168.0.1 192.168.0.2" into "192-168-0-1_192-168-0-2"
    clean = target_str.replace("/", "-").replace(" ", "+")
    return clean

# --- HELPER: Find my own IP ---
def get_container_ip():
    """Finds the container's primary IP address."""
    try:
        # We connect to a dummy external IP (Google DNS) to see which interface is used.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "192.168.0.19"
    
# --- HELPER: Filter my own IP
def filter_targets(target_str):
    """
    Splits the target string into a list and removes the container's own IP.
    """
    if not target_str:
        return None

    # 1. Get the single IP to exclude
    my_ip = get_container_ip()
    
    ip_list = target_str.split()
    
    # 3. Create a new list keeping ONLY IPs that are NOT my_ip
    clean_list = [ip for ip in ip_list if ip != my_ip]

    # Log the removal
    if len(ip_list) != len(clean_list):
        print(f"[LOGIC] Removed my own IP ({my_ip}) from scan list.")

    # 4. Return None if list is empty, otherwise join back to string
    if not clean_list:
        return None

    return " ".join(clean_list)

def get_latest_summary(preset, target):

    prefix = f"summary_{preset}_{target}"

    files = [
        f for f in os.listdir(SUMMARY_DIR) 
        if f.startswith(prefix) and f.endswith(".txt")
    ]
    if not files:
        print(f"[LOG] No previous summary found for {target} ({preset})")
        return None

    # sort by timestamp extracted from filename
    files.sort(reverse=True)
    latest_file = files[0]
    print(f"[LOG] Latest previous {target} ({preset}) summary: {latest_file}")
    return os.path.join(SUMMARY_DIR, latest_file)

def perform_ping_sweep(network_cidr):
    """Runs a Ping Scan (-sn) and returns a list of live IPs."""
    print(f"[INFO] PING MODE: Sweeping {network_cidr} for live hosts...")
    nm = nmap.PortScanner()
    try:
        # -sn = Ping Scan (No port scan)
        # -n  = No DNS resolution (Faster)
        nm.scan(hosts=network_cidr, arguments='-sn -n')
        hosts_up = [x for x in nm.all_hosts() if nm[x].state() == 'up']
        return hosts_up
    except Exception as e:
        print(f"[ERROR] Ping sweep failed: {e}")
        return []

def main():
    # 1. GET ARGUMENTS (CLI)
    args = get_args()

    # Clean
    if args.mode == "clean":
        run_cleanup()
        return

    # DEBUG
    if args.mode == "debug":
        print("[INFO] DEBUG MODE ACTIVE")
        print("[INFO] The container is now sleeping. You can shell into it.")
        print("[INFO] Press Ctrl+C to stop manually.")
        while True:
            try:
                time.sleep(3600)
            except KeyboardInterrupt:
                print("[INFO] Stopping...")
                break
        return

    # 2. RESOLVE TARGET & FLAGS (LOGIC)
    target = resolve_target(args)
    target = filter_targets(target)
    nmap_flags = resolve_flags(args)

    if not target:
        print("[ERROR] No target determined. Exiting.")
        sys.exit(1)

    # 3. RUN SCAN (PARSER)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"[EXEC] Running scan on: {target}")

    results, raw_nmap_text = run_scan(target, nmap_flags)

    data_filename = f"scan_{timestamp}.txt"
    data_path = os.path.join(DATA_DIR, data_filename)
    
    try:
        with open(data_path, "w") as f:
            f.write(raw_nmap_text)
        print(f"[SUCCESS] Saved raw data to: {data_path}")
    except Exception as e:
        print(f"[ERROR] Could not save data file: {e}")

# Check for flag
    flag_file = "/data/scheduled.flag.txt"
    run_origin = "[MANUAL]"

    if os.path.exists(flag_file):
        run_origin = "[SCHEDULED]"
        try:
            os.remove(flag_file) # Delete it so next manual run doesn't get confused
            print(f"[LOGIC] Found scheduler flag ({flag_file}). Set mode to SCHEDULED.")
        except OSError as e:
            print(f"[WARN] Could not delete scheduler flag: {e}")
    else:
        print(f"[LOGIC] Flag file ({flag_file}) not found. Running in MANUAL mode.")


    # 4. REPORTING (SUMMARY & DIFF)
    summary_text = generate_summary(results, timestamp)

    safe_target = sanitize_target(target)

    # Check for Diff
    prev_file = get_latest_summary(args.preset, safe_target)
    summary_path = f"/summary/summary_{args.preset}_{safe_target}_{timestamp}.txt"
    
    # Save current summary
    with open(summary_path, "w") as f:
        f.write(summary_text)

    # Generate Diff if previous exists
    if prev_file:
        diff = generate_diff(prev_file, summary_path)
        summary_text += "\n\n" + diff
        with open(summary_path, "a") as f:
            f.write("\n" + diff)

    # 5. EMAIL
    final_attachment_path = data_path if os.path.exists(data_path) else None
    
    if not final_attachment_path:
        print(f"[WARN] File {data_path} not found. Sending email without attachment.")

    print("[EXEC] Sending email...")
    send_email(
        sender="Container_test@op.pl",
        recipient="user_test125@wp.pl",
        subject=f"{run_origin} Nmap Scan: {args.mode.upper()} - {timestamp}",
        body=summary_text,
        attachment_path=final_attachment_path
    )

    print("[DONE] Scan finished successfully.")


if __name__ == "__main__":
    main()


# docker build -t nmap-python .
# docker save nmap-python:latest -o nmap-python.tar