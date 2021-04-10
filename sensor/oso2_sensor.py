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
        self.__flag_connection_oso2 = False
        self.__flag_connection_esp32 = False

        self.__oso2 = hid.device()
        self.__oso2.open(1155, 22320)  # TREZOR VendorID/ProductID
        
        self.__state_oso2 = 0

        self.__time_missing_data = 0
        self.__list_spo2 = []
        self.__list_heart_rate = []

        self.__enable_run_oso2 = threading.Event()
        self.__read_oso2 = None

        self.status = 0
                
        LogMesssage("Opening connection Heart Rate and SPO2 measurement device", opt=0)
        LogMesssage("Manufacturer: %s" % self.__oso2.get_manufacturer_string(), opt=0)
        LogMesssage("Product: %s" % self.__oso2.get_product_string(), opt=0)
        LogMesssage("Serial No: %s" % self.__oso2.get_serial_number_string(), opt=0)

        # enable non-blocking mode
        self.__oso2.set_nonblocking(1)

    def startMeasure(self):
        if self.__read_oso2 is None or not self.__read_oso2.is_alive():
            self.__read_oso2= threading.Thread(target=self.__getOSO2Data, args=())
            self.__read_oso2.daemon = True
            self.__read_oso2.start()
            LogMesssage('Start thread measuring herat rate and spo2')
        else:
            LogMesssage('Thread measuring herat rate and spo2 is already running')



    def __getOSO2Data(self):
        while not self.__enable_run_oso2.is_set():
            if self.__state_oso2 == 0:
                self.__stateOSO2_0()
            elif self.__state_oso2 == 1:
                self.__stateOSO2_1()
            elif self.__state_oso2 == 2:
                self.__stateOSO2_2()
    
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
        print(self.__list_heart_rate)
        print(self.__list_spo2)
        mean_spo2 = statistics.mean(self.__list_spo2)
        mean_heart_rate = statistics.mean(self.__list_heart_rate)
        print(mean_spo2)
        print(mean_heart_rate)
        LogMesssage('Back to wait read first data from OSO2 device')
        self.__time_missing_data == 0
        self.__state_oso2 = 0
        # self.status += 1


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

                print(data[hr_index])
                print(data[spo2_index])

                self.__list_heart_rate.append(data[hr_index])
                self.__list_spo2.append(data[spo2_index])
        
    def stopMeasure(self):
        if not self.__enable_run_oso2.is_set():
            self.__enable_run_oso2.set()
            self.__read_oso2.join()
            # print(self.__read_oso2.is_alive())

    def closeDevice(self):
        self.stopMeasure()

        if self.__flag_connection_oso2 == True:
            LogMesssage("Closing connection Heart Rate and SPO2 measurement device", opt=0)
            self.__oso2.close()


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
# sensor.stopMeasure()