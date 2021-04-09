from PyQt5.QtWidgets import QDialog
import sys, time, threading

# sys.path.append('/home/thesis/Documents/thesis/E-Healthcare-System')
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')
from utils.parameters import *
from sensor.oso2_sensor import testReadSensor

class MeasureSensorDialog(QDialog):
    def __init__(self, ret, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(glo_va.MEASURE_SENSOR_GUI_PATH, self) # Load the .ui file
        self.ret = -2
        self.index_image = 0
        self.num_image = 2

        # self.setupUi(self)

        self.pre_but.clicked.connect(lambda: self.__onButtonListenning(glo_va.BUTTON_BACK_GUILDE_SENSOR))
        self.next_but.clicked.connect(lambda: self.__onButtonListenning(glo_va.BUTTON_NEXT_GUILDE_SENSOR))
        self.guilde_but.clicked.connect(lambda: self.__onButtonListenning(glo_va.BUTTON_GUILDE_SENSOR))
        self.back_guilde_but.clicked.connect(lambda: self.__onButtonListenning(glo_va.BUTTON_QUIT_GUILDE_SENSOR))
        self.capture_sensor.clicked.connect(lambda: self.__onButtonListenning(glo_va.BUTTON_CAPTURE_SENSOR))
        self.confirm_sensor.clicked.connect(lambda: self.__onButtonListenning(glo_va.BUTTON_CONFIRM_SENSOR))

        self.image_stack.addWidget(self.first_image)
        self.image_stack.addWidget(self.second_image)

        self.stackedWidget.addWidget(self.guide)
        self.stackedWidget.addWidget(self.main_step)

        self.stackedWidget.setCurrentWidget(self.main_step)

        self.__list_image = [self.first_image, self.second_image]

        self.progress_bar.setValue(0)
    
    def __onButtonListenning(self, opt):
        if opt == glo_va.BUTTON_BACK_GUILDE_SENSOR:
            if self.index_image > 0:
                self.index_image -= 1
                # print(self.state)
                self.image_stack.setCurrentWidget(self.__list_image[self.index_image])

        elif opt == glo_va.BUTTON_NEXT_GUILDE_SENSOR:
            if self.index_image < 2 - 1:
                self.index_image += 1
                # print(self.state)
                self.image_stack.setCurrentWidget(self.__list_image[self.index_image])

        elif opt == glo_va.BUTTON_GUILDE_SENSOR:
            self.image_stack.setCurrentWidget(self.first_image)
            self.stackedWidget.setCurrentWidget(self.guide)
            
        elif opt == glo_va.BUTTON_QUIT_GUILDE_SENSOR:
            self.index_image = 0
            self.stackedWidget.setCurrentWidget(self.main_step)

        elif opt == glo_va.BUTTON_CAPTURE_SENSOR:
            print('Capture')
            self.measureSenSor()

        elif opt == glo_va.BUTTON_CONFIRM_SENSOR:
            print('Confirm')
            self.__ClearPage()
    
    def measureSenSor(self):
        measure_sensor_thread = threading.Thread(target=testReadSensor, args=())
        measure_sensor_thread.daemon = True
        measure_sensor_thread.start()

        for i in range(20):
            # self.progress_bar.setValue(i*5)
            # print('Hello')
            if glo_va.temp_sensor['spo2'] != -1:
                self.spo2.setText(str(glo_va.temp_sensor['spo2']))

            if glo_va.temp_sensor['hr'] != -1:
                self.heart_rate.setText(str(glo_va.temp_sensor['hr']))
        
            time.sleep(1)
        

        self.spo2.setText(str(glo_va.temp_sensor['spo2']))
        self.heart_rate.setText(str(glo_va.temp_sensor['hr']))


    def closeEvent(self, event):
        if self.ret == -2:
            self.ret = -1
            self.__ClearPage()
            self.accept()
    
    def __ClearPage(self):
        # self.temperature.setText("")
        # self.height.setText("")
        # self.weight.setText("")
        # self.BMI.setText("")
        # self.heart_rate.setText("")
        # self.spo2.setText("")

        glo_va.temp_sensor['height'] = -1
        glo_va.temp_sensor['weight'] = -1
        glo_va.temp_sensor['spo2'] = -1
        glo_va.temp_sensor['hr'] = -1
        glo_va.temp_sensor['temperature'] = -1
