import xmlrpc.client
import psutil
import time
import subprocess
from datetime import datetime, timedelta
import socket

INTERVAL_SECONDS = 60

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

    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", ps_command],
        capture_output=True,
        text=True
    )

    try:
        return int(result.stdout.strip())
    except:
        return 0

while True:
    #verbind met de sevrer
    proxy = xmlrpc.client.ServerProxy("http://localhost:8000")
    #haal het percentage van gerbuikte geheugen op
    mem = psutil.virtual_memory()
    #stuur memory percentage naar de server
    proxy.print_memory(mem.percent)

    count = get_failed_logins()
    hostname = socket.gethostname()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    proxy.receive_failed_logins(hostname, count, timestamp)
    



    #wacht 1 seconde en stuur opnieuw
    time.sleep(1)
