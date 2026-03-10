import matplotlib  
matplotlib.use("Agg") # voorkomt dat er geen GUI nodig is zodat deze foutmelding verholpen is: RuntimeError: main thread is not in main loop
import threading
from flask import Flask, Response #ter behoeve van de webserver
import matplotlib.pyplot as plt  
import io
import os

app = Flask(__name__)        # maakt een object voor de webserver aan

BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # Stelt de huide directory in als working directory zodat de log bestanden goed uitgelezen worden
memory_file = os.path.join(BASE_DIR, "memory_load.log")       # Zorgt ervoor dat de variabelenen gekoppeld zijn aan de juiste locatie van de logbestanden
security_file = os.path.join(BASE_DIR, "failed_logins.log")
cpu_temp_file = os.path.join(BASE_DIR, "cpu_temperatures.log")
cpu_load_file = os.path.join(BASE_DIR, "cpu_load.log")               


def read_log(file):           # Functie om de logbestanden uit te lezen
    xs, ys = [], []           # Lijsten voor x- en y-waarden initialiseren

    try:
        with open(file, "r") as f:        # Probeer het bestand te openen in leesmodus
            lines = f.read().split("\n")  # Lees alle regels en split op newline
    except FileNotFoundError:            
        return xs, ys                     # Als het bestand niet bestaat geef de lege lijst terug
 
    for line in lines:                   # Loop door elke regel in het bestand
        if "," in line:                  
            try:
                x, y = line.split(",")     # Split de regel in x en y, gebruik "," aks scheidingsteken
                xs.append(float(x))        # Voeg x toe als float
                ys.append(float(y))        # Voeg y toe als float
            except ValueError:
                pass                      # Sla deze regel over als het toeveogen/omzetten niet lukt.

    return xs[-10:], ys[-10:]            # Zorgt dat de gtafiek niet groter wordt dan de laatste 10 waarden


def generate_dashboard():                #functie om de grafieken te maken

    fig, axes = plt.subplots(2, 2, figsize=(10, 6))        # 2 rijen, 2 kolommen, grootte 10x6 inch
    ax1, ax2, ax3, ax4 = axes.flatten()                 # Haal alle assen uit de grid voor eenvoudig gebruik

    # Grafiek memory usage
    xs, ys = read_log(memory_file)                     # Roept de bovenstaande functie aan en loopt deze door met de memory file
    ax1.plot(xs, ys)                                   # Plot de data
    ax1.set_title("Memory Usage")                      # Titel voor de grafiek
                                                       # voor onderstaande grafieken is de logica hetzelfde refereen aan bovenstaande comments voor uitleg
    # Grafiek failed logins
    xs, ys = read_log(security_file)
    ax2.plot(xs, ys)
    ax2.set_title("Failed Logins")

    # Grafiek CPU temperature
    xs, ys = read_log(cpu_temp_file)
    ax3.plot(xs, ys)
    ax3.set_title("CPU Temperature")

    # Grafiek CPU temperature 
    xs, ys = read_log(cpu_load_file)
    ax4.plot(xs, ys)
    ax4.set_title("CPU Load")

    plt.tight_layout()                                 # Zorgt dat de titels en labels elkaar niet overlappen

    
    img = io.BytesIO()             
    fig.savefig(img, format="png")                   # Sla de figuur op in het geheuhen als PNG
    plt.close(fig)                                   # Sluit hem weer om geheugen vrij te maken
    img.seek(0)                                      # Zet de pointer terug naar het begin van de afbeelding. Als deze lijn ontbreekt blijven de grafieken leeg

    return img                                       # Returnt de png voor gebruik in de webserver


@app.route("/dashboard.png")
def dashboard():
    img = generate_dashboard()
    return Response(img.getvalue(), mimetype="image/png")


@app.route("/")      # Hoofdpagina van de webserver
def index():         # Voer deze functie uit als iemand de hoofdpagina bezoekt
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
def start_web_server():
    thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    )
    thread.daemon = True
    thread.start()
    return thread

if __name__ == "__main__":                
    app.run(host="0.0.0.0", port=5000)          # Runt de webserver lokaal op poort 5000
