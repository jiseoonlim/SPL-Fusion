import time
import serial
from math import cos, sin, pi

ArduinoSerial = serial.Serial('COM6', 115200)


print("Enter name of file to write to: ")
filename = input()
f = open(f'test.txt',"w+")

def format(f): 
    return "%.0f" %f

def send_signal():
    print("Enter start signal : ")
    signal = input()
    ArduinoSerial.write(signal.encode())
    print(f"Sent signal: {signal}")
    time.sleep(1)
    
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
    line = ArduinoSerial.readline().decode('utf-8', errors='ignore')
    line = line.strip()

    if line.startswith("s,") and line.endswith(", e"):
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

def change_step(angle):
    step = angle * 4096/360 
    return step

def change_rad(step):
    rad = step * (2*pi)/4096 
    return rad

def write_to_file():
    global tilt, pan, distance
    print("scanning...")
    while (True):
        read_serial_data()

        if (distance > 5):

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
    get_angle()
    write_to_file()

if __name__ == "__main__":
    main()