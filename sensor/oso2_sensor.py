import hid
import time, sys, threading
import statistics
from threading import Timer

sys.path.append('/home/thesis/Documents/thesis/E-Healthcare-System')
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')
from utils.parameters import *
from utils.common_functions import LogMesssage

class MeasureSensor:
    def __init__(self):
        self.__oso2_connection = None
        self.__esp_connection = None

        self.__state_oso2 = 0
        self.__list_spo2 = []
        self.__list_heart_rate = []
        self.__time_missing_data = 0

        self.has_oso2 = False
        self.has_esp = False

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
            LogMesssage("Opening connection with esp device", opt=0)

            self.__state_oso2 = 0
            self.__list_spo2 = []
            self.__list_heart_rate = []
            self.__time_missing_data = 0

            self.has_oso2 = False
            self.has_esp = False

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
            if self.__state_oso2 == 0:
                self.__stateOSO2_0()
            elif self.__state_oso2 == 1:
                self.__stateOSO2_1()
            elif self.__state_oso2 == 2:
                self.__stateOSO2_2()
            
            # Check whether has enought esp and oso2 data
            if self.has_esp and self.has_oso2:
                return 1
            else:
                return 0
                
        except Exception as e:
            self.__time_missing_data == 0
            self.__state_oso2 = 0

            if str(e) == 'read error':
                return -2

            else:
                LogMesssage('Has error at __getSensorsData: {e}'.format(e=e))
                return -1
    
    def __stateOSO2_0(self):
        data = self.__oso2_connection.read(64)
        if data:
            self.__readOSO2Date(data)
            self.__state_oso2 = 1
            LogMesssage('Has first data from OSO2 device')

    def __stateOSO2_1(self):
        data = self.__oso2_connection.read(64)
        if data:
            self.__time_missing_data = 0
            self.__readOSO2Date(data)
        else:
            # LogMesssage('Missing data: {num}'.format(num=self.__time_missing_data))
            # print(self.__read_oso2.is_alive())
            self.__time_missing_data += 1

            time.sleep(1)
        
        if self.__time_missing_data == 3:
            self.__state_oso2 = 2
    
    def __stateOSO2_2(self):
        LogMesssage('Done read data from OSO2 device')
        # print(self.__list_heart_rate)
        # print(self.__list_spo2)

        self.has_oso2 = True
        self.final_spo2 = str(int(statistics.mean(self.__list_spo2)))
        self.final_heart_pulse = str(int(statistics.mean(self.__list_heart_rate)))
        
        request = {
            'type': glo_va.REQUEST_UPDATE_OSO2, 
            'data': {
                'heart_pulse': self.final_heart_pulse, 
                'spo2': self.final_spo2,
                'final': 0
            }
        }
        glo_va.gui.queue_request_states_thread.put(request)

        # simulate has esp
        self.has_esp = True
        self.final_temperature = str(round(float('37.2'),1))
        self.final_height = str(round(float('1.74'),2))
        self.final_weight = str(round(float('84.21'),1))
        self.final_bmi = str(round(float(self.final_weight)/pow(float(self.final_height), 2), 1))

        request = {
            'type': glo_va.REQUEST_UPDATE_ESP, 
            'data': {
                'heart_pulse': self.final_heart_pulse, 'spo2': self.final_spo2, 
                'height': self.final_height, 'weight': self.final_weight, 
                'temperature': self.final_temperature, 'bmi': self.final_bmi, 
                'final': 0
            }
        }
        glo_va.gui.queue_request_states_thread.put(request)
        
        self.__state_oso2 = 0
        self.__list_spo2 = []
        self.__list_heart_rate = []
        self.__time_missing_data = 0

        LogMesssage('Back to wait read first data from OSO2 device')

    def __readOSO2Date(self, data):
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

                request = {
                    'type': glo_va.REQUEST_UPDATE_OSO2, 
                    'data': {
                        'heart_pulse': data[hr_index], 
                        'spo2': data[spo2_index], 
                        'final': -1
                    }
                }
                glo_va.gui.queue_request_states_thread.put(request)

                self.__list_heart_rate.append(data[hr_index])
                self.__list_spo2.append(data[spo2_index])

    def closeDevice(self):
        try:
            self.__oso2_connection.close()
            LogMesssage("Closing connection Heart Rate and SPO2 measurement device", opt=0)
        except Exception as e:
            LogMesssage('Fail to close device sensor connection')


# sensor = MeasureSensor()
# sensor.openConnectionSensors()