import serial
import numpy as np
from math import cos, sin, radians, pi

print("Enter name of file to write to: ")
filename = input()
f = open(f'{filename}.txt',"w+")

ArduinoSerial = serial.Serial('COM6', 115200)

def format(f): #int->float
    return "%.0f" %f

def readSerial():
    data = ArduinoSerial.readline().decode('utf-8')  # read line and decode
    data = data.strip()  # remove any surrounding whitespace, including \r\n
    numeric_part = ''.join(filter(str.isdigit, data))  # extract only numeric characters
    return int(numeric_part) if numeric_part else 0  # safely convert to int, default to 0 if empty


def write_to_file():
    print("scanning...")
    while (readSerial != "--End of Scan--"):
        motor1 = int(readSerial())
        motor2 = int(readSerial()) #임의의 어떤 값일텐데...
        distance = int(readSerial())

        if (distance > 1): #이상치 제거

            x = ((distance*cos(radians(motor1))*cos(radians(motor2))))
            y = ((distance*cos(radians(motor1))*sin(radians(motor2))))
            z = ((distance*sin(radians(motor1))))

            x = format(x)
            y = format(y)
            z = format(z)

            f.write(str(x))
            f.write(",")
            f.write(str(y))
            f.write(",")
            f.write(str(z))
            f.write("\n")

write_to_file()
