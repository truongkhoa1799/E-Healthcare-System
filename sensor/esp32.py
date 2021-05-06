import serial
import time
import numpy as np

list_height = []
# list_weight = []
list_temperature = []

def getSensorData():
    conn = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=0.1)
    conn.write(b"1")  # write a string
    has_value = False
    count = 0

    while True:
        esp_message = conn.read(64)
        esp_message_decoded = esp_message.decode("utf-8").replace('\r\n', '')
        print(esp_message)

        count += 1
        if count == 10:

            conn.write(b"1")  # write a string
            break

    return 1


print(getSensorData())
