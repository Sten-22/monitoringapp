import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

def plot_realtime_example(file_path='example.txt'):
    #Plots the last 10 points from a CSV-style text file in real time
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    def animate(i):
        try:
            with open(file_path, 'r') as f:
                graph_data = f.read()
        except FileNotFoundError:
            return  # skip if file doesn't exist yet

        lines = graph_data.split('\n')
        xs, ys = [], []
        for line in lines:
            if len(line) > 1:
                x, y = line.split(',')
                xs.append(float(x))
                ys.append(float(y))

        ax1.clear()
        ax1.plot(xs[-10:], ys[-10:])  # last 10 points

    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()

