#!/bin/bash

# Ожидание инициализации железа
sleep 5

# Фиксация DNS
echo "nameserver 8.8.8.8" > /etc/resolv.conf

# Настройка маршрутов для Xray TProxy
ip rule add fwmark 1 table 100 2>/dev/null || true
ip route add local 0.0.0.0/0 dev lo table 100 2>/dev/null || true
ip rule add fwmark 255 lookup main 2>/dev/null || true

# Включаем пересылку трафика
sysctl -w net.ipv4.ip_forward=1

# Запуск раздачи Wi-Fi (с тем самым & в конце!)
/home/ravenchickd/linux-router/lnxrouter --ap wlp5s0 MyVpnTV -p 12345678 -i enp0s10 --dns 8.8.8.8 --no-virt &

exit 0
