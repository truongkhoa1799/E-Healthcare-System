import hid
import serial
import time
import numpy as np

MIN_WEIGHT = 5.0
NUM_GET_ESP = 7

UART_PORT_0 = "/dev/ttyUSB0"
UART_PORT_1 = "/dev/ttyUSB1"

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
        self.__uart_connection_0 = None
        self.__uart_connection_1 = None
        self.__uart_0_message_decoded = ""
        self.__uart_1_message_decoded = ""

        self.__pre_weight = 0.0
        self.__cur_weight = 0.0
        self.__list_weight = []
        self.__list_height = []
        self.__list_temperature = []
        self.__num_esp_records = 0

        self.final_spo2 = ""
        self.final_heart_pulse = ""
        self.final_temperature = ""
        self.final_height = ""
        self.final_weight = ""
        self.final_bmi = ""

    def openConnectionSensors(self):
        try:
            self.has_esp = False
            self.has_oso2 = False

            self.final_spo2 = ""
            self.final_heart_pulse = ""
            self.final_temperature = ""
            self.final_height = ""
            self.final_weight = ""
            self.final_bmi = ""

            # Open connection with oso2 devuce
            self.__oso2_connection = hid.device()
            self.__oso2_connection.open(1155, 22320)  # TREZOR VendorID/ProductID
            # enable non-blocking mode
            self.__oso2_connection.set_nonblocking(1)
            LogMesssage("Opening connection Heart Rate and SPO2 measurement device", opt=0)
            
            # Open UART_0 connection
            self.__uart_connection_0 = serial.Serial(UART_PORT_0, baudrate=115200, timeout=0.1)
            self.__uart_connection_0.write(b"1")  # write a string
            LogMesssage("Opening connection with UART 0 device", opt=0)

            # Open UART_1 connection
            self.__uart_connection_1 = serial.Serial(UART_PORT_1, baudrate=115200, timeout=0.1)
            self.__uart_connection_1.write(b"1")  # write a string
            LogMesssage("Opening connection with UART 1 device", opt=0)

            return 0

        except Exception as e:
            LogMesssage('Fail to open connection with sensors device: {e}'.format(e=e))
            return -1

    # ret -1: error
    # ret -2: disconnect device
    # ret 0 : normal
    # ret 1 : enought data
    # ret 2: not have esp, have oso2
    # ret 3: not have oso2, have esp
    def getSensorsData(self):
        try:
            # Get sensor infdrmation of oso2 device
            if not self.has_oso2: self.__getOSO2Data()

            # Get sensor infdrmation of esp devices
            if not self.has_esp: self.__getESPData()
            
            if not self.has_esp and not self.has_oso2: return 0
            elif self.has_esp and self.has_oso2: return 1
            elif not self.has_esp and self.has_oso2: return 2
            elif not self.has_oso2 and self.has_esp: return 3
            
        except Exception as e:
            if str(e) == 'read error': return -2

            else:
                LogMesssage('Has error at __getSensorsData: {e}'.format(e=e))
                return -1

############################################################
# OSO2 DEVICE                                              #
############################################################
    ########################################################
    # OSO2 STATE 0                                         #
    ########################################################
    def __stateOSO2_0(self):
        data = self.__oso2_connection.read(64)
        if data:
            self.__readOSO2Data(data)
            self.__state_oso2 = 1
            LogMesssage('[measuring_sensors___stateOSO2_0]: Has first data from OSO2 device')
    
    ########################################################
    # OSO2 STATE 1                                         #
    ########################################################
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
        
        if self.__time_missing_data == 3: self.__state_oso2 = 2
    
    ########################################################
    # OSO2 STATE 2                                         #
    ########################################################
    def __stateOSO2_2(self):
        LogMesssage('[measuring_sensors___stateOSO2_2]: Done read data from OSO2 device')

        self.has_oso2 = True
        processed_list_spo2 = self.__removeNoiseListData(self.__list_spo2)
        processed_list_heart_pulse = self.__removeNoiseListData(self.__list_heart_rate)

        self.final_spo2 = str(int(np.mean(processed_list_spo2)))
        self.final_heart_pulse = str(int(np.mean(processed_list_heart_pulse)))
        
        request = {
            'type': glo_va.REQUEST_UPDATE_OSO2, 
            'data': {
                'heart_pulse': self.final_heart_pulse, 
                'spo2': self.final_spo2,
                'final': 0
            }
        }
        glo_va.gui.queue_request_states_thread.put(request)

        self.__state_oso2 = 0
        self.__list_spo2 = []
        self.__list_heart_rate = []
        self.__time_missing_data = 0

        LogMesssage("[measuring_sensors___stateOSO2_0]: Final spo2: {}, final hear rate: {}".format(self.final_spo2, self.final_heart_pulse))

    ########################################################
    # GET OSO2 DATA                                        #
    ########################################################
    def __getOSO2Data(self):
        if self.__state_oso2 == 0: self.__stateOSO2_0()

        elif self.__state_oso2 == 1: self.__stateOSO2_1()

        elif self.__state_oso2 == 2: self.__stateOSO2_2()
    
    ########################################################
    # EXTRACT OSO2 DATA                                    #
    ########################################################
    def __readOSO2Data(self, data):
        # print(data)
        hex_string = ""
        sub_str_set = []

        for element in data: hex_string += hex(element)

        hex_string = hex_string.replace('x', '')
        sub_str_set = hex_string.split('0a0d')

        sub_str_set = sub_str_set[:-1]

        for i in range(len(sub_str_set)):
            if sub_str_set[i][:3] == '04f':
                OFFSET = i*16
                hr_index = OFFSET + 2
                spo2_index = OFFSET + 10

                request = {
                    'type': glo_va.REQUEST_UPDATE_OSO2, 
                    'data': {
                        'heart_pulse': data[hr_index], 
                        'spo2': data[spo2_index], 
                        'final': -1
                    }
                }
                glo_va.gui.queue_request_states_thread.put(request)

                print("spo2: {}, hear rate: {}".format(data[spo2_index], data[hr_index]))

                self.__list_heart_rate.append(data[hr_index])
                self.__list_spo2.append(data[spo2_index])
    
############################################################
# ESP DEVICE                                               #
############################################################
    ########################################################
    # EXTRACT ESP DATA                                     #
    ########################################################
    # 0 : ok, weight, height, temperature 
    # -1: error
    def __extractESPMessage(self, weight, height_temp):
        try:
            weight_splited = weight.split('/')
            height_temp_splited = height_temp.split('/')
            if weight_splited[0] != "0x83" \
                or height_temp_splited[0] != "0x83" \
                or weight_splited[2] != "0x81" \
                or height_temp_splited[3] != "0x81":
                return -1, None, None, None
            
            return 0, float(weight_splited[1]), float(height_temp_splited[1]), float(height_temp_splited[2])

        except Exception as e:
            return -1, None, None, None

    ########################################################
    # GET ESP DATA                                         #
    ########################################################
    def __getESPData(self):
        # Read esp32 data
        uart_0_message = self.__uart_connection_0.read(64).decode("utf-8").replace('\r\n', '')
        uart_1_message = self.__uart_connection_1.read(64).decode("utf-8").replace('\r\n', '')

        if uart_0_message != '': self.__uart_0_message_decoded = uart_0_message
        if uart_1_message != '': self.__uart_1_message_decoded = uart_1_message
        
        if self.__uart_0_message_decoded != '' and self.__uart_1_message_decoded != '':
            weight_message, height_temp_message = None, None
            
            if len(self.__uart_0_message_decoded) > len(self.__uart_1_message_decoded):
                height_temp_message = self.__uart_0_message_decoded
                weight_message = self.__uart_1_message_decoded
            else:
                height_temp_message = self.__uart_1_message_decoded
                weight_message = self.__uart_0_message_decoded

            self.__uart_0_message_decoded, self.__uart_1_message_decoded = '', ''

            ret, weight, height, temperature = self.__extractESPMessage(weight_message, height_temp_message)
            if ret == -1 or height == -1.0: return
            
            LogMesssage("[measure_sensors___getESPData]: Has data from ESP32. Weight: {}, Height: {}, Temperature: {}".format(weight, height, temperature))
            
            self.__cur_weight = weight
            
            if self.__cur_weight >= MIN_WEIGHT and abs(self.__cur_weight - self.__pre_weight) < MIN_WEIGHT:
                self.__list_weight.append(self.__cur_weight)
                self.__list_height.append(glo_va.BASE_HEIGHT_SENSOR - height)
                self.__list_temperature.append(temperature + glo_va.ADDITIONAL_TEMP_SENSOR)

                request = {
                    'type': glo_va.REQUEST_UPDATE_ESP,
                    'data': {
                        'height': str(round(height, 2)), 'weight': str(round(weight, 1)), 
                        'temperature': str(round(temperature, 1)), 'bmi': "0", 
                        'final': -1
                    }
                }
                glo_va.gui.queue_request_states_thread.put(request)

                self.__num_esp_records += 1
                LogMesssage("[measure_sensors___getESPData]: Has {} records from esp".format(self.__num_esp_records))

                if self.__num_esp_records >= NUM_GET_ESP:
                    # remove noise data in list
                    processed_list_weight = self.__removeNoiseListData(self.__list_weight)
                    processed_list_height = self.__removeNoiseListData(self.__list_height)
                    processed_list_temperature = self.__removeNoiseListData(self.__list_temperature)

                    # get final values
                    self.final_weight = np.mean(processed_list_weight)
                    self.final_height = np.mean(processed_list_height)
                    self.final_temperature = np.mean(processed_list_temperature)
                    self.final_bmi = self.final_weight / pow(self.final_height, 2)

                    LogMesssage("[measure_sensors___getESPData]: Done getting datas ESP32. Final weight: {}, final height: {}, final temperature: {}, final bmi: {}".format(self.final_weight, self.final_height, self.final_temperature, self.final_bmi))

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
                            'height': str(round(self.final_height, 2)), 'weight': str(round(self.final_weight, 1)), 
                            'temperature': str(round(self.final_temperature, 1)), 'bmi':str(round(self.final_bmi, 1)),
                            'final': 0
                        }
                    }
                    glo_va.gui.queue_request_states_thread.put(request)

            else:
                LogMesssage('\tReset reading esp32')
                self.__num_esp_records = 0
                self.__list_height = []
                self.__list_weight = []
                self.__list_temperature = []

            self.__pre_weight = self.__cur_weight

############################################################
# REMOVE NOISE                                             #
############################################################
    def __removeNoiseListData(self, list_data):
        mean = np.mean(list_data)
        std = np.std(list_data)
        processed_list = [i for i in list_data if i >= (mean - std) and i <= (mean + std)]
        return processed_list

    def closeDevice(self):
        try:
            self.__uart_connection_0.write(b"0")
            time.sleep(0.01)
            self.__uart_connection_1.write(b"0")
            time.sleep(0.1)
            self.__uart_connection_0.close()
            time.sleep(0.1)
            self.__uart_connection_1.close()
            LogMesssage("[measure_sensors_closeDevice]: Closing connection with ESP32 device", opt=0)

            self.__oso2_connection.close()
            LogMesssage("[measure_sensors_closeDevice]: Closing connection Heart Rate and SPO2 measurement device", opt=0)
        except Exception as e:
            LogMesssage('[measure_sensors_closeDevice]: Fail to close device sensor connection')


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