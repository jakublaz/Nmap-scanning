import datetime

def generate_summary(scan_results, timestamp):
    lines = []
    lines.append("==================================================")
    lines.append("FINAL SUMMARY")
    lines.append("==================================================")

    for host in sorted(scan_results.keys(), key=lambda ip: tuple(int(x) for x in ip.split('.'))):
        data = scan_results[host]
        lines.append(f"Host: {host}")
        lines.append(f"  - State: {data.get('state', 'unknown')}")

        # ------------------------------
        # PORTS + SERVICES
        # ------------------------------
        protocols = data.get("protocols", {})

        open_ports = []
        services = []

        for proto, ports in protocols.items():
            for port, info in ports.items():
                if info.get("state") == "open":
                    open_ports.append(f"{port}/{proto}")
                    svc = info.get("service") or "unknown"
                    services.append(svc)

        if open_ports:
            lines.append(f"  - Open ports: {', '.join(open_ports)}")
        else:
            if protocols:
                lines.append("  - Open ports: none")
            else:
                lines.append("  - No port scan performed")

        if services:
            lines.append(f"  - Services: {', '.join(services)}")
        else:
            if protocols:
                lines.append("  - Services: none")
            else:
                lines.append("  - Services: N/A (no version scan)")

        # ------------------------------
        # HOST-SCRIPT RESULTS (NSE)
        # ------------------------------
        host_scripts = data.get("host_scripts")
        if host_scripts:
            lines.append("  - Host scripts:")
            for script_name, output in host_scripts.items():
                lines.append(f"      * {script_name}: {output.splitlines()[0]}...")

        # ------------------------------
        # PORT-SCRIPT RESULTS (NSE)
        # ------------------------------
        port_scripts = data.get("port_scripts")
        if port_scripts:
            lines.append("  - Port scripts:")
            for key, scripts in port_scripts.items():
                lines.append(f"      * Port {key}:")
                for sname, stext in scripts.items():
                    lines.append(f"          - {sname}: {stext.splitlines()[0]}...")

        # ------------------------------
        # OS DETECTION
        # ------------------------------
        os_info = data.get("osmatch")
        if os_info:
            lines.append("  - OS Detection:")
            for match in os_info:
                name = match.get("name")
                acc = match.get("accuracy")
                lines.append(f"      * {name} ({acc}% confidence)")
        
                classes = match.get("osclass", [])
                for cls in classes:
                    vendor = cls.get("vendor")
                    family = cls.get("osfamily")
                    gen = cls.get("osgen")
                    lines.append(f"          - {vendor} {family} {gen} ({cls.get('accuracy')}%)")


        lines.append("")

    lines.append("==================================================")
    lines.append("ALL SCANS COMPLETED")
    lines.append(f"Finished: {datetime.datetime.utcnow()}")
    lines.append("==================================================")

    return "\n".join(lines)


