import serial
import threading

def read_from_arduino(ser):
    while True:
        line = ser.readline().decode('utf-8').rstrip()
        print(f"Arduino: {line}")

# Initialize serial connection with Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
threading.Thread(target=read_from_arduino, args=(ser,)).start()

# Example: Send a command to the Arduino
ser.write(b'Your command\n')