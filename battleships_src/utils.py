#   
#   Battleships Game: Extra Utilities.
#   Contains extra utilities, such as a port locator for serial communication on any OS.
#   By: aldrick-t (github.com/aldrick-t)
#   Version: June 2024 (v0.3.0) python3.11.2
#   

import sys
import glob

import serial

def locate_ports() -> list[str]:
    if sys.platform.startswith('win'): # Computadora windows
        platform = 'win'
        ports =[f'COM{i}' for i in range(1, 256)]
    elif sys.platform.startswith('linux'): # Computadora Linux
        platform = 'linux'
        ports =glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'): # Mac
        platform = 'darwin'
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported Platform')
    result = []
    for port in ports:
        early_stop = True if platform == 'win' else False
        try:
            s= serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            if early_stop:
                break
            continue

    return result