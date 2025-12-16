import datetime
import ipaddress

def generate_summary(scan_results, timestamp):
    lines = []
    lines.append("==================================================")
    lines.append("FINAL SUMMARY")
    lines.append("==================================================")

    # --- HELPER: Safe Sorting for IPs and Hostnames ---
    def sort_key(target):
        try:
            # Handle IPv4 and IPv6
            return (0, ipaddress.ip_address(target))
        except ValueError:
            # Handle Hostnames (sort them after IPs alphabetically)
            return (1, target)

    # Sort hosts safely
    sorted_hosts = sorted(scan_results.keys(), key=sort_key)

    for host in sorted_hosts:
        data = scan_results[host]
        state = data.get('state', 'unknown')
        
        lines.append(f"Host: {host}")
        lines.append(f"  - State: {state}")

        # ------------------------------
        # PORTS + SERVICES (Combined)
        # ------------------------------
        protocols = data.get("protocols", {})
        open_ports_list = []

        for proto, ports in protocols.items():
            for port, info in ports.items():
                if info.get("state") == "open":
                    svc = info.get("service") or "unknown"
                    # Format: "80/tcp (http)"
                    open_ports_list.append(f"{port}/{proto} ({svc})")

        # --- LOGIC FIX: Distinguish between "Clean Scan" and "No Scan" ---
        if open_ports_list:
            lines.append(f"  - Open ports: {', '.join(open_ports_list)}")
        else:
            if state == 'up':
                # Host is UP, but no ports were returned -> Firewall/Closed
                lines.append("  - Result: 0 open ports found (all scanned ports closed/filtered)")
            else:
                # Host is DOWN or actually not scanned
                lines.append("  - Result: Host appears offline or blocking ping")

        # ------------------------------
        # HOST-SCRIPT RESULTS (NSE)
        # ------------------------------
        host_scripts = data.get("host_scripts")
        if host_scripts:
            lines.append("  - Host scripts:")
            for script_name, output in host_scripts.items():
                # Clean up output: take first line, max 60 chars
                clean_out = output.splitlines()[0][:60]
                lines.append(f"      * {script_name}: {clean_out}...")

        # ------------------------------
        # PORT-SCRIPT RESULTS (NSE)
        # ------------------------------
        port_scripts = data.get("port_scripts")
        if port_scripts:
            lines.append("  - Port scripts:")
            for port_key, scripts in port_scripts.items():
                lines.append(f"      * Port {port_key}:")
                for sname, stext in scripts.items():
                    clean_out = stext.splitlines()[0][:60]
                    lines.append(f"          - {sname}: {clean_out}...")

        # ------------------------------
        # OS DETECTION
        # ------------------------------
        os_info = data.get("osmatch")
        if os_info:
            lines.append("  - OS Detection:")
            # Limit to top 3 matches to save space
            for match in os_info[:3]:
                name = match.get("name")
                acc = match.get("accuracy")
                lines.append(f"      * {name} ({acc}% confidence)")

        lines.append("") # Empty line for spacing

    lines.append("==================================================")
    lines.append("ALL SCANS COMPLETED")
    # Updated to use modern timezone-aware UTC
    lines.append(f"Finished: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("==================================================")

    return "\n".join(lines)