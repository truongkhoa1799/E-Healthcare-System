import hid
import serial
import time, sys, threading
import numpy as np
from threading import Timer

sys.path.append('/home/thesis/Documents/thesis/E-Healthcare-System')
# sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')

MIN_WEIGHT = 10.0
NUM_GET_ESP = 5
DELAY_TIME_ESP32 = 8
DELAY_TIME_RESET_ESP32 = 3
DEVICE_ESP32_PORT = "/dev/ttyUSB0"

from utils.parameters import *
from utils.common_functions import LogMesssage

class MeasureSensor:
    def __init__(self):
        self.has_oso2 = False
        self.__oso2_connection = None
        self.__state_oso2 = 0
        self.__list_spo2 = []
        self.__list_heart_rate = []
        self.__time_missing_data = 0

        self.has_esp = False
        self.__esp_connection = None
        self.__pre_weight = 0.0
        self.__cur_weight = 0.0
        self.__list_weight = []
        self.__list_height = []
        self.__list_temperature = []
        self.__num_esp_records = 0
        self.__delay_esp32 = False
        self.__sum_time_delay = 0
        self.__pre_time = 0

        self.final_spo2 = None
        self.final_heart_pulse = None
        self.final_temperature = None
        self.final_height = None
        self.final_weight = None
        self.final_bmi = None

    def openConnectionSensors(self):
        try:
            self.__oso2_connection = hid.device()
            self.__oso2_connection.open(1155, 22320)  # TREZOR VendorID/ProductID
            # enable non-blocking mode
            self.__oso2_connection.set_nonblocking(1)

            LogMesssage("Opening connection Heart Rate and SPO2 measurement device", opt=0)
            LogMesssage("Manufacturer: %s" % self.__oso2_connection.get_manufacturer_string(), opt=0)
            LogMesssage("Product: %s" % self.__oso2_connection.get_product_string(), opt=0)
            LogMesssage("Serial No: %s" % self.__oso2_connection.get_serial_number_string(), opt=0)
            
            # Open connection esp
            self.__esp_connection = serial.Serial(DEVICE_ESP32_PORT, baudrate=115200, timeout=0.1)
            self.__esp_connection.write(b"1")  # write a string
            LogMesssage("Opening connection with height and temperature measurement device", opt=0)

            return 0

        except Exception as e:
            LogMesssage('Fail to open connection with sensors device: {e}'.format(e=e))
            return -1

    # ret -1: error
    # ret -2: disconnect device
    # ret 0 : normal
    # ret 1 : enought data
    def getSensorsData(self):
        try:
            self.__getOSO2Data()

            if self.__delay_esp32 == False:
                self.__getESPData()
            else:
                self.__delayESP32()

            # Check whether has enought esp and oso2 data
            if self.has_esp and self.has_oso2: return 1
            else: return 0
                
        except Exception as e:
            # Send messgae to stop esp32
            self.__esp_connection.write(b"0")

            if str(e) == 'read error': return -2

            else:
                LogMesssage('Has error at __getSensorsData: {e}'.format(e=e))
                return -1
    
    def __stateOSO2_0(self):
        data = self.__oso2_connection.read(64)
        if data:
            self.__readOSO2Data(data)
            self.__state_oso2 = 1
            LogMesssage('Has first data from OSO2 device')

    def __stateOSO2_1(self):
        data = self.__oso2_connection.read(64)
        if data:
            self.__time_missing_data = 0
            self.__readOSO2Data(data)
        else:
            # LogMesssage('Missing data: {num}'.format(num=self.__time_missing_data))
            # print(self.__read_oso2.is_alive())
            self.__time_missing_data += 1

            time.sleep(1)
        
        if self.__time_missing_data == 3:
            self.__state_oso2 = 2
    
    def __stateOSO2_2(self):
        LogMesssage('Done read data from OSO2 device')

        self.has_oso2 = True
        processed_list_spo2 = self.__removeNoiseListData(self.__list_spo2)
        processed_list_heart_pulse = self.__removeNoiseListData(self.__list_heart_rate)

        self.final_spo2 = str(int(np.mean(processed_list_spo2)))
        self.final_heart_pulse = str(int(np.mean(processed_list_heart_pulse)))
        
        # request = {
        #     'type': glo_va.REQUEST_UPDATE_OSO2, 
        #     'data': {
        #         'heart_pulse': self.final_heart_pulse, 
        #         'spo2': self.final_spo2,
        #         'final': 0
        #     }
        # }
        # glo_va.gui.queue_request_states_thread.put(request)

        self.__state_oso2 = 0
        self.__list_spo2 = []
        self.__list_heart_rate = []
        self.__time_missing_data = 0

        print("Final spo2: {}, final hear rate: {}".format(self.final_spo2, self.final_heart_pulse))
        LogMesssage('Back to wait read first data from OSO2 device')

        # simulate has esp
        # self.has_esp = True
        

    def __getOSO2Data(self):
        if self.__state_oso2 == 0:
            self.__stateOSO2_0()
        elif self.__state_oso2 == 1:
            self.__stateOSO2_1()
        elif self.__state_oso2 == 2:
            self.__stateOSO2_2()

    def __getESPData(self):
        # Read esp32 data
        esp_message = self.__esp_connection.read(64)
        esp_message_decoded = esp_message.decode("utf-8").replace('\r\n', '')

        pos_start = esp_message_decoded.find('0x83')
        pos_end = esp_message_decoded.find('0x81')

        if pos_start != -1 and pos_end != -1:
            extract_message = esp_message_decoded[pos_start + 5: pos_end - 1]
            list_data = extract_message.split('/')
            # List_data: weight, height, temperature

            try:
                self.__cur_weight = float(list_data[0])
            except Exception as e:
                return

            # print(type(MIN_WEIGHT))
            # print(type(self.__cur_weight))
            LogMesssage("[oso2_sensor___getESPData]: Has data from ESP32. Weight: {}, Height: {}, Temperature: {}".format(list_data[0], list_data[1], list_data[2]))
            
            if self.__cur_weight >= MIN_WEIGHT and abs(self.__cur_weight - self.__pre_weight) < MIN_WEIGHT:
                self.__list_weight.append(self.__cur_weight)
                self.__list_height.append(float(list_data[1]))
                self.__list_temperature.append(float(list_data[2]))
                self.__num_esp_records += 1
                LogMesssage("[oso2_sensor___getESPData]: Has {} records from esp".format(self.__num_esp_records))

                if self.__num_esp_records >= NUM_GET_ESP:
                    # remove noise data in list
                    processed_list_weight = self.__removeNoiseListData(self.__list_weight)
                    processed_list_height = self.__removeNoiseListData(self.__list_height)
                    processed_list_temperature = self.__removeNoiseListData(self.__list_temperature)

                    # get final values
                    self.final_weight = str(round(float(np.mean(processed_list_weight)), 1))
                    self.final_height = str(round(float(np.mean(processed_list_height)), 2))
                    self.final_temperature = str(round(float(np.mean(processed_list_temperature)), 1))

                    LogMesssage("[oso2_sensor___getESPData]: Done getting datas ESP32. Final weight: {}, final height: {}, final temperature: {}".format(self.final_weight, self.final_height, self.final_temperature))

                    self.__num_esp_records = 0
                    self.__list_height = []
                    self.__list_weight = []
                    self.__list_temperature = []
                    self.__pre_weight = 0.0
                    self.__cur_weight = 0.0
                    self.has_esp = True
                    request = {
                        'type': glo_va.REQUEST_UPDATE_ESP, 
                        'data': {
                            'height': self.final_height, 'weight': self.final_weight, 
                            'temperature': self.final_temperature, 'bmi': self.final_bmi, 
                            'final': 0
                        }
                    }
                    glo_va.gui.queue_request_states_thread.put(request)

                    # reset esp32
                    self.__esp_connection.write(b"0")
                    self.__delay_esp32 = True
                    return
            else:
                print('\tReset reading esp32')
                self.__num_esp_records = 0
                self.__list_height = []
                self.__list_weight = []
                self.__list_temperature = []

            self.__pre_weight = self.__cur_weight
    
    def __delayESP32(self):
        if self.__pre_time == 0:
            self.__pre_time = time.time()
        else:
            self.__sum_time_delay += (time.time() - self.__pre_time)
            self.__pre_time = time.time()
        
        if self.__sum_time_delay >= DELAY_TIME_ESP32:
            self.__pre_time = 0
            self.__sum_time_delay = 0
            self.__delay_esp32 = False
            LogMesssage("[oso2_sensor___delayESP32]: Done restart ESP32")
        elif self.__sum_time_delay >= DELAY_TIME_RESET_ESP32:
            self.__esp_connection.write(b"1")

    def __readOSO2Data(self, data):
        # print(data)
        hex_string = ""
        sub_str_set = []

        for element in data:
            hex_string += hex(element)

        hex_string = hex_string.replace('x', '')
        sub_str_set = hex_string.split('0a0d')

        sub_str_set = sub_str_set[:-1]

        for i in range(len(sub_str_set)):
            if sub_str_set[i][:3] == '04f':
                OFFSET = i*16
                hr_index = OFFSET + 2
                spo2_index = OFFSET + 10

                # request = {
                #     'type': glo_va.REQUEST_UPDATE_OSO2, 
                #     'data': {
                #         'heart_pulse': data[hr_index], 
                #         'spo2': data[spo2_index], 
                #         'final': -1
                #     }
                # }
                # glo_va.gui.queue_request_states_thread.put(request)

                print("spo2: {}, hear rate: {}".format(data[spo2_index], data[hr_index]))

                self.__list_heart_rate.append(data[hr_index])
                self.__list_spo2.append(data[spo2_index])

    def __removeNoiseListData(self, list_data):
        mean = np.mean(list_data)
        std = np.std(list_data)
        processed_list = [i for i in list_data if i >= (mean - std) and i <= (mean + std)]
        return processed_list

    def closeDevice(self):
        try:
            self.__esp_connection.write(b"0")
            self.__esp_connection.close()
            LogMesssage("Closing connection with ESP32 device", opt=0)

            self.__oso2_connection.close()
            LogMesssage("Closing connection Heart Rate and SPO2 measurement device", opt=0)
        except Exception as e:
            LogMesssage('Fail to close device sensor connection')


# sensor = MeasureSensor()
# ret = sensor.openConnectionSensors()
# if ret == -1:
#     print("Not connected")
#     exit(-1)

# while True:
#     ret = sensor.getSensorsData()
#     # disconnect
#     if ret == -2:
#         sensor.closeDevice()
#         LogMesssage("[State_8]: Connection with sensors device is disconnected")
#         break
#     elif ret == 1:
#         sensor.closeDevice()
#         LogMesssage("[State_8]: Have data from oso2 and esp device. Disconnect device")
#         break