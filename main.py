import time
import serial
from math import cos, sin, pi

ArduinoSerial = serial.Serial('COM6', 115200)


print("Enter name of file to write to: ")
filename = input()
f = open(f'{filename}.txt',"w+")

def format(f): 
    return "%.0f" %f

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
            print(f"pos1: {motor1}, pos2: {motor2}, distance: {distance}")

def get_angle():
    user_input = input("Enter 4 numbers (e.g., 30 45 90 0): ")

# 입력값 유효성 검사
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

def write_to_file():
    global motor1, motor2, distance
    print("scanning...")
    while (True):
        read_serial_data()

        if (distance > 5):

            motor1 = change_rad(motor1) # step -> angle(') -> rad
            motor2 = change_rad(motor2)

            x = (distance*sin(motor1)*cos(motor2))
            y = (distance*sin(motor1)*sin(motor2))
            z = ((distance*cos(motor1)))
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

def read_serial():
    if ArduinoSerial.in_waiting > 0:
        data = ArduinoSerial.readline().decode().strip()
        return data
    return None

def main():
    get_angle()
    write_to_file()

if __name__ == "__main__":
    main()