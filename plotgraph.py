
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

def plot_graphs(memory_file='example.txt', security_file='failed_logins.log'):
    fig, (ax1, ax2) = plt.subplots(2, 1)  # 2 rows, 1 column

    def animate(i):
        # memory graph
        try:
            with open(memory_file, 'r') as f:
                lines = f.read().split('\n')
        except FileNotFoundError:
            lines = []

        xs, ys = [], []
        for line in lines:
            if ',' in line:
                try:
                    x, y = line.split(',')
                    xs.append(float(x))
                    ys.append(float(y))
                except ValueError:
                    pass

        ax1.clear()
        ax1.plot(xs[-10:], ys[-10:])
        ax1.set_title("Memory Usage")

        # security graph
        try:
            with open(security_file, 'r') as f:
                lines = f.read().split('\n')
        except FileNotFoundError:
            lines = []

        xs, ys = [], []
        for line in lines:
            if ',' in line:
                try:
                    x, y = line.split(',')
                    xs.append(float(x))
                    ys.append(float(y))
                except ValueError:
                    pass

        ax2.clear()
        ax2.plot(xs[-10:], ys[-10:])
        ax2.set_title("Failed Logins")

    ani = animation.FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)

    plt.tight_layout()
    plt.show()
