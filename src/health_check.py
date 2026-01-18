import os
import shutil
import subprocess
import time
from datetime import datetime

def cpu_load():
    load1, load5, load15 = os.getloadavg()
    return {
        "1min": round(load1, 2),
        "5min": round(load5, 2),
        "15min": round(load15, 2)
    }

def memory_info():
    total_bytes = int(subprocess.check_output(
        ["sysctl", "-n", "hw.memsize"]
    ).strip())

    vm_stat = subprocess.check_output(["vm_stat"]).decode()
    pages_free = pages_active = pages_inactive = pages_spec = 0

    for line in vm_stat.splitlines():
        if "Pages free" in line:
            pages_free = int(line.split(":")[1].strip().strip("."))
        elif "Pages active" in line:
            pages_active = int(line.split(":")[1].strip().strip("."))
        elif "Pages inactive" in line:
            pages_inactive = int(line.split(":")[1].strip().strip("."))
        elif "Pages speculative" in line:
            pages_spec = int(line.split(":")[1].strip().strip("."))

    page_size = 4096
    available = (pages_free + pages_inactive + pages_spec) * page_size

    return {
        "total_gb": round(total_bytes / (1024**3), 2),
        "available_gb": round(available / (1024**3), 2)
    }

def disk_usage(path="/"):
    usage = shutil.disk_usage(path)
    return {
        "total_gb": round(usage.total / (1024**3), 2),
        "used_gb": round(usage.used / (1024**3), 2),
        "free_gb": round(usage.free / (1024**3), 2),
        "used_pct": round((usage.used / usage.total) * 100, 2)
    }

def uptime():
    seconds = float(subprocess.check_output(
        ["sysctl", "-n", "kern.boottime"]
    ).decode().split("sec =")[1].split(",")[0].strip())
    now = time.time()
    return round((now - seconds) / 3600, 2)

def generate_report():
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu = cpu_load()
    mem = memory_info()
    disk = disk_usage("/")
    up = uptime()

    report = f"""
SYSTEM HEALTH REPORT
====================
Generated: {report_time}

CPU Load:
  1 min : {cpu['1min']}
  5 min : {cpu['5min']}
  15 min: {cpu['15min']}

Memory:
  Total     : {mem['total_gb']} GB
  Available : {mem['available_gb']} GB

Disk (/):
  Total : {disk['total_gb']} GB
  Used  : {disk['used_gb']} GB ({disk['used_pct']}%)
  Free  : {disk['free_gb']} GB

System uptime:
  {up} hours
"""
    return report

def main():
    report = generate_report()
    print(report)

    os.makedirs("reports", exist_ok=True)
    filename = f"reports/health_{int(time.time())}.txt"
    with open(filename, "w") as f:
        f.write(report)

    print(f"Report saved to {filename}")

if __name__ == "__main__":
    main()

