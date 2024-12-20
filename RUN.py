import time
import serial
import numpy as np
from math import cos, sin, radians, pi

print("Enter name of file to write to: ")
filename = input()
f = open(f'{filename}.txt',"w+")

ArduinoSerial = serial.Serial('COM6', 115200)

def format(f): 
    return "%.0f" %f

def readSerial():
    read = ArduinoSerial.readline().decode('utf-8') 

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


def change_angle(step):
    angle = step * (2*pi)/4096 #1 바퀴에 4096 steps
    return angle


def write_to_file():
    global motor1, motor2, distance
    print("scanning...")
    while (True):
        read_serial_data()

        if (distance > 5):

            motor1 = change_angle(motor1) # step -> angle(') -> rad
            motor2 = change_angle(motor2)

            x = (distance*sin(motor1)*sin(motor2))
            y = (distance*sin(motor1)*cos(motor2))
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



send_signal()
write_to_file()
#read_serial_data()
