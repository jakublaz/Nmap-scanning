import os
import re

def load_hosts(summary_path):
    hosts = {}
    if not os.path.exists(summary_path):
        return hosts

    with open(summary_path) as f:
        lines = f.readlines()

    current = None
    for line in lines:
        if line.startswith("Host: "):
            current = line.split()[1].strip()
            hosts[current] = {"ports": []}
        if "- Open ports:" in line:
            ports = line.split(":", 1)[1].strip()
            if ports != "none":
                hosts[current]["ports"] = ports.split(",")

    return hosts


def generate_diff(prev_path, curr_path):
    prev = load_hosts(prev_path)
    curr = load_hosts(curr_path)

    lines = []
    lines.append("==================================================")
    lines.append("AUTO-DIFF (Changes Since Last Scan)")
    lines.append("==================================================")

    if not prev:
        lines.append("[INFO] No previous summary found; all hosts considered new.")
        return "\n".join(lines)

    # new hosts
    for host in curr:
        if host not in prev:
            lines.append(f"❗ New host discovered: {host}")

    # removed hosts
    for host in prev:
        if host not in curr:
            lines.append(f"❌ Host removed: {host}")

    # port changes
    for host in curr:
        if host in prev:
            old_ports = set(prev[host]["ports"])
            new_ports = set(curr[host]["ports"])

            opened = new_ports - old_ports
            closed = old_ports - new_ports

            if opened or closed:
                lines.append(f"⚠ Port change on {host}:")
                if opened:
                    lines.append(f"   + Opened: {','.join(opened)}")
                if closed:
                    lines.append(f"   - Closed: {','.join(closed)}")
            else:
                lines.append(f"✔ Host {host} unchanged")

    return "\n".join(lines)
