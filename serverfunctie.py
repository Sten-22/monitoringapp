from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread
import configparser
import os

config = configparser.ConfigParser()             #
config.read("config.ini")

xml_rpc_port = config["network"]["xml_rpc_port"]  
xml_rpc_host = config["network"]["host"]  

memorylog = config["logging"]["memorylog"]          # Haalt de naam van het memorylog uit het ini bestand
securitylog = config["logging"]["securitylog"]
cputemplog = config["logging"]["cputemplog"]
cpuloadlog = config["logging"]["cpuloadlog"]


max_log_size = 1000000     # Staat gelijk aan 1 mb
max_backup_files = 3   

def rotate_log(logfile):
    if not os.path.exists(logfile):  # Als bestand niet bestaat: niks doen
        return
    
    if os.path.getsize(logfile) < max_log_size: # Als bestand niet te groot is: doet niks
        return
    
    oldest = f"{logfile}.{max_backup_files}"    # Verwijderd oudste bestand
    if os.path.exists(oldest):
        os.remove(oldest)

    for i in range(max_backup_files - 1, 0, -1):    # Schuift benaming van de bestanden op
        src = f"{logfile}.{i}"
        dst = f"{logfile}.{i+1}"
        if os.path.exists(src):
            os.rename(src, dst)
        
        os.rename(logfile, f"{logfile}.1")  # Hernoem huidige log naar .1

def receive_memory_load(memory_load):  # Functie die het memory percentage van de client ontvangt
    LOGFILE = memorylog        # Variabele die bepaalt waar de log weggeschreven wordt
    logline = f"{memory_load}"         # variabele die bepaalt wat er wordt weggeschreven op een nieuwe line van een log
    try:
        with open(LOGFILE, "r") as f:  # Opent het logbestand in de leesmodus
            lines = f.readlines()      # Opent alle regels en slaat ze op in een lijst
            if lines:               # Voer uit als het bestand niet leeg is
                last_line = lines[-1].strip()    # Pakt het laatste object uit de lijst(Laatste regel) en haalt de newline tekens weg met strip()
                last_x = int(last_line.split(",")[0])   # Pakt de laatste regel uit de lijst, split de lijn op een komma en pakt de waarde die voor de komma staat
            else:
                last_x = 0     # Voer uit als het bestand leeg is. Zet waarde van x op 0 zodat de volgende waarde 1 wordt
    except FileNotFoundError:
        last_x = 0  # Voer uit als het bestand niet bestaat. Zet waarde van x op 0 zodat de volgende waarde 1 wordt
    
    new_x = last_x + 1   # Zorgt dat de volgende lijn de volgende opvolgt met stappen van 1 er tussen.

    rotate_log(LOGFILE)

    with open(LOGFILE, "a") as f:           # Opent het logbestand in schrijfmodus
        f.write(f"{new_x},{logline}\n")     # Voor de komma komt een opeenvolgend nummer. Na de komma komt de opgehaalde waarde
    return True          # Geeft terug of het scrhijven is gelukt
                         # De volgende 3 functies gebruiken dezelfde logica. Refereer dus naar de comments hierboven om te begrijpen hoe het werkt.

def receive_failed_logins(count):    
    LOGFILE = securitylog           # Variabele die bepaalt waar de log weggeschreven wordt
    logline = f"{count}"            # variabele die bepaalt wat er wordt weggeschreven op een nieuwe line van een log

    
    try:                                # Schrijf de memory naar het log bestand
        with open(LOGFILE, "r") as f:   # Opent logfile in read mode
            lines = f.readlines()       # Leest alle regels van het bestand
            if lines:
                last_line = lines[-1].strip()           # Leest laatste regel en stript en haalt de newlines weg
                last_x = int(last_line.split(",")[0])   # Pakt de laatste regel uit de lijst, split de lijn op een komma en pakt de waarde die voor de komma staat      
            else:
                last_x = 0              # Bestand zonder regels: begint hij op 0
    except FileNotFoundError:
        last_x = 0                      # Als het bestand nog niet bestaat, bijv. als het de eerste keer is dat hij draait
    
    new_x = last_x + 1                  # Zorgt voor een oplopende teller, voor de grafiek om uit te lezen

    rotate_log(LOGFILE)

    with open(LOGFILE, "a") as f:       # Opent logfile bestand in 'append mode'. Nieuwe data wordt onderaan toegevoegd, niet overschreven
        f.write(f"{new_x},{logline}\n") # Schrijft een nieuwe regel met een x as nummer en login count

    return True                         # Actie geslaagd

def receive_cpu_temp(cpu_temp):
    LOGFILE = cputemplog                # Variabele die bepaalt waar de log weggeschreven wordt
    logline = f"{cpu_temp}"             # variabele die bepaalt wat er wordt weggeschreven op een nieuwe line van een log

    #schrijf de memory naar het log bestand
    try:
        with open(LOGFILE, "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()           # Pakt het laatste object uit de lijst(Laatste regel) en haalt de newline tekens weg met strip()
                last_x = int(last_line.split(",")[0])   # Pakt de laatste regel uit de lijst, split de lijn op een komma en pakt de waarde die voor de komma staat
            else:
                last_x = 0                              # Voer uit als het bestand leeg is. Zet waarde van x op 0 zodat de volgende waarde 1 wordt
    except FileNotFoundError:
        last_x = 0          # Voer uit als het bestand niet bestaat. Zet waarde van x op 0 zodat de volgende waarde 1 wordt
    
    new_x = last_x + 1      # Zorgt dat de volgende lijn de volgende opvolgt met stappen van 1 er tussen.

    rotate_log(LOGFILE)

    with open(LOGFILE, "a") as f:           # Opent het logbestand in schrijfmodus
        f.write(f"{new_x},{logline}\n")     # Voor de komma komt een opeenvolgend nummer. Na de komma komt de opgehaalde waarde

    return True

def receive_cpu_load(cpu_load):
    LOGFILE = cpuloadlog                # Variabele die bepaalt waar de log weggeschreven wordt
    logline = f"{cpu_load}"             # variabele die bepaalt wat er wordt weggeschreven op een nieuwe line van een log

    #schrijf de memory naar het log bestand
    try:
        # Read the last line to get the last X value
        with open(LOGFILE, "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()               # Pakt het laatste object uit de lijst(Laatste regel) en haalt de newline tekens weg met strip()
                last_x = int(last_line.split(",")[0])       # Pakt de laatste regel uit de lijst, split de lijn op een komma en pakt de waarde die voor de komma staat
            else:
                last_x = 0         # Voer uit als het bestand leeg is. Zet waarde van x op 0 zodat de volgende waarde 1 wordt
    except FileNotFoundError:
        last_x = 0                 # Voer uit als het bestand niet bestaat. Zet waarde van x op 0 zodat de volgende waarde 1 wordt
    
    new_x = last_x + 1                      # Zorgt dat de volgende lijn de volgende opvolgt met stappen van 1 er tussen.

    rotate_log(LOGFILE)

    with open(LOGFILE, "a") as f:           # Opent het logbestand in schrijfmodus
        f.write(f"{new_x},{logline}\n")     # Voor de komma komt een opeenvolgend nummer. Na de komma komt de opgehaalde waarde

    return True

def start_server(host=xml_rpc_host, port=xml_rpc_port):        # Functie om de XML-RPC server te starten

    server = SimpleXMLRPCServer((host, port))         # Slaat de gegevens van de server op als de variabele server
    server.register_function(receive_memory_load, "receive_memory_load")    # Deze lijnen zorgen ervoor dat de XML-RPC client de functies uit dit bestand kunnen aanroepen
    server.register_function(receive_failed_logins, "receive_failed_logins")
    server.register_function(receive_cpu_temp, "receive_cpu_temp")
    server.register_function(receive_cpu_load, "receive_cpu_load")
    print(f"Server listening on port {port}")     # Print met welke poort de client moet verbinden

    t = Thread(target=server.serve_forever, daemon=True)    # Runt de server in een aparte thread. Dit moet gedaan worden anders stopt het main bestand bij deze functie en kunnen de grafieken niet gemaakt worden
    t.start()     # start de XML-RPC server