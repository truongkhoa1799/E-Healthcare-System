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
        self.__oso2 = hid.device()
        self.__oso2.open(1155, 22320)  # TREZOR VendorID/ProductID
        
        self.__state_oso2 = 0

        self.__time_missing_data = 0
        self.__list_spo2 = []
        self.__list_heart_rate = []

        self.__enable_run_oso2 = None
        self.__read_oso2 = None

        self.__has_oso2 = False
        self.__has_esp = False
                
        LogMesssage("Opening connection Heart Rate and SPO2 measurement device", opt=0)
        LogMesssage("Manufacturer: %s" % self.__oso2.get_manufacturer_string(), opt=0)
        LogMesssage("Product: %s" % self.__oso2.get_product_string(), opt=0)
        LogMesssage("Serial No: %s" % self.__oso2.get_serial_number_string(), opt=0)

        # enable non-blocking mode
        self.__oso2.set_nonblocking(1)

    def startMeasure(self):
        if self.__read_oso2 is None or not self.__read_oso2.is_alive():
            self.__enable_run_oso2 = True
            
            self.__has_oso2 = False
            self.__has_esp = False
            
            self.__read_oso2 = threading.Thread(target=self.__getOSO2Data, args=())
            self.__read_oso2.daemon = True
            self.__read_oso2.start()
            LogMesssage('Start thread measuring herat rate and spo2')
        else:
            LogMesssage('Thread measuring herat rate and spo2 is already running')

    def __getOSO2Data(self):
        while self.__enable_run_oso2:
            if self.__state_oso2 == 0:
                self.__stateOSO2_0()
            elif self.__state_oso2 == 1:
                self.__stateOSO2_1()
            elif self.__state_oso2 == 2:
                self.__stateOSO2_2()
            
        LogMesssage('Stop thread measuring herat rate and spo2')
    
    def __stateOSO2_0(self):
        data = self.__oso2.read(64)
        if data:
            self.__readOSO2Date(data)
            self.__state_oso2 = 1
            LogMesssage('Has first data from OSO2 device')

    def __stateOSO2_1(self):
        data = self.__oso2.read(64)
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

        mean_spo2 = statistics.mean(self.__list_spo2)
        mean_heart_rate = statistics.mean(self.__list_heart_rate)
        
        # print(mean_spo2)
        # print(mean_heart_rate)

        request = {'type': 0, 'data': {'heart_rate': mean_heart_rate, 'spo2': mean_spo2}}
        glo_va.measure_sensor_dialog.queue_request_states_thread.put(request)
        
        LogMesssage('Back to wait read first data from OSO2 device')
        self.__time_missing_data == 0
        self.__state_oso2 = 0
        self.__has_oso2 = True

        if self.__has_esp and self.__has_oso2:
            self.__stopMeasure()

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

                request = {'type': 0, 'data': {'heart_rate': data[hr_index], 'spo2': data[spo2_index]}}
                glo_va.measure_sensor_dialog.queue_request_states_thread.put(request)

                self.__list_heart_rate.append(data[hr_index])
                self.__list_spo2.append(data[spo2_index])
        
    def __stopMeasure(self):
        if self.__read_oso2.is_alive():
            self.__enable_run_oso2 = False
            # self.__read_oso2.join()

    def closeDevice(self):
        try:
            self.__stopMeasure()
            self.__oso2.close()
            LogMesssage("Closing connection Heart Rate and SPO2 measurement device", opt=0)
        except Exception as e:
            LogMesssage('Fail to close device sensor connection')


# sensor = MeasureSensor()
# sensor.startMeasure()
# # time.sleep(2)
# # sensor.startMeasure()
# listening_sensor = threading.Event()

# while not listening_sensor.is_set():
#     # self.progress_bar.setValue((i+1)*5)
#     # print('Hello')
#     # if glo_va.temp_sensor['spo2'] != -1:
#     #     self.spo2.setText(str(glo_va.temp_sensor['spo2']))

#     # if glo_va.temp_sensor['hr'] != -1:
#     #     self.heart_rate.setText(str(glo_va.temp_sensor['hr']))

#     if sensor.status == 1:
#         listening_sensor.set()

#     listening_sensor.wait(1)

# # self.spo2.setText(str(glo_va.temp_sensor['spo2']))
# # self.heart_rate.setText(str(glo_va.temp_sensor['hr']))
# sensor.__stopMeasure()

# # for d in hid.enumerate():
# #     keys = list(d.keys())
# #     keys.sort()
# #     for key in keys:
# #         print("%s : %s" % (key, d[key]))
# #     print()