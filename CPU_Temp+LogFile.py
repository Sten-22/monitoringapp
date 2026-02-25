import requests
import matplotlib.pyplot as plt
import time
import json
from datetime import datetime

# URL van Libre Hardware Monitor
url = "http://192.168.48.1:8085/data.json"

# Logbestand
logfile = "hardware_log.txt"

x_data = []
y_data = []

plt.ion()
fig, ax = plt.subplots()

#functie om temp te zoeken
def find_temp(node):

    #Als er children zijn verder zoeken
    if "Children" in node:
        for child in node["Children"]:
            result = find_temp(child)
            if result is not None:
                return result

    #Controle op juiste sensor
    if node.get("Text") == "Core (Tctl/Tdie)":
        return float(node["Value"].replace(" °C", "").replace(",", "."))

    return None

while True:
    try:

        #Data ophalen

        response = requests.get(url)
        data = response.json()

        temperature = find_temp(data)

        if temperature is not None:
            log_entry = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "temperature": temperature
            }


            #Logfile uitlezen

            try:
                with open(logfile, "r") as f:
                    log_data = json.load(f)
            except:
                log_data = []

            # Nieuwe meting toevoegen
            log_data.append(log_entry)

            # Terugschrijven naar logfile
            with open(logfile, "w") as f:
                json.dump(log_data, f, indent=4)

        #Logfile uitlezen voor grafiek
        try:
            with open(logfile, "r") as f:
                log_data = json.load(f)

            x_data = []
            y_data = []

            for i, entry in enumerate(log_data):
                x_data.append(i)
                y_data.append(entry["temperature"])

            ax.clear()
            ax.plot(x_data, y_data)
            ax.set_xlabel("Metingen")
            ax.set_ylabel("Temperatuur (°C)")
            ax.set_title("CPU Temperatuur Over Tijd")

            plt.pause(1)

        except Exception as e:
            print("Fout bij het lezen van logfile:", e)

    except Exception as e:
        print("Fout bij het ophalen van data:", e)

    time.sleep(1)