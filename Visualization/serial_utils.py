import serial

ArduinoSerial = serial.Serial('COM6', 115200)

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