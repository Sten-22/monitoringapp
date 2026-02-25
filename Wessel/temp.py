import subprocess                                           # Start andere programma's
import time
from datetime import datetime, timedelta                    # Tijd berekeningen
from pathlib import Path                                    # File path

def ps_logon():
    OUTPUT_FILE = Path(r"C:\001. Documenten\Persoonlijke bestanden\HBO Cybersecurity & Cloud\05. Opdrachten\Programmeren\Groepsopdracht app\failed_logons_per_minute.txt")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    INTERVAL_SECONDS = 60

    while True:
        # Tijdvenster: afgelopen minuut
        now = datetime.now()
        since = (now - timedelta(seconds=INTERVAL_SECONDS)).strftime("%m/%d/%Y %H:%M:%S")
        now_str = now.strftime("%Y-%m-%d %H:%M")

        # PowerShell: TEL aantal 4625 events (geen tekst!)
        ps_command = (
            f'(Get-EventLog -LogName Security -After "{since}" | '
            f'Where-Object {{ $_.EventID -eq 4625 }} | '
            f'Measure-Object).Count')

        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
            capture_output=True,
            text=True)

        # Aantal events (fallback = 0)
        try:
            count = int(result.stdout.strip())
        except ValueError:
            count = 0

        # Schrijf: tijdstip + count
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"{now_str} {count}\n")

        print(f"{now_str} -> {count} failed logons")

        time.sleep(INTERVAL_SECONDS)

ps_logon()
