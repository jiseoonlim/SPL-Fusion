import time
import serial
from math import cos, sin, pi
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

ArduinoSerial = serial.Serial('COM6', 115200)

print("Enter name of file to write to: ")
filename = input()
f = open(f'{filename}.txt', "w+")

# 기본 형식으로 출력
def format(f):
    return "%.0f" % f

# 데이터 파싱 함수
def parse_data(line):
    global motor1, motor2, distance
    distance = -1
    try:
        # 데이터를 파싱합니다.
        parts = line.split(',')
        motor1 = int(parts[1].strip())
        motor2 = int(parts[2].strip())
        distance = int(parts[3].strip())
        return motor1, motor2, distance
    except (IndexError, ValueError):
        # 오류가 발생한 경우 None을 반환합니다.
        return None

# 시리얼 데이터를 읽는 함수
def read_serial_data():
    line = ArduinoSerial.readline().decode('utf-8', errors='ignore')
    line = line.strip()

    if line.startswith("s,") and line.endswith(", e"):
        data = parse_data(line)
        if data:
            motor1, motor2, distance = data
            print(f"pos1: {motor1}, pos2: {motor2}, distance: {distance}")

# 사용자 각도 입력 처리
def get_angle():
    user_input = input("Enter 4 numbers (e.g., 30 45 90 0): ")

    if not user_input.strip():  # 입력 값이 비어 있으면
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

# 각도를 스텝으로 변환하는 함수
def change_step(angle):
    step = angle * 4096 / 360
    return step

# 스텝을 라디안으로 변환하는 함수
def change_rad(step):
    rad = step * (2 * pi) / 4096
    return rad

# 실시간 시각화 함수
def update_plot(frame, x_vals, y_vals, z_vals, line):
    global motor1, motor2, distance
    read_serial_data()

    if distance > 5:
        motor1 = change_rad(motor1)  # 스텝 -> 각도(') -> 라디안으로 변환
        motor2 = change_rad(motor2)

        # 3D 좌표 계산
        x = (distance * sin(motor1) * cos(motor2))
        y = (distance * sin(motor1) * sin(motor2))
        z = (distance * cos(motor1))

        # 출력 형식 변환
        x = format(x)
        y = format(y)
        z = format(z)

        # 3D 좌표 리스트에 추가
        x_vals.append(x)
        y_vals.append(y)
        z_vals.append(z)

        # 좌표 값 시각화 업데이트
        line.set_data(x_vals, y_vals)
        line.set_3d_properties(z_vals)

        # 파일에 3D 좌표 기록
        f.write(f"{x},{y},{z}\n")
        f.flush()

    return line,

# 실시간 시각화 함수 설정
def start_plot():
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # 3D 좌표 초기화
    x_vals = []
    y_vals = []
    z_vals = []

    # 선 그래프 초기화
    line, = ax.plot([], [], [], 'r-')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Real-time 3D Data Visualization')

    ani = FuncAnimation(fig, update_plot, fargs=(x_vals, y_vals, z_vals, line), interval=100, blit=False)
    plt.show()

# 시리얼에서 데이터 읽기
def read_serial():
    if ArduinoSerial.in_waiting > 0:
        data = ArduinoSerial.readline().decode().strip()
        return data
    return None

# 메인 함수
def main():
    get_angle()
    start_plot()

if __name__ == "__main__":
    main()
