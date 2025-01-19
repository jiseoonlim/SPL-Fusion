import matplotlib
matplotlib.use('TkAgg')  # TkAgg 백엔드 사용

import time
import serial
from math import cos, sin, pi
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# interactive mode off
plt.ioff()

ArduinoSerial = serial.Serial('COM6', 115200)
x_data, y_data, z_data = [], [], []

fig = plt.figure()                                  
ax = fig.add_subplot(111, projection='3d')


def send_signal():
    print("Enter start signal : ")
    signal = input()
    ArduinoSerial.write(signal.encode())
    print(f"Sent signal: {signal}")
    time.sleep(1)
    
def parse_data(line):
    global motor1, motor2, distance
    distance = -1
    try:
        # parsing each data
        parts = line.split(',')
        motor1 = int(parts[1].strip())
        motor2 = int(parts[2].strip())
        distance = int(parts[3].strip())
        return motor1, motor2, distance
    except (IndexError, ValueError):
        # if some data has an error return None
        return None

def read_serial_data():
    line = ArduinoSerial.readline().decode('utf-8', errors='ignore')
    line = line.strip()

    if line.startswith("s,") and line.endswith(", e"):
        data = parse_data(line)
        if data:
            motor1, motor2, distance = data
            # print(f"pos1: {motor1}, pos2: {motor2}, distance: {distance}")

def get_angle():
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

def change_step(angle):
    step = angle * 4096/360 
    return step

def change_rad(step):
    rad = step * (2*pi)/4096 
    return rad

def calculate_position(motor1, motor2, distance):
    motor1 = change_rad(motor1)  # step -> angle(') -> rad
    motor2 = change_rad(motor2)

    x = (distance * sin(motor1) * cos(motor2))
    y = (distance * sin(motor1) * sin(motor2))
    z = (distance * cos(motor1))

    return x, y, z

def update_graph():
    # 그래프 초기화 및 갱신
    ax.clear()
    ax.scatter(x_data, y_data, z_data, c='blue', marker='o')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Real-time 3D Visualization')

def update(frame):
    global motor1, motor2, distance
    global x_data, y_data, z_data
    print("scanning...")

    while True:
        read_serial_data()

        if distance > 5:
            # Calculate position
            x, y, z = calculate_position(motor1, motor2, distance)

            # Store data
            x_data.append(x)
            y_data.append(y)
            z_data.append(z)

            # Update graph
            update_graph()

def read_serial():
    if ArduinoSerial.in_waiting > 0:
        data = ArduinoSerial.readline().decode().strip()
        return data
    return None

def main():
    get_angle()
    ani = FuncAnimation(fig, update, interval=100, cache_frame_data=False)
    plt.show(block=True)

if __name__ == "__main__":
    main()
