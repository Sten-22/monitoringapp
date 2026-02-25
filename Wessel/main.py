import time
import subprocess
from datetime import datetime

def run_powershell_command() -> str:
    # telt mislukte logins (Event ID 4625) in de afgelopen 60 minuten.
    minutes_back = 60
    powershell_script = f"""
    $minutes = {minutes_back}
    $start = (Get-Date).AddMinutes(-$minutes)
    $events = Get-WinEvent -FilterHashtable @{{LogName='Security'; Id=4625; StartTime=$start}} -ErrorAction SilentlyContinue
    ($events | Measure-Object).Count
    """

    # Voer PowerShell uit
    result = subprocess.run(["powershell", "-NoProfile", "-Command", powershell_script],capture_output=True,text=True)
    # Registeerd output
    output_text = (result.stdout or "").strip()
    # Bij geen nieuwe events = 0
    if output_text == "":
        output_text = "0"

    return output_text

def append_to_text_file(file_path: str, index_number: int, new_events: int) -> None:
    line = f"{index_number},{new_events}\n"

    # "a" = append (steeds een nieuwe regel onderaan)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(line)

def main() -> None:
    # Bestand waar je alles in opslaat
    output_file = "powershell_output.txt"
    # Hoe vaak uitvoeren (in seconden)
    interval_seconds = 1
    # Dit nummer loopt op
    index_number = 0
    # We onthouden de vorige totale telling, zodat we "nieuwe events" kunnen bepalen
    previous_total = None

    print(f"Interval: {interval_seconds} seconden")

    while True:
        # PowerShell uitvoeren
        output = run_powershell_command()

        # Van de output een getal te maken (totaal aantal events)
        try:
            current_total = int(output)
        except ValueError:
            # 0 events bij geen logons
            current_total = 0

        # Bereken hoeveel NIEUWE events erbij zijn gekomen sinds vorige meting
        if previous_total is None:
            new_events = 0
        else:
            new_events = current_total - previous_total
            # Voorkom negatieve waardes (kan gebeuren als telling "reset" lijkt)
            if new_events < 0:
                new_events = 0

        # Update "previous_total" voor de volgende ronde
        previous_total = current_total
        # Verhoog index en schrijf precies "index,new_events"
        index_number += 1
        append_to_text_file(output_file, index_number, new_events)
        # Ook even in de console tonen (handig voor testen)
        print(f"{index_number},{new_events}")
        # Wachten tot de volgende ronde
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()