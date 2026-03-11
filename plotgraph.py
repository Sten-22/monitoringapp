import matplotlib  
matplotlib.use("Agg") # voorkomt dat er geen GUI nodig is zodat deze foutmelding verholpen is: RuntimeError: main thread is not in main loop
import threading
from flask import Flask, Response #ter behoeve van de webserver
import matplotlib.pyplot as plt  
import io
import os
import configparser

config = configparser.ConfigParser()             #
config.read("config.ini")

memorylog = config["logging"]["memorylog"]          # Haalt de naam van het memorylog uit het ini bestand
securitylog = config["logging"]["securitylog"]
cputemplog = config["logging"]["cputemplog"]
cpuloadlog = config["logging"]["cpuloadlog"]

app = Flask(__name__)        # maakt een object voor de webserver aan

BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # Stelt de huide directory in als working directory zodat de log bestanden goed uitgelezen worden
memory_file = os.path.join(BASE_DIR, memorylog)       # Zorgt ervoor dat de variabelenen gekoppeld zijn aan de juiste locatie van de logbestanden
security_file = os.path.join(BASE_DIR, securitylog)
cpu_temp_file = os.path.join(BASE_DIR, cputemplog)
cpu_load_file = os.path.join(BASE_DIR, cpuloadlog)         

memory_buffer = []
security_buffer = []
temp_buffer = []
load_buffer = []

MAX_POINTS = 60


def read_last_value(file):
    try:
        with open(file, "r") as f:
            last = f.readlines()[-1]
            parts = last.split(",")
            return float(parts[1])
    except:
        return None

def generate_dashboard():                #functie om de grafieken te maken
    global memory_buffer, security_buffer, temp_buffer, load_buffer

    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    ax1, ax2, ax3, ax4 = axes.flatten()

    MAX_POINTS = 60

    def update_buffer(buf, value):
        if value is not None:
            buf.append(value)
        if len(buf) > MAX_POINTS:
            buf.pop(0)

    # read newest values from logs
    mem = read_last_value(memory_file)
    sec = read_last_value(security_file)
    tmp = read_last_value(cpu_temp_file)
    lod = read_last_value(cpu_load_file)

    # update buffers
    update_buffer(memory_buffer, mem)
    update_buffer(security_buffer, sec)
    update_buffer(temp_buffer, tmp)
    update_buffer(load_buffer, lod)

    # x-axis for last 60 refreshes
    x_mem = list(range(len(memory_buffer)))
    x_sec = list(range(len(security_buffer)))
    x_tmp = list(range(len(temp_buffer)))
    x_lod = list(range(len(load_buffer)))

    # memory usage
    ax1.plot(x_mem, memory_buffer)
    ax1.set_xlim(0, 60)
    ax1.set_title("Memory Usage")

    # failed logins
    ax2.plot(x_sec, security_buffer)
    ax2.set_xlim(0, 60)
    ax2.set_title("Failed Logins")

    # cpu temperature
    ax3.plot(x_tmp, temp_buffer)
    ax3.set_xlim(0, 60)
    ax3.set_title("CPU Temperature")

    # cpu load
    ax4.plot(x_lod, load_buffer)
    ax4.set_xlim(0, 60)
    ax4.set_title("CPU Load")

    plt.tight_layout()

    img = io.BytesIO()
    fig.savefig(img, format="png")
    plt.close(fig)
    img.seek(0)

    return img

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
