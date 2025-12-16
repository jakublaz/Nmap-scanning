import sys
import nmap
from presets import PRESETS
from discovery import get_auto_target, get_router_arp


def perform_ping_sweep(subnet):
    """
    Runs a Ping Scan (-sn) with extra discovery flags to find stubborn hosts.
    """
    print(f"[LOGIC] Ping Sweeping {subnet}...")
    nm = nmap.PortScanner()
    try:
        # UPDATED ARGUMENTS
        # -sn : Ping Scan (No ports)
        # -n  : No DNS (Speed)
        # -PE : ICMP Echo (Standard Ping)
        # -PS443 : TCP SYN to port 443 (Tricks firewalls)
        # -PA80  : TCP ACK to port 80 (Tricks stateful firewalls)
        # -PP : ICMP Timestamp (Old devices)
        
        args = '-sn -n -PE -PS443 -PA80 -PP'
        
        nm.scan(hosts=subnet, arguments=args)
        hosts_up = [x for x in nm.all_hosts() if nm[x].state() == 'up']
        
        if not hosts_up:
            return None
            
        return " ".join(hosts_up)
    except Exception as e:
        print(f"[ERROR] Ping sweep failed: {e}")
        return None

def resolve_target(args):
    """
    Decides WHO to scan based on the CLI mode.
    Returns a single string of targets for Nmap.
    """
    target = ""

    # 1. CUSTOM MODE
    if args.mode == "custom":
        target = args.target_input
        print(f"[LOGIC] Custom Target: {target}")

    # 2. AUTO MODE (Direct Subnet Scan)
    elif args.mode == "auto":
        print("[LOGIC] Auto-detecting network...")
        target = get_auto_target()
        if not target:
            print("[CRITICAL] Could not detect network interface.")
            sys.exit(1)
        print(f"[LOGIC] Auto Target (Full Subnet): {target}")

    # 3. PING MODE (IP -> Sweep -> Live IPs)
    elif args.mode == "ping":
        print("[LOGIC] Auto-detecting network for Ping Sweep...")
        subnet = get_auto_target()
        if not subnet:
            print("[CRITICAL] Could not detect network.")
            sys.exit(1)
        
        # LOGIC handles the sweep here
        live_hosts = perform_ping_sweep(subnet)
        if not live_hosts:
            print("[LOGIC] No live hosts found.")
            sys.exit(0)
            
        target = live_hosts
        print(f"[LOGIC] Live Targets: {target}")

    # 4. ARP MODE
    elif args.mode == "router-arp":
        print("[LOGIC] ARP-mode selected")
        target = get_router_arp()
        print(f"[LOGIC] Live Targets: {target}")

    return target


def resolve_flags(args):
    """
    Decides HOW to scan.
    Prioritizes manual flags, but rescues --preset if it was swallowed by argparse.
    """
    
    # Check if "--preset" was captured as a manual flag by mistake
    if args.manual_flags and "--preset" in args.manual_flags:
        try:
            # Find where "--preset" is located
            idx = args.manual_flags.index("--preset")
            
            # The next item is the preset name (e.g., "fast")
            if idx + 1 < len(args.manual_flags):
                args.preset = args.manual_flags[idx + 1]
                
                # Remove "--preset" and "fast" from the manual flags list
                # This performs the "delete --preset" action
                del args.manual_flags[idx:idx+2]
                
                print(f"[LOGIC] Detected and extracted preset '{args.preset}' from flags.")
        except ValueError:
            pass

    # If user typed EXTRA flags remaining (e.g. -- -p 80)
    if args.manual_flags:
        # Remove '--' if present and join
        # Note: If manual_flags became empty after the patch above, this is skipped
        remaining_flags = [f for f in args.manual_flags if f != "--"]
        
        if remaining_flags:
            flags = " ".join(remaining_flags)
            print(f"[LOGIC] Using Manual Flags: {flags}")
            return flags
    
    # Otherwise use the preset
    flags = PRESETS[args.preset]
    print(f"[LOGIC] Using Preset '{args.preset}': {flags}")
    return flags