import matplotlib
matplotlib.use("Agg")

from flask import Flask, Response
import matplotlib.pyplot as plt
import io
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
memory_file = os.path.join(BASE_DIR, "memory_load.log")
security_file = os.path.join(BASE_DIR, "failed_logins.log")
cpu_temp_file = os.path.join(BASE_DIR, "cpu_temperatures.log")
cpu_load_file = os.path.join(BASE_DIR, "cpu_load.log")


def read_log(file):
    xs, ys = [], []

    try:
        with open(file, "r") as f:
            lines = f.read().split("\n")
    except FileNotFoundError:
        return xs, ys

    for line in lines:
        if "," in line:
            try:
                x, y = line.split(",")
                xs.append(float(x))
                ys.append(float(y))
            except ValueError:
                pass

    return xs[-10:], ys[-10:]


def generate_dashboard():

    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    ax1, ax2, ax3, ax4 = axes.flatten()

    xs, ys = read_log(memory_file)
    ax1.plot(xs, ys)
    ax1.set_title("Memory Usage")

    xs, ys = read_log(security_file)
    ax2.plot(xs, ys)
    ax2.set_title("Failed Logins")

    xs, ys = read_log(cpu_temp_file)
    ax3.plot(xs, ys)
    ax3.set_title("CPU Temperature")

    xs, ys = read_log(cpu_load_file)
    ax4.plot(xs, ys)
    ax4.set_title("CPU Load")

    plt.tight_layout()

    img = io.BytesIO()
    fig.savefig(img, format="png")
    plt.close(fig)
    img.seek(0)

    return img


@app.route("/dashboard.png")
def dashboard():
    img = generate_dashboard()
    return Response(img.getvalue(), mimetype="image/png")


@app.route("/")
def index():
    return """
    <html>
    <body>
    <h2>System Monitoring Dashboard</h2>
    <img id="dash" src="/dashboard.png" width="900">

    <script>
    setInterval(function(){
        document.getElementById("dash").src = "/dashboard.png?t=" + new Date().getTime();
    }, 1000);
    </script>

    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)