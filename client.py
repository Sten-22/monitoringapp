import xmlrpc.client
import psutil
import time
import subprocess
from datetime import datetime, timedelta
from threading import Thread
from PyLibreHardwareMonitor import Computer


INTERVAL_SECONDS = 60
SERVER_URL = "http://localhost:8000"

# Initialize hardware monitor once
computer = Computer()
cpu_name = list(computer.cpu.keys())[0]

def get_memory_load():
    try:
        return psutil.virtual_memory().percent
    except:
        return 0

def get_failed_logins():
    now = datetime.now()
    since = (now - timedelta(seconds=INTERVAL_SECONDS)).strftime("%Y-%m-%dT%H:%M:%S")
    ps_command = f"""
    $filter = @{{
        LogName='Security'
        Id=4625
        StartTime='{since}'
    }}
    (Get-WinEvent -FilterHashtable $filter | Measure-Object).Count
    """
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps_command],
            capture_output=True,
            text=True
        )
        return int(result.stdout.strip())
    except:
        return 0

def get_cpu_temp():
    try:
        return round(computer.cpu[cpu_name]["Temperature"]["Core Average"], 1)
    except:
        return 0

def get_cpu_load():
    try:
        return round(psutil.cpu_percent(interval=1), 1)
    except:
        return 0

# Thread-safe sending functions (each thread gets its own proxy)
def send_memory_load(value):
    try:
        proxy = xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)
        proxy.receive_memory_load(value)
    except:
        pass

def send_failed_logins(value):
    try:
        proxy = xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)
        proxy.receive_failed_logins(value)
    except:
        pass

def send_cpu_temp(value):
    try:
        proxy = xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)
        proxy.receive_cpu_temp(value)
    except:
        pass

def send_cpu_load(value):
    try:
        proxy = xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)
        proxy.receive_cpu_load(value)
    except:
        pass

def send_async(func, value):
    Thread(target=func, args=(value,), daemon=True).start()

# Main loop
try:
    while True:
        mem = get_memory_load()
        failed = get_failed_logins()
        temp = get_cpu_temp()
        load = get_cpu_load()

        # Send all metrics concurrently
        send_async(send_memory_load, mem)
        send_async(send_failed_logins, failed)
        send_async(send_cpu_temp, temp)
        send_async(send_cpu_load, load)

        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")

