#!/bin/sh
set -eu

# Ensure summary directory exists
mkdir -p /summary

# Inject resolv.conf only if 8.8.8.8 is NOT already present
if ! grep -q "8.8.8.8" /etc/resolv.conf 2>/dev/null; then
    echo "Adding Google DNS to /etc/resolv.conf"
    # We overwrite because Alpine’s resolv.conf inside Docker is ephemeral anyway
    # and cannot be reliably appended (musl rewrites it on DHCP updates)
    {
        echo "nameserver 8.8.8.8"
        echo "nameserver 8.8.4.4"
        echo "options edns0 trust-ad"
    } > /etc/resolv.conf
else
    echo "DNS already configured, skipping."
fi

# Pass ALL arguments to Python
exec python3 -u /scanner/run.py "$@"
