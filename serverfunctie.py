from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread

def receive_memory_load(memory_load):  # Functie die het memory percentage van de client ontvangt
    LOGFILE = "memory_load.log"        # Variabele die bepaalt waar de log weggeschreven wordt
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


    with open(LOGFILE, "a") as f:           # Opent het logbestand in schrijfmodus
        f.write(f"{new_x},{logline}\n")     # Voor de komma komt een opeenvolgend nummer. Na de komma komt de opgehaalde waarde
    return True          # Geeft terug of het scrhijven is gelukt
                         # De volgende 3 functies gebruiken dezelfde logica. Refereer dus naar de comments hierboven om te begrijpen hoe het werkt.
def receive_failed_logins(count):    
    LOGFILE = "failed_logins.log"
    logline = f"{count}"

    # Schrijf de memory naar het log bestand
    try:
        # Read the last line to get the last X value
        with open("failed_logins.log", "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                last_x = int(last_line.split(",")[0])
            else:
                last_x = 0
    except FileNotFoundError:
        last_x = 0  # File does not exist yet
    
    new_x = last_x + 1

    with open(LOGFILE, "a") as f:
        f.write(f"{new_x},{logline}\n")

    return True

def receive_cpu_temp(cpu_temp):
    LOGFILE = "cpu_temperatures.log"
    logline = f"{cpu_temp}"

    #schrijf de memory naar het log bestand
    try:
        # Read the last line to get the last X value
        with open("cpu_temperatures.log", "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                last_x = int(last_line.split(",")[0])
            else:
                last_x = 0
    except FileNotFoundError:
        last_x = 0  # File does not exist yet
    
    new_x = last_x + 1

    with open(LOGFILE, "a") as f:
        f.write(f"{new_x},{logline}\n")

    return True

def receive_cpu_load(cpu_load):
    LOGFILE = "cpu_load.log"
    logline = f"{cpu_load}"

    #schrijf de memory naar het log bestand
    try:
        # Read the last line to get the last X value
        with open("cpu_load.log", "r") as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                last_x = int(last_line.split(",")[0])
            else:
                last_x = 0
    except FileNotFoundError:
        last_x = 0  # File does not exist yet
    
    new_x = last_x + 1

    with open(LOGFILE, "a") as f:
        f.write(f"{new_x},{logline}\n")

    return True

def start_server(host="localhost", port=8000):        # Functie om de XML-RPC server te starten

    server = SimpleXMLRPCServer((host, port))         # Slaat de gegevens van de server op als de variabele server
    server.register_function(receive_memory_load, "receive_memory_load")    # Deze lijnen zorgen ervoor dat de XML-RPC client de functies uit dit bestand kunnen aanroepen
    server.register_function(receive_failed_logins, "receive_failed_logins")
    server.register_function(receive_cpu_temp, "receive_cpu_temp")
    server.register_function(receive_cpu_load, "receive_cpu_load")
    print(f"Server listening on port {port}")     # Print met welke poort de client moet verbinden

    t = Thread(target=server.serve_forever, daemon=True)    # Runt de server in een aparte thread. Dit moet gedaan worden anders stopt het main bestand bij deze functie en kunnen de grafieken niet gemaakt worden
    t.start()     # start de XML-RPC server