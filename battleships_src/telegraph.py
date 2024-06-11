import serial
import time


BAUDRATES = [
    2400,
    4800, 
    9600, 
    19200, 
    38400, 
    57600, 
    115200
]

class SerialCommunicator:
    def __init__(self, port, baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # wait for the serial connection to initialize

    def send(self, message):
        self.ser.write((message + '\n').encode())

    def receive(self):
        if self.ser.in_waiting > 0:
            return self.ser.readline().decode().strip()
        return None

    def close(self):
        self.ser.close()

# Example usage:
if __name__ == "__main__":
    communicator = SerialCommunicator('/dev/ttyUSB0')
    communicator.send("Hello, Arduino!")
    while True:
        response = communicator.receive()
        if response:
            print("Received from Arduino:", response)