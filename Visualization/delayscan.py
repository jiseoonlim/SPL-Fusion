import time
from math import cos, sin, pi
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
from data_utils import *
from serial_utils import *

# Initialize data lists
x_data = []
y_data = []
z_data = []

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.set_xlim(-100, 100)
ax.set_ylim(-100, 100)
ax.set_zlim(0, 200)

scatter = ax.scatter([], [], [])

def parse_data(line):
    global tilt, pan, distance
    distance = -1
    try:
        # parsing each data
        parts = line.split(',')
        tilt = int(parts[1].strip())
        pan = int(parts[2].strip())
        distance = int(parts[3].strip())
        return tilt, pan, distance
    except (IndexError, ValueError):
        # if some data has an error return None
        return None

def read_serial_data():
    global tilt, pan, distance
    line = ArduinoSerial.readline().decode('utf-8', errors='ignore')
    line = line.strip()

    if line.startswith("s, ") and line.endswith(", e"):
        data = parse_data(line)
        if data:
            tilt, pan, distance = data

def write_angle():
    default_numbers = [60, 120, 60, 120]
    numbers = [str(int(num * 4096 / 360)) for num in default_numbers]
    message = " ".join(numbers)
    ArduinoSerial.write((message + "\n").encode())
    print(f"Sent default: {message}")

def collect_data():
    global tilt, pan, distance
    while len(x_data) < 500:
        read_serial_data()

        if distance > -1:
            tilt = change_rad(tilt)  # Convert step to angle (degrees) -> rad
            pan = change_rad(pan)

            x = (distance * sin(tilt) * cos(pan))
            y = (distance * sin(tilt) * sin(pan))
            z = (distance * cos(tilt))

            # Add data to lists for plotting
            x_data.append(format(x))
            y_data.append(format(y))
            z_data.append(format(z))

            # Print for debugging
            print(f"x: {format(x)}, y: {format(y)}, z: {format(z)}")

            time.sleep(0.1)  # Adjust the sleep time as needed

def update(frame):
    # Update the scatter plot with the data up to the current frame
    scatter._offsets3d = (x_data[-100:], y_data[-100:], z_data[-100:])
    return scatter,

def main():
    write_angle()

    data_thread = threading.Thread(target=collect_data, daemon=False)
    data_thread.start()
 
    print("Scanning........")

    # Animation setup
    global ani
    ani = FuncAnimation(fig, update, frames=100, interval=100, blit=True)
    plt.show()

if __name__ == "__main__":
    main()
