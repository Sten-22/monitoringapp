import matplotlib.pyplot as plt
from serverfunctie import start_server
from plotgraph import app

def main():
    #start_web_server()
    start_server()



if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=5000)
