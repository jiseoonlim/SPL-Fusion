import time
from math import cos, sin, pi
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from data_utils import *
from serial_utils import *

# Initialize data lists
x_data = []
y_data = []
z_data = []

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.set_xlim(0, 200)
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
            print(f"pos1: {tilt}, pos2: {pan}, distance: {distance}")


def write_angle():
    user_input = input("Enter 4 numbers (e.g., 30 45 90 0): ")

    if not user_input.strip():  # input value empty
        default_numbers = [60, 120, 60, 120]
        numbers = [str(int(num * 4096 / 360)) for num in default_numbers]
        message = " ".join(numbers)
        ArduinoSerial.write((message + "\n").encode())
        print(f"Sent default: {message}")
    else:
        numbers = user_input.split()
        if len(numbers) == 4 and all(num.isdigit() for num in numbers):
            numbers = [str(int(int(num) * 4096 / 360)) for num in numbers]
            message = " ".join(numbers)
            ArduinoSerial.write((message + "\n").encode())
            print(f"Sent: {message}")
        else:
            print("Invalid input. Please enter exactly 4 numbers separated by space.")

def write_to_file(f):
    global tilt, pan, distance
    read_serial_data()
    while distance > 5:  # Add a condition to stop the loop after a certain distance
        read_serial_data()

        if distance > 5:
            tilt = change_rad(tilt)  # Convert step to angle (degrees) -> rad
            pan = change_rad(pan)

            x = (distance * sin(tilt) * cos(pan))
            y = (distance * sin(tilt) * sin(pan))
            z = (distance * cos(tilt))

            # Add data to lists for plotting
            x_data.append(x)
            y_data.append(y)
            z_data.append(z)

            print(x_data)

            # Write data to file
            f.write(f"{x}, {y}, {z}\n")
            f.flush()
            time.sleep(0.05)

def main():
    filename = input("Enter name of file to write to: ")
    f = open(f'{filename}.txt', "w+")

    write_angle()
    print("Scanning........")
    write_to_file(f)  # Pass file object to write_to_file

    # Animation setup after data is collected
    ani = FuncAnimation(fig, update, frames=500, interval=2000, blit=True)
    plt.show()  # Show the plot after animation setup and data collection

def update(frame):
    # Update the scatter plot with the data up to the current frame
    scatter._offsets3d = (x_data[:frame], y_data[:frame], z_data[:frame])  # z values are the actual data
    print(x_data)
    return scatter,

if __name__ == "__main__":
    main()
