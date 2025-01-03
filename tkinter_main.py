import tkinter as tk
from tkinter import messagebox
import time
import serial
from math import cos, sin, pi

# Arduino Serial Initialization
try:
    ArduinoSerial = serial.Serial('COM6', 115200)
except Exception as e:
    print("Error connecting to Arduino:", e)
    ArduinoSerial = None

# GUI Application
class MotorControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Motor Control GUI")

        # File name input
        tk.Label(root, text="Enter file name:").grid(row=0, column=0, padx=10, pady=10)
        self.file_entry = tk.Entry(root, width=20)
        self.file_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Button(root, text="Set File", command=self.set_file).grid(row=0, column=2, padx=10, pady=10)

        # Angle input
        tk.Label(root, text="Enter Angles (degrees):").grid(row=1, column=0, columnspan=3, pady=10)

        tk.Label(root, text="Angle 1:").grid(row=2, column=0, padx=10, pady=5)
        self.angle1_entry = tk.Entry(root, width=10)
        self.angle1_entry.grid(row=2, column=1, padx=10, pady=5)
        self.angle1_entry.insert(0, "60")

        tk.Label(root, text="Angle 2:").grid(row=3, column=0, padx=10, pady=5)
        self.angle2_entry = tk.Entry(root, width=10)
        self.angle2_entry.grid(row=3, column=1, padx=10, pady=5)
        self.angle2_entry.insert(0, "120")

        tk.Label(root, text="Angle 3:").grid(row=4, column=0, padx=10, pady=5)
        self.angle3_entry = tk.Entry(root, width=10)
        self.angle3_entry.grid(row=4, column=1, padx=10, pady=5)
        self.angle3_entry.insert(0, "60")

        tk.Label(root, text="Angle 4:").grid(row=5, column=0, padx=10, pady=5)
        self.angle4_entry = tk.Entry(root, width=10)
        self.angle4_entry.grid(row=5, column=1, padx=10, pady=5)
        self.angle4_entry.insert(0, "120")

        # Start and Stop Buttons in a single row
        self.button_frame = tk.Frame(root)
        self.button_frame.grid(row=6, column=0, columnspan=3, pady=10)

        tk.Button(self.button_frame, text="Start", bg="green", width=15, command=self.start_process).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Stop", bg="red", width=15, command=self.stop_process).pack(side=tk.RIGHT, padx=5)

        # Status
        self.status_label = tk.Label(root, text="Status: Idle", fg="blue")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=10)

        # Variables
        self.filename = None
        self.running = False  # To control the stop mechanism

    def set_file(self):
        self.filename = self.file_entry.get().strip()
        if self.filename:
            if not self.filename.endswith(".txt"):
                self.filename += ".txt"
            self.status_label.config(text=f"File set: {self.filename}", fg="green")
        else:
            self.status_label.config(text="Please enter a valid file name.", fg="red")

    def start_process(self):
        if not self.filename:
            messagebox.showerror("Error", "Please set a file name first.")
            return
        if not ArduinoSerial:
            messagebox.showerror("Error", "Arduino not connected.")
            return

        self.running = True  # Enable running flag
        # Send angles
        if not self.send_angles():
            self.running = False  # Disable running flag on error
            return

        # Start writing to file
        self.write_to_file()

    def stop_process(self):
        self.running = False
        self.status_label.config(text="Status: Stopped", fg="red")

    def send_angles(self):
        try:
            angles = [
                int(self.angle1_entry.get()),
                int(self.angle2_entry.get()),
                int(self.angle3_entry.get()),
                int(self.angle4_entry.get())
            ]
            if ArduinoSerial:
                steps = [str(int(angle * 4096 / 360)) for angle in angles]
                message = " ".join(steps)
                ArduinoSerial.write((message + "\n").encode())
                self.status_label.config(text=f"Sent Angles: {angles}", fg="green")
                return True
        except ValueError:
            self.status_label.config(text="Invalid angles. Please enter numeric values.", fg="red")
            return False

    def write_to_file(self):
        self.status_label.config(text="Writing to file...", fg="blue")
        try:
            with open(self.filename, "w") as f:
                while self.running:  # Check running flag
                    line = ArduinoSerial.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("s,") and line.endswith(", e"):
                        data = self.parse_data(line)
                        if data:
                            motor1_rad = self.change_rad(data[0])
                            motor2_rad = self.change_rad(data[1])
                            x = self.format(data[2] * sin(motor1_rad) * cos(motor2_rad))
                            y = self.format(data[2] * sin(motor1_rad) * sin(motor2_rad))
                            z = self.format(data[2] * cos(motor1_rad))
                            f.write(f"{x},{y},{z}\n")
                            f.flush()
            if self.running:
                self.status_label.config(text="File writing completed.", fg="green")
            else:
                self.status_label.config(text="Stopped writing to file.", fg="red")
        except Exception as e:
            self.status_label.config(text=f"Error: {e}", fg="red")

    def parse_data(self, line):
        try:
            parts = line.split(',')
            motor1 = int(parts[1].strip())
            motor2 = int(parts[2].strip())
            distance = int(parts[3].strip())
            return motor1, motor2, distance
        except (IndexError, ValueError):
            return None

    def change_rad(self, step):
        return step * (2 * pi) / 4096

    def format(self, f):
        return "%.0f" % f


# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = MotorControlApp(root)
    root.mainloop()
