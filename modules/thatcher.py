#!/usr/bin/env python3

# === THATCHER - System Severance / Network Isolation ===
# Author: Botond "ahu" Vaski
# Version: 1.7 (Dissonance)

import os, sys, subprocess as s, time as t, socket as k, random as r, platform

# === basic XOR encoder for logs ===
def x(b): return ''.join(chr(ord(i)^0x13) for i in b)

# === stealth sleep with jitter ===
def z(): t.sleep(r.uniform(0.3, 0.7))

# === suppress output everywhere ===
FNULL = open(os.devnull, 'w')

# === encoded STORMTRANCE emit ===
def v(name, src):
    stamp = s.getoutput("date '+%Y-%m-%d %H:%M:%S'")
    h = k.gethostname()
    entry = f"[STORMTRANCE] [{stamp}] [{h}] VECTOR[{name}] SOURCE[{src}]"
    logp = os.path.expanduser("~/.kaylarecon/logs/guardian.log")
    os.makedirs(os.path.dirname(logp), exist_ok=True)
    with open(logp, 'a') as f: f.write(x(entry) + '\n')
    print(entry)  # Output plaintext to terminal for visibility

# === firewall sever ===
def a():
    system = platform.system()
    if system == "Linux" or system == "Darwin":
        ipt = "/sbin/iptables"
        if not os.path.exists(ipt): return
        ssh = s.getoutput("who | grep pts | awk '{print $5}' | tr -d '()' | head -n1")
        cmds = [
            f"{ipt} -F OUTPUT",
            f"{ipt} -A OUTPUT -p tcp --dport 22 -s {ssh} -j ACCEPT",
            f"{ipt} -A OUTPUT -o lo -j ACCEPT",
            f"{ipt} -A OUTPUT -j DROP"
        ]
        for c in cmds:
            s.call(c, shell=True, stdout=FNULL, stderr=FNULL)
            print(f"Executed: {c}")
            z()
        v("PROTOCOL-SEVER-ACTIVATED", "thatcher.py")
    elif system == "Windows":
        try:
            cmds = [
                'netsh advfirewall firewall delete rule name="BlockAllOutboundExceptSSH"',
                'netsh advfirewall firewall add rule name="BlockAllOutboundExceptSSH" dir=out action=block program=any enable=yes'
            ]
            for c in cmds:
                s.call(c, shell=True, stdout=FNULL, stderr=FNULL)
                print(f"Executed: {c}")
                z()
            v("PROTOCOL-SEVER-ACTIVATED-WIN", "thatcher.py")
        except: pass

# === tool neuter ===
def b():
    system = platform.system()
    tools = ['nmap','netcat','nc','airgeddon','wireshark','tshark','tcpdump']
    for tname in tools:
        path = s.getoutput(f"{'where' if system == 'Windows' else 'command -v'} {tname}")
        if os.path.exists(path):
            try:
                os.chmod(path, 0o000)
                os.rename(path, path + ".~")
                print(f"Neutered: {tname} at {path}")
                v("THATCHER-TOOL-NEUTRAL", "thatcher.py")
            except: pass
        z()

# === interface killer (preserve lo) ===
def c():
    system = platform.system()
    if system == "Windows":
        try:
            out = s.check_output("netsh interface show interface", shell=True).decode()
            for line in out.splitlines():
                if any(skip in line.lower() for skip in ["loopback", "disconnected"]):
                    continue
                name = line.split()[-1]
                s.call(f"netsh interface set interface \"{name}\" admin=disable", shell=True, stdout=FNULL, stderr=FNULL)
                print(f"Disabled interface: {name}")
                z()
            v("THATCHER-INTERFACE-LOCKDOWN-WIN", "thatcher.py")
        except: pass
    else:
        try:
            data = s.check_output("ls /sys/class/net", shell=True).decode().split()
            for iface in data:
                if iface != "lo":
                    s.call(f"ip link set {iface} down", shell=True, stdout=FNULL, stderr=FNULL)
                    print(f"Brought down: {iface}")
                    z()
            v("THATCHER-INTERFACE-LOCKDOWN", "thatcher.py")
        except: pass

# === process hide ===
def d():
    if platform.system() != "Windows":
        try:
            os.sethostname(".")
            os.setsid()
        except: pass

# === start sequence ===
def q():
    d(); a(); c(); b()

# === invoke without trace ===
if __name__ != '__main__':
    exit(0)
if os.getenv("KRECON") != "SEVER":
    sys.exit(0)
q()