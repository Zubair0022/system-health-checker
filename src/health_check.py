#!/usr/bin/env python3
"""
System Health Checker (macOS)
Exit codes:
0 = OK
1 = WARNING
2 = CRITICAL
"""

import os
import subprocess
import shutil
from datetime import datetime


def run(cmd):
    return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()


def bytes_to_gb(b):
    return round(b / (1024 ** 3), 2)


# -------------------------
# System checks
# -------------------------

def cpu_load():
    load1 = os.getloadavg()[0]
    cores = os.cpu_count() or 1
    return round((load1 / cores) * 100, 2)


def memory_info():
    page_size = int(run(["sysctl", "-n", "hw.pagesize"]))
    total_bytes = int(run(["sysctl", "-n", "hw.memsize"]))

    vm = run(["vm_stat"]).splitlines()
    stats = {}

    for line in vm:
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = val.strip().replace(".", "")
        if not val.isdigit():
            continue
        stats[key.strip()] = int(val)

    free_pages = stats.get("Pages free", 0)
    inactive_pages = stats.get("Pages inactive", 0)

    available_bytes = (free_pages + inactive_pages) * page_size

    return {
        "total_gb": bytes_to_gb(total_bytes),
        "available_gb": bytes_to_gb(available_bytes),
    }


def disk_usage(path="/"):
    total, used, free = shutil.disk_usage(path)
    return {
        "used_pct": round((used / total) * 100, 2),
        "free_gb": bytes_to_gb(free),
    }


# -------------------------
# Evaluation
# -------------------------

def evaluate(cpu_pct, mem_avail_gb, disk_used_pct):
    code = 0
    msgs = []

    if cpu_pct >= 90:
        code = 2
        msgs.append(f"CRIT: CPU load {cpu_pct}%")
    elif cpu_pct >= 70:
        code = max(code, 1)
        msgs.append(f"WARN: CPU load {cpu_pct}%")

    if mem_avail_gb <= 1:
        code = 2
        msgs.append(f"CRIT: Memory available {mem_avail_gb} GB")
    elif mem_avail_gb <= 2:
        code = max(code, 1)
        msgs.append(f"WARN: Memory available {mem_avail_gb} GB")

    if disk_used_pct >= 95:
        code = 2
        msgs.append(f"CRIT: Disk usage {disk_used_pct}%")
    elif disk_used_pct >= 85:
        code = max(code, 1)
        msgs.append(f"WARN: Disk usage {disk_used_pct}%")

    if not msgs:
        msgs.append("OK: System healthy")

    return code, msgs


# -------------------------
# Main
# -------------------------

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cpu = cpu_load()
    mem = memory_info()
    disk = disk_usage()

    code, alerts = evaluate(cpu, mem["available_gb"], disk["used_pct"])

    print("=" * 40)
    print("System Health Report")
    print("Time:", now)
    print("=" * 40)
    print(f"CPU Load: {cpu}%")
    print(f"Memory: {mem['available_gb']} GB free / {mem['total_gb']} GB")
    print(f"Disk Used: {disk['used_pct']}%")
    print("-" * 40)

    for a in alerts:
        print(a)

    print("=" * 40)
    exit(code)


if __name__ == "__main__":
    main()
