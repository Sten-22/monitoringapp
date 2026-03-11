import matplotlib.pyplot as plt
from serverfunctie import start_server
from plotgraph import app
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

xml_rpc_port = config.getint("network", "port")

def main():
    #start_web_server()
    start_server()



if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=xml_rpc_port)
