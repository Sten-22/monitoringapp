import requests
import matplotlib.pyplot as plt
import time

url = "http://localhost:8085/data.json"

x_data = [] 
y_data = []

plt.ion()
fig, ax = plt.subplots()

while True:
    try:
        response = requests.get(url)
        data = response.json()

        temperature = None

        def find_temp(node):
            if "Children" in node:
                for child in node["Children"]:
                    find_temp(child)
            if node.get("Text") == "Core (Tctl/Tdie)":
                global temperature
                temperature = float(node["Value"].replace("°C", "").replace(",", "."))

        find_temp(data)

        if temperature is not None:
            x_data.append(len(x_data))
            y_data.append(temperature)

            ax.clear()
            ax.plot(x_data, y_data)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Temperature (°C)")

            plt.pause(1)

    except Exception as e:
        print("Fout bij het ophalen van gegevens:", e)

    time.sleep(1)
