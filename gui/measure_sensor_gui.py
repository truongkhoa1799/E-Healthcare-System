from utils.common_functions import LogMesssage
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore, QtWidgets

import sys, time, threading, queue

# sys.path.append('/home/thesis/Documents/thesis/E-Healthcare-System')
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')

from utils.parameters import *
from sensor.oso2_sensor import MeasureSensor
from ok_dialog import OkDialogClass
from yes_no_dialog import QDialogClass

class MeasureSensorDialog(QDialog):
    def __init__(self, ret, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(glo_va.MEASURE_SENSOR_GUI_PATH, self) # Load the .ui file
        self.ret = -2
        self.index_image = 0
        self.num_image = 2

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

        self.queue_request_states_thread = queue.Queue(maxsize = 10)
        check_request_states_thread = QtCore.QTimer(self)
        check_request_states_thread.timeout.connect(self.__CheckRequestStatesThread)
        check_request_states_thread.start(1000)

        self.progress_bar.setValue(0)
        self.__init_device = False
    
    def __CheckRequestStatesThread(self):
        if self.queue_request_states_thread.empty():
            return
        
        request = self.queue_request_states_thread.get()

        if request['type'] == 0:
            print(request['data'])
            self.heart_rate.setText(str(int(request['data']['heart_rate'])))
            self.spo2.setText(str(int(request['data']['spo2'])))


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
            self.measureSenSor()

        elif opt == glo_va.BUTTON_CONFIRM_SENSOR:
            self.confirmSensor()
    
    def measureSenSor(self):
        try:
            if self.__init_device == False:
                self.sensor_measurement = MeasureSensor()
                self.__init_device = True

            self.sensor_measurement.startMeasure()

        except Exception as e:
            LogMesssage('Fail to init MeasureSensor: {e}'.format(e=e), opt=2)
            LogMesssage('Please open OSO2 before capture', opt=2)
    
    def confirmSensor(self):
        try:
            hear_rate = str(self.heart_rate.text())
            spo2 = str(self.spo2.text())
            temperature = str(self.temperature.text())
            height = str(self.height.text())
            weight = str(self.weight.text())
            BMI = str(self.BMI.text())

            # if hear_rate == '' or spo2 == '' \
            #     or temperature == '' or height == '' \
            #     or weight == '' or BMI == '':
            if hear_rate == '' or spo2 == '':
                data = {}
                data['opt'] = 3
                submit_dialog = OkDialogClass(-2, data)
                submit_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
                submit_dialog.exec_()
            else:
                ret = None
                dialog = QDialogClass(ret, glo_va.CONFIRM_SENSOR_INFORMATION)
                dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
                if dialog.exec_() == QtWidgets.QDialog.Accepted and int(dialog.ret) == 0:
                    self.closeMeasureSensor()
                    LogMesssage('Patient successfully have all sensor information')
                    self.close()

        except Exception as e:
            LogMesssage('Fail to confirm MeasureSensor: {e}'.format(e=e), opt=2)
    
    def closeMeasureSensor(self):
        if self.__init_device == True:
            self.sensor_measurement.closeDevice()
            self.__init_device = False
    
        
    def closeEvent(self, event):
        if self.ret == -2:
            self.ret = -1
            
            self.closeMeasureSensor()
            self.accept()
