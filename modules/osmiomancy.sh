#!/bin/bash

# === OSMIOMANCY - Filesystem Scryer & Persistence Oracle ===
# Author: Botond "ahu" Vaski
# Version: 1.1 (Glassveil)

LOG_DIR="~/.kaylarecon/logs/osmiomancy"
mkdir -p "$LOG_DIR"
OSMIO_LOG="$LOG_DIR/osmiomancy-$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$OSMIO_LOG") 2>&1

echo "[*] OSMIOMANCY initialized at $(date)"
echo "[*] Scanning for persistence vectors and writable config paths..."

# === Check Functions ===

check_writable() {
  [[ -w "$1" ]] && echo "[!] Writable: $1"
}

check_writable_dir() {
  [[ -d "$1" && -w "$1" ]] && echo "[!] Writable directory: $1"
}

# === 1. User Init Files ===
echo "[*] Scanning user init files..."
for file in ~/.bashrc ~/.bash_profile ~/.profile ~/.zshrc; do
  [[ -f "$file" ]] && check_writable "$file"
done

# === 2. Global Init Files ===
echo "[*] Scanning global shell init scripts..."
for file in /etc/bash.bashrc /etc/profile /etc/zsh/zshrc; do
  [[ -f "$file" ]] && check_writable "$file"
done

# === 3. Cron Directories ===
echo "[*] Checking cron persistence..."
check_writable_dir /etc/cron.d
check_writable_dir /etc/cron.hourly
check_writable_dir /etc/cron.daily
check_writable_dir /etc/cron.weekly
check_writable_dir /etc/cron.monthly

# === 4. rc.local and init.d ===
echo "[*] Scanning legacy startup scripts..."
[[ -f /etc/rc.local ]] && check_writable /etc/rc.local
check_writable_dir /etc/init.d

# === 5. systemd Service Files ===
echo "[*] Scanning systemd unit paths..."
UNIT_DIRS=(
  /etc/systemd/system
  /usr/lib/systemd/system
  /lib/systemd/system
)
for dir in "${UNIT_DIRS[@]}"; do
  check_writable_dir "$dir"
done

# === 6. Environment Sourcing ===
echo "[*] Checking environment files..."
check_writable /etc/environment
check_writable /etc/profile.d/custom.sh
check_writable_dir /etc/profile.d

# === 7. Crontab Binary Write Abuse (advanced) ===
echo "[*] Crontab binary self-check..."
[[ -w "$(which crontab)" ]] && echo "[!] Writable crontab binary: $(which crontab)"

# === Done ===
echo "[+] OSMIOMANCY complete. Log archived at: $OSMIO_LOG"
