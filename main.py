import matplotlib.pyplot as plt
from serverfunctie import start_server
from plotgraph import app
import configparser

config = configparser.ConfigParser()        # Zet de varibale voor het config bestand
config.read("config.ini")                   # Leest alle instellingen uit dit bestand

xml_rpc_port = config.getint("network", "port")     # Leest de netwerk en poort instellingen, als integer door 'getint'

def main():     # Start het hele feestje
    #start_web_server()
    start_server()



if __name__ == "__main__":  # Start dit script alleen als dit bestand zelf gestart wordt, dus main bestand is
    main()
    app.run(host="0.0.0.0", port=xml_rpc_port)      # Start webserver op alle netwerkinterfaces. En gebruikt de instellingen uit het config bestand
