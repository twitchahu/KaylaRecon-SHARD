#!/bin/bash

# === SEPARATION - Misconfig & Shadow Socket Scanner ===
# Author: Botond "ahu" Vaski
# Version: 1.1 (Anxiety Protocol)

LOG_DIR="~/.kaylarecon/logs/separation"
mkdir -p "$LOG_DIR"
SEP_LOG="$LOG_DIR/separation-$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$SEP_LOG") 2>&1

echo "[*] SEPARATION initialized at $(date)"
echo "[*] Scanning services, sockets, and misconfigurations..."

# === 1. World-writable Service Files ===
echo "[*] Checking for writable service definitions..."
SERVICE_PATHS=(/etc/systemd/system /lib/systemd/system /usr/lib/systemd/system)

for path in "${SERVICE_PATHS[@]}"; do
  if [[ -d "$path" ]]; then
    find "$path" -type f -perm -002 -exec echo "[!] Writable service: {}" \;
  fi
done

# === 2. Active Network Sockets (ss/netstat) ===
echo "[*] Checking active network bindings..."
ss -tulpen 2>/dev/null | grep -v "127.0.0.1" | grep -v "::1" | while read -r line; do
  if echo "$line" | grep -q -E "LISTEN"; then
    PORT=$(echo "$line" | awk '{print $5}' | cut -d: -f2)
    USER=$(echo "$line" | awk '{print $7}' | cut -d',' -f1 | sed 's/uid=//')
    [[ -n "$PORT" && "$PORT" -ge 1024 ]] && echo "[!] Suspicious high port listener: Port $PORT UID=$USER"
  fi
done

# === 3. Unprivileged Binds to Reserved Ports ===
echo "[*] Looking for services binding below 1024 without root..."
netstat -tulpen 2>/dev/null | grep -E ':[0-9]{1,3} ' | while read -r line; do
  PORT=$(echo "$line" | awk '{print $4}' | cut -d: -f2)
  UID=$(echo "$line" | awk '{print $7}' | cut -d'/' -f1)
  if [[ "$PORT" -lt 1024 && "$UID" -ne 0 ]]; then
    echo "[!] Reserved port $PORT bound by UID=$UID (non-root)"
  fi
done

# === 4. Exposed D-Bus Interfaces ===
echo "[*] Probing D-Bus permissions..."
BUSDIR="/etc/dbus-1/system.d"
if [[ -d "$BUSDIR" ]]; then
  find "$BUSDIR" -type f -perm -002 -exec echo "[!] Writable DBus config: {}" \;
fi

# === Completion ===
echo "[+] SEPARATION complete. Log archived at: $SEP_LOG"
