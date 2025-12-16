import argparse
from presets import PRESETS

def get_args():
    # 1. Create a "parent" parser to hold shared arguments like --preset
    # This ensures --preset works even if typed at the end of the command.
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument("--preset", choices=PRESETS.keys(), default="normal", help="Scan profile")

    # 2. Main Parser
    parser = argparse.ArgumentParser(description="Modular Nmap Scanner")
    subparsers = parser.add_subparsers(dest="mode", required=True, help="Target selection mode")

    # 3. Define Modes (Inherit from base_parser)

    # Mode: AUTO
    # Usage: python run.py auto --preset fast
    p_auto = subparsers.add_parser("auto", parents=[base_parser], help="Auto-discover network interface and scan all")
    p_auto.add_argument('manual_flags', nargs=argparse.REMAINDER, help="Manual Nmap flags override")

    # Mode: PING
    # Usage: python run.py ping --preset deep
    p_ping = subparsers.add_parser("ping", parents=[base_parser], help="Auto-discover, Ping Sweep, then Scan Live Hosts")
    p_ping.add_argument('manual_flags', nargs=argparse.REMAINDER, help="Manual Nmap flags override")

    # Mode: CUSTOM
    # Usage: python run.py custom 192.168.0.0/24 --preset fast
    p_custom = subparsers.add_parser("custom", parents=[base_parser], help="Manually set target IP/CIDR")
    p_custom.add_argument("target_input", help="The specific IP, CIDR, or Range")
    p_custom.add_argument('manual_flags', nargs=argparse.REMAINDER, help="Manual Nmap flags override")

    # Mode: ROUTER-ARP MODE ---
    # Uses Router ARP table.
    p_arp = subparsers.add_parser("router-arp", parents=[base_parser], help="Scan Router ARP Table")
    p_arp.add_argument('manual_flags', nargs=argparse.REMAINDER, help="Manual Nmap flags override")

    # Mode: Clean
    p_clean = subparsers.add_parser("clean", help="Keep only the latest file for each scan type")
    # Mode: DEBUG
    p_debug = subparsers.add_parser("debug", parents=[base_parser], help="Do nothing: keep container alive for debugging")

    return parser.parse_args()