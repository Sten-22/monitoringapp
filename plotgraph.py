import matplotlib  
matplotlib.use("Agg") # voorkomt dat er geen GUI nodig is zodat deze foutmelding verholpen is: RuntimeError: main thread is not in main loop
import threading
from flask import Flask, Response #Flask voor de webserver
import matplotlib.pyplot as plt  
import io
import os
import configparser

config = configparser.ConfigParser()             
config.read("config.ini")                 # Leest de Config.ini uit zodat de waardes gebruikt kunnen worden

#haalt de namen van de log uit de ini file
memorylog = config["logging"]["memorylog"] 
securitylog = config["logging"]["securitylog"]
cputemplog = config["logging"]["cputemplog"]
cpuloadlog = config["logging"]["cpuloadlog"]

app = Flask(__name__)        #maakt een object voor de webserver aan

BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # Stelt de huide directory in als working directory zodat de log bestanden uitgelezen worden
memory_file = os.path.join(BASE_DIR, memorylog)       # Zorgt ervoor dat de variabelenen gekoppeld zijn aan de juiste locatie van de logbestanden
security_file = os.path.join(BASE_DIR, securitylog)
cpu_temp_file = os.path.join(BASE_DIR, cputemplog)
cpu_load_file = os.path.join(BASE_DIR, cpuloadlog)         

#maakt lege lijsten aan waar de logs in komen
memory_buffer = []          
security_buffer = []
temp_buffer = []
load_buffer = []

MAX_POINTS = 60             # Variabele die het maximum aantal punten in de buffers bepaalt


def read_last_value(file):    # Functie die de waarde van de laatste logline uitleest
    try:
        with open(file, "r") as f:   # Opent het logbestand in leesmodus
            last = f.readlines()[-1]    # Slaat de laatste line op in de variabele last
            parts = last.split(",")     # Split de line op de komma en slaat deze op als list
            return float(parts[1])   # returnt index 1 van de list, dit is de waarde die in de grafiek komt.
    except:
        return None         # als het openen niet lukt returnt niks

def generate_dashboard():                #functie om de grafieken te maken
    global memory_buffer, security_buffer, temp_buffer, load_buffer   # Staat python toe om de globale variabelen aan te passen

    #dashboard layout 2x2 grid
    fig, axes = plt.subplots(2, 2, figsize=(10, 6))    # 2 rijen, 2 kolommen, grootte 10x6 inch
    ax1, ax2, ax3, ax4 = axes.flatten()        # Haal alle assen uit de grid voor eenvoudig gebruik

    MAX_POINTS = 60     # Maximum aantal plot points op de X as. 60 voor de laatste minuut

    def update_buffer(buf, value):    # Functie om de buffer bij te houden zodat de grafiek blijft doorlopen 
        if value is not None:     # Als de waarde die wordt meegegeven iets bevat wordt dit toegevoegd aan een lijst
            buf.append(value)     
        if len(buf) > MAX_POINTS:  # Als de lijst groter wordt dan het maximum aantan punten wordt de eerste waarde eruit gehaald en schuift de rest door
            buf.pop(0)

    #leest de laatste value uit de log en slaat deze op in een variabele
    mem = read_last_value(memory_file)
    sec = read_last_value(security_file)
    tmp = read_last_value(cpu_temp_file)
    lod = read_last_value(cpu_load_file)

    #update de buffers
    update_buffer(memory_buffer, mem)
    update_buffer(security_buffer, sec)
    update_buffer(temp_buffer, tmp)
    update_buffer(load_buffer, lod)

    # Geeft het aantal waardes in de memory buffer terug. Range maakt daar een reeks van en list zet deze reeks om in een lijst. Deze lijsten worden de x waardes van de grafieken
    x_mem = list(range(len(memory_buffer)))  
    x_sec = list(range(len(security_buffer)))
    x_tmp = list(range(len(temp_buffer)))
    x_lod = list(range(len(load_buffer)))

    #memory usage
    ax1.plot(x_mem, memory_buffer)      # Plot de opgehaalde data
    ax1.set_xlim(0, 60)                 # Zet de x as vast op 0 tot 60 (1 minuut)
    ax1.set_title("Memory Usage In %")  # Zet een titel boven de grafiek
    ax1.set_ylim(0, 100)                # Zet de y as vast op 0 tot 100 (Logische waarden voor temperatuur)
    ax1.set_xticklabels([])             # zorgt ervoor dat de x as geen getallen laat zien
    ax1.set_xlabel("Last 60 seconds")   # zet een label bij de x as
                    # de rest van de grafieken volgen dezelfde logica. voor uitleg refereer aan bovenstaande comments
    #failed logins
    ax2.plot(x_sec, security_buffer)
    ax2.set_xlim(0, 60)
    ax2.set_title("Failed Login Counter")
    ax2.set_ylim(0, 5)
    ax2.set_xticklabels([])
    ax2.set_xlabel("Last 60 seconds")

    #cpu temperature
    ax3.plot(x_tmp, temp_buffer)
    ax3.set_xlim(0, 60)
    ax3.set_title("CPU Temperature in °C")
    ax3.set_ylim(0, 100)
    ax3.set_xticklabels([])
    ax3.set_xlabel("Last 60 seconds")

    #cpu load
    ax4.plot(x_lod, load_buffer)
    ax4.set_xlim(0, 60)
    ax4.set_title("CPU Usage In %")
    ax4.set_ylim(0, 100)
    ax4.set_xticklabels([])
    ax4.set_xlabel("Last 60 seconds")

    plt.tight_layout()          # Zorgt dat de titels en labels elkaar niet overlappen
 
    img = io.BytesIO()
    fig.savefig(img, format="png")           # Sla de figuur op in het geheuhen als PNG
    plt.close(fig)                          # Sluit hem weer om geheugen vrij te maken
    img.seek(0)       # Zet de pointer terug naar het begin van de afbeelding. Als deze lijn ontbreekt blijven de grafieken leeg

    return img       # Returnt de png voor gebruik in de webserver

@app.route("/dashboard.png")
def dashboard():
    img = generate_dashboard()
    return Response(img.getvalue(), mimetype="image/png")

#HTLM van de webserver
@app.route("/")         # Hoofdpagina van de webserver
def index():            # Voer deze functie uit als iemand de hoofdpagina bezoekt
                      # Returnt de volgende HTML code
    return """            
    <html>
    <body>
    <h2>System Monitoring Dashboard</h2>
    <img id="dash" src="/dashboard.png" width="900">

    <script>
    setInterval(function(){
        document.getElementById("dash").src = "/dashboard.png?t=" + new Date().getTime();
    }, 1000);
    </script>

    </body>
    </html>
    """
#def start_web_server():              # Functie om de webserver te starten
#    thread = threading.Thread(       #
#        target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
 #   )
#    thread.daemon = True
#    thread.start()
#    return thread


