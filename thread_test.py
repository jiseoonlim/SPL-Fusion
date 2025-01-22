import time
import serial
from math import cos, sin, pi
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

ArduinoSerial = serial.Serial('COM6', 115200)

def format(f):
    return "%.0f" % f

def parse_data(line):
    global tilt, pan, distance
    distance = -1
    try:
        # 데이터를 파싱합니다.
        parts = line.split(',')
        tilt = int(parts[1].strip())
        pan = int(parts[2].strip())
        distance = int(parts[3].strip())
        return tilt, pan, distance
    except (IndexError, ValueError):
        return None

def get_angle():
    user_input = input("Enter 4 numbers (e.g., 30 45 90 0): ")

    if not user_input.strip():
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
    step = angle * 4096 / 360
    return step

def change_rad(step):
    rad = step * (2 * pi) / 4096
    return rad

def update_plot(frame, x_vals, y_vals, z_vals, line):
    global tilt, pan, distance
    line = ArduinoSerial.readline().decode('utf-8', errors='ignore')
    line = line.strip()
    
    if line.startswith("s,") and line.endswith(", e"):
        data = parse_data(line)
        if data:
            tilt, pan, distance = data
    
    if distance > 5:
        tilt = change_rad(tilt)  # 스텝 -> 각도(') -> 라디안으로 변환
        pan = change_rad(pan)

        # 3D 좌표 계산
        x = (distance * sin(tilt) * cos(pan))
        y = (distance * sin(tilt) * sin(pan))
        z = (distance * cos(tilt))

        # 새로운 좌표를 데이터 리스트에 추가
        x_vals.append(format(x))
        y_vals.append(format(y))
        z_vals.append(format(z))

        # 3D plot 업데이트
        line.set_data(x_vals, y_vals)  # 2D 데이터 업데이트 (x, y)
        line.set_3d_properties(z_vals)  # 3D Z 데이터 업데이트
        
    return line,

# 실시간 시각화 함수 설정
def start_plot():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    x_vals = []  # X, Y, Z 좌표 리스트 초기화
    y_vals = []
    z_vals = []

    # 선 그래프 초기화
    line, = ax.plot([], [], [], 'r-')

    # 축 레이블 설정
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Real-time 3D Data Visualization')

    # FuncAnimation에서 업데이트 함수 호출
    ani = FuncAnimation(fig, update_plot, fargs=(x_vals, y_vals, z_vals, line), interval=100, blit=False)

    # 플로팅 표시
    plt.show()

start_plot()
