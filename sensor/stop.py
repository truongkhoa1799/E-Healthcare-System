import time
import serial
conn_0 = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=1)
conn_0.write(b"0")  # write a string
time.sleep(1)
conn_1 = serial.Serial("/dev/ttyUSB1", baudrate=115200, timeout=0.5)
conn_1.write(b"0")  # write a string
