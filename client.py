import xmlrpc.client
import psutil
import time
import subprocess
from datetime import datetime, timedelta
from threading import Thread
from PyLibreHardwareMonitor import Computer


INTERVAL_SECONDS = 60                 # Deze variabele bepaalt hoeveel seconden terug in de security log wordt gekeken voor failed logins
SERVER_URL = "http://localhost:8000"  # Variabele voor het adres van de XML-RPC server

computer = Computer()                    # Maakt een object aan voor computer d.m.v pylibrehardwaremonitor. Hiermee kan de temperatuur uitgelezen worden
cpu_name = list(computer.cpu.keys())[0]  # Maakt een list aan met alle cpu's en pakt de eerste entry(index 0). deze wordt opgeslagen als cpu_name

def get_memory_load():                  # Functie voor het ophalen van het gebruikte memory percentage
    try:
        return psutil.virtual_memory().percent      # Geeft het memory percentage terug met psutil
    except:
        return 0                            # als dat niet lukt geef 0 terug zodat het programma blijft draaien

def get_failed_logins():              # functie voor het registreren van gefaalde login logins
    now = datetime.now()              # Slaat de huidige datum en tijd op 
    since = (now - timedelta(seconds=INTERVAL_SECONDS)).strftime("%Y-%m-%dT%H:%M:%S")   # Haalt 60 seconden van de huidige tijd af en converteert dit naar een string die bruikbaar is in powershell
    ps_command = f"""
    $filter = @{{
        LogName='Security'
        Id=4625
        StartTime='{since}'
    }}
    (Get-WinEvent -FilterHashtable $filter | Measure-Object).Count
    """
    # bovenstaande code slaat een powershell commando op die van de afgelopen 60 seconden (interval seconds) de gefaalde logins ophaalt
    try:         
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps_command],      # start powershell en voert het commando uit dat hierboven is opgeslagen
            capture_output=True,        # Slaat de output op in het result.stdout object
            text=True                   # Slaat de output op als een string
        )
        return int(result.stdout.strip())    # Converteert de output naar een int zodat dit in de grafiek gebruikt kan worden en returnt die waarde
    except:
        return 0        # als dat niet lukt geef 0 terug zodat het programma blijft draaien

def get_cpu_temp():             # Functie voor het ophalen van de cpu temperatuur
    try:
        return round(computer.cpu[cpu_name]["Temperature"]["Core Average"], 1)   # Maakt gebruik van het eerder aangemaakt computer object en haalt daarvan de gemiddelde temperatuur op van alle cores
    except:
        return 0      # Als dat niet lukt geef 0 terug zodat het programma blijft draaien

def get_cpu_load():
    try:
        return round(psutil.cpu_percent(interval=1), 1)  # Haalt het gemmidelde CPU verbruik op over een periode van 1 seconde afgerond naar een getal achter de komma
    except:
        return 0 # Als dat niet lukt geef 0 terug zodat het programma blijft draaien

# Thread-safe sending functions (each thread gets its own proxy)
def send_memory_load(value):       # Functie om het eerder opgehaalde ram gebruik naar de server te sturen
    try:
        proxy = xmlrpc.client.ServerProxy(SERVER_URL, allow_none=True)      # Maakt een object aan voor de server
        proxy.receive_memory_load(value)     # Roept een functie aan die op de server beschikbaar is gemaakt en stuurt de opgehaalde waarde daarheen
    except:
        pass              # zorgt dat het programma niet crasht als dat niet lukt.
                          # De onderstaande code gebruikt dezelfde logica. refereer naar de comments hierboven om te begrijpen hoe het werkt
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

def send_async(func, value):        # Zorgt dat de bovenstaande functies in hun eigen thread aangeroepen worden zodat deze elkaar niet verhinderen
    Thread(target=func, args=(value,), daemon=True).start()  # De functie die gestart moet wordne en welke value meegegeven moet worden naar de server

# Main loop
try:
    while True:     # Slaat de alle metrics op in variabelen zodat deze doorgestuurd kunnen worden
        mem = get_memory_load()
        failed = get_failed_logins()
        temp = get_cpu_temp()
        load = get_cpu_load()

    # Gebruikt de send_async functie om alle variabelen hierboven tegelijk naar de srver te sturen
        send_async(send_memory_load, mem)
        send_async(send_failed_logins, failed)
        send_async(send_cpu_temp, temp)
        send_async(send_cpu_load, load)

        time.sleep(1)    # Wacht 1 seconde voordat het opnieuw verstuurd wordt
except KeyboardInterrupt:
    print("Shutting down...") # Zorgt ervoor dat errors niet getoond worden bij het afsluiten van de client

