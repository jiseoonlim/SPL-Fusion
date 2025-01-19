import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import time
import serial
from math import cos, sin, pi

# 시리얼 포트 설정
ArduinoSerial = serial.Serial('COM6', 115200)

def parse_data(line):
    try:
        parts = line.split(',')
        motor1 = int(parts[1].strip())
        motor2 = int(parts[2].strip())
        distance = int(parts[3].strip())
        return motor1, motor2, distance
    except (IndexError, ValueError):
        return None

def read_serial_data():
    line = ArduinoSerial.readline().decode('utf-8', errors='ignore').strip()
    if line.startswith("s,") and line.endswith(", e"):
        return parse_data(line)
    return None

def change_rad(step):
    return step * (2 * pi) / 4096  # Step -> Radian 변환

# 초기 설정
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
x_data, y_data, z_data = [], [], []  # 누적 데이터 저장

def update_graph(motor1, motor2, distance):
    if distance > 5:
        rad_motor1 = change_rad(motor1)
        rad_motor2 = change_rad(motor2)

        # 변환된 좌표 계산
        x = distance * sin(rad_motor1) * cos(rad_motor2)
        y = distance * sin(rad_motor1) * sin(rad_motor2)
        z = distance * cos(rad_motor1)

        # 데이터 누적
        x_data.append(x)
        y_data.append(y)
        z_data.append(z)

        # 그래프 업데이트
        ax.clear()
        ax.scatter(x_data, y_data, z_data, c='blue', marker='o')
        ax.set_title("Real-time 3D Visualization")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        plt.pause(0.1)

try:
    while True:
        data = read_serial_data()
        if data:
            motor1, motor2, distance = data
            print(f"pos1: {motor1}, pos2: {motor2}, distance: {distance}")
            update_graph(motor1, motor2, distance)
        time.sleep(0.1)  # 데이터 읽기 주기 조정
except KeyboardInterrupt:
    print("프로그램 종료")
    ArduinoSerial.close()
    plt.close()
