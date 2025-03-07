import time
import serial
from math import cos, sin, pi
import sys
import signal


ArduinoSerial = serial.Serial('/dev/ttyACM0', 115200)

# # Mock Serial class when there's no connection to Arduino
# class MockSerial:
#     def write(self, message):
#         print(f"Sending to Arduino: {message.decode().strip()}")
    
#     def readline(self):
#         return b"s, 90, 90, 10, e\n"  # Mocked response
    
#     def close(self):
#         print("MockSerial closed.")

# try:
#     ArduinoSerial = serial.Serial('/dev/ttyACM0', 115200)
# except serial.SerialException:
#     print("Serial port not found, using mock serial.")
#     ArduinoSerial = MockSerial()

# print("Enter name of file to write to: ")
# filename = input()
f = open(f'plane.txt',"w+")

def format(f): 
    return "%.0f" %f

def change_rad(step):
    rad = step * (2*pi)/4096 
    return rad

# tilt_start, tilt_fin, pan_start, pan_finish, tilt_gap, pan_gap 총 6개의 값을 입력받음. 입력하지 않을 경우 default 값으로 계산
def get_data():
    input_angle = input("Enter angles (default 60, 100, 60, 100): ")

    if not input_angle.strip():  # input value empty
        angles = [60, 100, 60, 100]
    else:
        angles = input_angle.split()
        if len(angles) == 4 and all(num.isdigit() for num in angles):
            angles = [int(int(num) * 4096 / 360) for num in angles] # 각도를 step 값으로 변경
        else:
            print("Invalid input. Please enter exactly 4 numbers separated by space.")
    print(angles)
    input_gap = input("Enter tilt gap, pan gap (default 16, 16): ")

    if not input_gap.strip():  # input value empty
        gaps = [16, 16]
    else:
        gaps = input_gap.split()
        if len(gaps) == 2 and all(num.isdigit() for num in gaps):
            gaps = [int(num) for num in gaps] # step 값을 기준으로 입력받아 별도의 변환 과정 없음
        else:
            print("Invalid input. Please enter exactly 2 numbers separated by space.")
    print(gaps)

    return angles + gaps

def send_data():
    list = get_data()
    tilt_start = list[0]
    tilt_fin = list[1]
    pan_start = list[2]
    pan_fin = list[3]
    tilt_gap = list[4]
    pan_gap = list[5]

    tilt_pos = tilt_start
    pan_pos = pan_start    

    start_pos = [tilt_start, pan_start]
    message = " ".join(map(str, start_pos))
    print("Send start position to Arduino --------------------------")
    ArduinoSerial.write(("start " + message + "\n").encode())
    print(repr("start " + message + "\n")) # 데이터 송신 확인
    time.sleep(3)
        
    for i in range ((tilt_fin-tilt_start) // tilt_gap):
        tilt_pos += tilt_gap
        if pan_pos >= pan_start:
            for j in range ((pan_fin-pan_start) // pan_gap):
                pan_pos += pan_gap
                pos = [tilt_pos, pan_pos]
                message = " ".join(map(str, pos))
                ArduinoSerial.write(("pos " + message + "\n").encode())
        else:
            for j in range ((pan_fin-pan_start) // pan_gap):
                pan_pos -= pan_gap
                pos = [tilt_pos, pan_pos]
                message = " ".join(map(str, pos))
                ArduinoSerial.write(("pos " + message + "\n").encode())

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

# Ctrl+C를 눌렀을 때의 종료 처리 함수
def handle_exit(signal, frame):
    print("\n아두이노에 초기화 명령을 전송")
    ArduinoSerial.write(b'reset\n')  # 아두이노로 "reset" 명령 전송
    time.sleep(1)  # 잠시 대기
    ArduinoSerial.close()  # 시리얼 포트 닫기
    sys.exit(0)  # 프로그램 종료

signal.signal(signal.SIGINT, handle_exit)

def write_to_file():
    global tilt, pan, distance
    print("scanning...")
    while (True):
        read_serial_data()

        if (distance > 1):

            tilt = change_rad(tilt) # step -> angle(') -> rad
            pan = change_rad(pan)

            x = (distance*sin(tilt)*cos(pan))
            y = (distance*sin(tilt)*sin(pan))
            z = ((distance*cos(tilt)))
            # print(f"변환pos1: {x}, pos2: {y}, distance: {z}")
            
            x = format(x)
            y = format(y)
            z = format(z)

            f.write(str(x))
            f.write(",")
            f.write(str(y))
            f.write(",")
            f.write(str(z))
            f.write("\n")
            f.flush()


def main():
    send_data()
    write_to_file()

if __name__ == "__main__":
    main()
