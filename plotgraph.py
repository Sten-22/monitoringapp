
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

style.use('fivethirtyeight')

def plot_graphs(memory_file='memory_load.log', security_file='failed_logins.log',cpu_temp_file="cpu_temperatures.log",cpu_load_file="cpu_load.log"):
    fig, axes = plt.subplots(2, 2)  # 2 rows, 2 column
    ax1, ax2, ax3, ax4 = axes.flatten()
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

        # cpu temperature graph
        try:
            with open(cpu_temp_file, 'r') as f:
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

        ax3.clear()
        ax3.plot(xs[-10:], ys[-10:])
        ax3.set_title("CPU Temperature")

        # cpu load graph
        try:
            with open(cpu_load_file, 'r') as f:
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

        ax4.clear()
        ax4.plot(xs[-10:], ys[-10:])
        ax4.set_title("CPU Load")

    ani = animation.FuncAnimation(fig, animate, interval=1000, cache_frame_data=False)

    plt.tight_layout()
    plt.show()
