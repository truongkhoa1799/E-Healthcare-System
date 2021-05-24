import serial
import time
import numpy as np

list_height = []
# list_weight = []
list_temperature = []

def getSensorData():
    try:
        conn_0 = serial.Serial("/dev/ttyUSB0", baudrate=115200, timeout=0.5)
        conn_0.write(b"1")  # write a string
        time.sleep(1)
        conn_1 = serial.Serial("/dev/ttyUSB1", baudrate=115200, timeout=0.5)
        conn_1.write(b"1")  # write a string
    except:
        pass
    
    has_value = False
    count = 0

    while True:
        conn_0_msg = conn_0.read(64)
        try:
            conn_0_msg_decoded = conn_0_msg.decode("utf-8").replace('\r\n', '')
            list_values = conn_0_msg_decoded.split("/")
            if len(list_values) == 4:
                print('height: {}.'.format( round(2.64 - float(list_values[1]), 2) ))
                print('\ttemp: {}.'.format(float(list_values[2]) + 1.5))

            conn_1_msg = conn_1.read(64)
            conn_1_msg_decoded = conn_1_msg.decode("utf-8").replace('\r\n', '')
            list_values = conn_1_msg_decoded.split("/")
            # print('{}.'.format(conn_1_msg_decoded))
            if len(list_values) == 3:
                print('\t\tweight: {}.'.format(list_values[1]))
            
            count += 1
            if count == 200:
                conn_0.write(b"0")  # write a string
                time.sleep(1)
                conn_1.write(b"0")  # write a string
                break
        except Exception as e:
            # print(e)
            pass

    return 1


print(getSensorData())
