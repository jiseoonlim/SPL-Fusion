import time
import serial
from math import cos, sin, pi

ArduinoSerial = serial.Serial('COM6', 115200)

print("Enter name of file to write to: ")
filename = input()
f = open(f'{filename}.txt', "w+")

# Initialize global variables
tilt = 0
pan = 0
real_tilt = 0
real_pan = 0

def parse_data(line):
    global tilt, pan, real_tilt, real_pan
    try:
        # parsing each data
        parts = line.split(',')
        tilt = int(parts[1].strip())
        pan = int(parts[2].strip())
        real_tilt = int(parts[3].strip())
        real_pan = int(parts[4].strip())

        return tilt, pan, real_tilt, real_pan
    except (IndexError, ValueError):
        # if some data has an error return None
        return None

def read_serial_data():
    global tilt, pan, real_tilt, real_pan
    line = ArduinoSerial.readline().decode('utf-8', errors='ignore')
    line = line.strip()

    if line.startswith("s,") and line.endswith(", e"):
        data = parse_data(line)
        if data:
            tilt, pan, real_tilt, real_pan = data
            print(f"tilt: {tilt}, pan: {pan}, real_tilt: {real_tilt}, real_pan: {real_pan}")

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

def write_to_file():
    global tilt, pan, real_tilt, real_pan
    print("scanning...")
    while True:
        read_serial_data()

        f.write(f"tilt : {tilt}, ")
        f.write(f"real_tilt ; {real_tilt}, ")
        f.write(f"pan : {pan}, ")
        f.write(f"real_pan : {real_pan}\n")
        f.flush()
        #print(f"Saved: {tilt}, {real_tilt}, {pan}, {real_pan}")

def main():
    get_angle()
    write_to_file()

if __name__ == "__main__":
    main()
