#!/bin/bash

# Wait for hardware initialization
sleep 5

# Lock DNS resolver
echo "nameserver 8.8.8.8" > /etc/resolv.conf

# Configure routes for Xray TProxy
ip rule add fwmark 1 table 100 2>/dev/null || true
ip route add local 0.0.0.0/0 dev lo table 100 2>/dev/null || true
ip rule add fwmark 255 lookup main 2>/dev/null || true

# Enable IPv4 forwarding
sysctl -w net.ipv4.ip_forward=1

# Launch Wi-Fi AP via lnxrouter (replace INTERFACE, SSID, and PASSWORD)
/home/user/linux-router/lnxrouter --ap wlp5s0 "YOUR_SSID" -p "YOUR_PASSWORD" -i enp0s10 --dns 8.8.8.8 --no-virt &

exit 0
