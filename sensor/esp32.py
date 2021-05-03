import serial
import time
import numpy as np

list_height = []
list_weight = []
list_temperature = []

def getSensorData():
    conn = serial.Serial("/dev/tty.usbserial-0001", baudrate=115200, timeout=1)
    conn.write(b"1")  # write a string
    has_value = False
    count = 0

    while has_value == False:
        try:
            d = conn.read(64)
            data_decoded = d.decode("utf-8").replace('\r\n', '')

            index_start_str = data_decoded.find('0x83')
            index_end_str = data_decoded.find('0x82')

            if index_start_str != -1:
                print('Has sensor data')
                list_data = data_decoded[index_start_str: index_start_str + 19].split('/')
                print(list_data)

                weight = float(list_data[1])
                height = float(list_data[2])
                temperature = float(list_data[3])

                if weight != -1.0:
                    list_weight.append(weight)
                if height != -1.0:
                    list_height.append(height)
                if temperature != -1.0:
                    list_temperature.append(temperature)

                if len(list_weight) >= 10 and len(list_height) >= 10 and len(list_temperature) >= 10:
                    conn.write(b"0")
            
            if index_end_str != -1:
                has_value = True
                print('Done reading sensor')
                continue
        except Exception as e:
            print(e)
    conn.close()
    
    print(list_weight)
    print(list_height)
    print(list_temperature)

    mean_weight = np.mean(list_weight)
    mean_height = np.mean(list_height)
    mean_temperature = np.mean(list_temperature)
    std_weight = np.std(list_weight)
    std_height = np.std(list_height)
    std_temperature = np.std(list_temperature)

    print("Mean weight: {}, Std weight: {}".format(mean_weight, std_weight))
    print("Mean height: {}, Std height: {}".format(mean_height, std_height))
    print("Mean temperature: {}, Std temperature: {}".format(mean_temperature, std_temperature))
    
    processed_list_height = [i for i in list_height if i >= (mean_height - std_height) and i <= (mean_height + std_height)]
    processed_list_weight = [i for i in list_weight if i >= (mean_weight - std_weight) and i <= (mean_weight + std_weight)]
    processed_list_temperature = [i for i in list_temperature if i >= (mean_temperature - std_temperature) and i <= (mean_temperature + std_temperature)]
    
    print(processed_list_weight)
    print(processed_list_height)
    print(processed_list_temperature)
    return 1


print(getSensorData())
