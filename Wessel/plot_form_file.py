import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import style
import pandas as pd

style.use("fivethirtyeight")


def animate(i):
    try:
        data = pd.read_csv("powershell_output.txt",header=None,names=["index", "logons"])

        x = data["index"]
        y = data["logons"]

        plt.cla()
        plt.plot(x, y, label="Nieuwe foutieve logons")

        plt.xlabel("seconden")
        plt.ylabel("Aantal nieuwe logons")
        plt.title("Nieuwe foutieve loginpogingen")
        plt.tight_layout()

ani = FuncAnimation(plt.gcf(), animate, interval=1000)

plt.show()
