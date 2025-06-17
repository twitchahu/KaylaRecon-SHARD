#!/usr/bin/env python3

# === LAZARUS - Memory Dump Reanimator ===
# Author: Botond "ahu" Vaski
# Version: 1.1 (Black Mirror)

import os
import sys
import hashlib
from datetime import datetime

LOG_DIR = os.path.expanduser("~/.kaylarecon-shard/logs/lazarus")
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_PATH = os.path.join(LOG_DIR, f"lazarus-{timestamp}.log")

def log(msg):
    print(msg)
    with open(LOG_PATH, "a") as f:
        f.write(msg + "\n")

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(4096):
            h.update(chunk)
    return h.hexdigest()

def scan_dump(dump_path):
    if not os.path.isfile(dump_path):
        log(f"[-] Dump not found: {dump_path}")
        sys.exit(1)

    log(f"[*] LAZARUS initialized at {timestamp}")
    log(f"[*] Scanning: {dump_path}")
    sha256 = hash_file(dump_path)
    log(f"[*] SHA256: {sha256}")

    size = os.path.getsize(dump_path)
    log(f"[*] Size: {size} bytes")

    # === String Scan ===
    log("[*] Extracting strings...")
    suspicious = []
    with os.popen(f"strings '{dump_path}'") as s:
        for line in s:
            line = line.strip()
            if any(keyword in line.lower() for keyword in [
                "password", "token", "root", "bash", "/bin/sh", "shadow", "ssh", "malware", "payload"
            ]):
                suspicious.append(line)

    if suspicious:
        log(f"[!] Suspicious strings found ({len(suspicious)}):")
        for s in suspicious:
            log(f"  > {s}")

    # === Header Check (Anti-Forensics) ===
    log("[*] Checking for anti-forensics indicators...")
    with open(dump_path, "rb") as f:
        head = f.read(256)

    null_ratio = head.count(b"\x00") / 256
    if null_ratio > 0.9:
        log("[!] Dump head shows abnormal null padding. Possible header wipe.")

    if head[:4] == b'\x50\x4b\x03\x04':
        log("[!] Dump appears to be compressed (ZIP magic bytes found).")

    log("[+] LAZARUS complete. Log saved to: " + LOG_PATH)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <memory_dump_file>")
        sys.exit(1)

    scan_dump(sys.argv[1])
