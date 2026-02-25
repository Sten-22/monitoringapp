import psutil
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import style
import pandas as pd
import time
from datetime import datetime
import json
import requests

# URL van Libre Hardware Monitor
url = "http://192.168.65.253:8085/data.json"

# grafiek styling
style.use("fivethirtyeight")

# data variabelen
x_cpu = []
y_cpu = []
x_temp = []
y_temp = []
start_time = time.time()

# matplotlib figure
fig, (ax_cpu, ax_logons, ax_temp) = plt.subplots(3, 1, figsize=(12, 8))
fig.suptitle("System Monitoring Dashboard")

# refereren naar log bestanden
log_file = open("cpu_log.txt", "a")
temp_logfile = "hardware_log.txt"

# CPU functies
def log_cpu():
    cpu = psutil.cpu_percent(interval=None)
    t = time.time() - start_time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | CPU usage: {cpu}%\n"
    log_file.write(line)
    log_file.flush()
    print(line.strip())

    x_cpu.append(t)
    y_cpu.append(cpu)

def update_cpu_graph():
    ax_cpu.clear()
    # CPU plot kleuren
    for i in range(1, len(x_cpu)):
        if y_cpu[i] <= 5:
            color = "green"
        elif 5 < y_cpu[i] <= 10:
            color = "yellow"
        elif 10 < y_cpu[i] <= 30:
            color = "orange"
        else:
            color = "red"
        ax_cpu.plot(x_cpu[i-1:i+1], y_cpu[i-1:i+1], color=color)

    ax_cpu.set_xlabel("Time (seconds)")
    ax_cpu.set_ylabel("CPU Usage (%)")
    ax_cpu.set_title("Live CPU Usage Monitor")

    # CPU plot legenda
    legend_colors = [
        ('green', '≤5% CPU'),
        ('yellow', '5–10% CPU'),
        ('orange', '10–30% CPU'),
        ('red', '>30% CPU')
    ]
    dummy_lines = [plt.Line2D([0], [0], color=c, lw=2) for c, _ in legend_colors]
    ax_cpu.legend(dummy_lines, [label for _, label in legend_colors])

# security functie
def update_login_graph():
    ax_logons.clear()
    try:
        data = pd.read_csv("powershell_output.txt", header=None, names=["index","logons"])
        ax_logons.plot(data["index"], data["logons"], label="Nieuwe foutieve logons")
        ax_logons.set_xlabel("Seconden")
        ax_logons.set_ylabel("Aantal nieuwe logons")
        ax_logons.set_title("Nieuwe foutieve loginpogingen")
        ax_logons.legend()
    except:
        ax_logons.set_title("Wachten op powershell_output.txt...")

# CPU temp functie
def find_temp(node):
    if "Children" in node:
        for child in node["Children"]:
            result = find_temp(child)
            if result is not None:
                return result
    if node.get("Text") == "Core Max":
        return float(node["Value"].replace(" °C", "").replace(",", "."))
    return None

def update_temp_graph():
    global x_temp, y_temp
    try:
        response = requests.get(url, timeout=2)
        response_data = response.json()
        temperature = find_temp(response_data)
        if temperature is not None:
            log_entry = {"time": datetime.now().strftime("%H:%M:%S"), "temperature": temperature}

            # logfile uitlezen
            try:
                with open(temp_logfile, "r") as f:
                    log_temp = json.load(f)
            except:
                log_temp = []

            # nieuwe meting toevoegen
            log_temp.append(log_entry)

            # terugschrijven naar logfile
            with open(temp_logfile, "w") as f:
                json.dump(log_temp, f, indent=4)

        # cpu temp grafiek data ophalen
        try:
            with open(temp_logfile, "r") as f:
                log_temp = json.load(f)

            x_temp = list(range(len(log_temp)))
            y_temp = [entry["temperature"] for entry in log_temp]

            ax_temp.clear()
            ax_temp.plot(x_temp, y_temp)
            ax_temp.set_xlabel("Tijd in seconde")
            ax_temp.set_ylabel("Temperatuur (°C)")
            ax_temp.set_title("CPU Temperatuur")
        except Exception as e:
            print("Fout bij het lezen van logfile:", e)

    except Exception as e:
        print("Fout bij het ophalen van data:", e)

# animatie functie
def animate(frame):
    log_cpu()
    update_cpu_graph()
    update_login_graph()
    update_temp_graph()
    fig.tight_layout()

# animatie
ani = FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)

plt.show()