import serial
import time
import numpy as np

list_height = []
# list_weight = []
list_temperature = []

def getSensorData():
    conn_0 = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=0.5)
    conn_0.write(b"1")  # write a string
    # time.sleep(1)
    # conn_1 = serial.Serial("/dev/ttyUSB1", baudrate=115200, timeout=0.5)
    # conn_1.write(b"1")  # write a string
    
    has_value = False
    count = 0

    while True:
        conn_0_msg = conn_0.read(64)
        conn_0_msg_decoded = conn_0_msg.decode("utf-8").replace('\r\n', '')
        print('{}.'.format(conn_0_msg_decoded))

        # conn_1_msg = conn_1.read(64)
        # conn_1_msg_decoded = conn_1_msg.decode("utf-8").replace('\r\n', '')
        # print('{}.'.format(conn_1_msg_decoded))
        # print(data[1])
        # print(data[2])

        count += 1
        if count == 10:
            conn_0.write(b"0")  # write a string
            # time.sleep(1)
            # conn_1.write(b"0")  # write a string
            break

    return 1


print(getSensorData())
