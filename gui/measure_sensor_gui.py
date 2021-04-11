from utils.common_functions import LogMesssage
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore, QtWidgets

import sys, time, threading, queue

# sys.path.append('/home/thesis/Documents/thesis/E-Healthcare-System')
# sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')

from utils.parameters import *
from sensor.oso2_sensor import MeasureSensor
from gui.ok_dialog import OkDialogClass
from gui.yes_no_dialog import QDialogClass

class MeasureSensorDialog(QDialog):
    def __init__(self, ret, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(glo_va.MEASURE_SENSOR_GUI_PATH, self) # Load the .ui file
        self.ret = {'blood_pressure': '', 'heart_pulse': '', 'temperature': '', 'spo2': '', 'height': '', 'weight': ''}
        self.index_image = 0
        self.num_image = 2

        self.MAIN_FRAME = 0
        self.INSTRUCTION_FRAME = 1

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
        # 0: main frame
        # 1: instruction frame
        self.current_frame = self.MAIN_FRAME

        self.__list_image = [self.first_image, self.second_image]

        self.queue_request_states_thread = queue.Queue(maxsize = 10)
        check_request_states_thread = QtCore.QTimer(self)
        check_request_states_thread.timeout.connect(self.__CheckRequestStatesThread)
        check_request_states_thread.start(1000)

        self.progress_bar.setValue(0)
        self.__init_device = False
        self.__has_osos2 = False
        self.__has_esp = False

        self.__sensor_measurement = MeasureSensor()
        self.__init_device = True
    
    def __CheckRequestStatesThread(self):
        if self.queue_request_states_thread.empty():
            return
        
        request = self.queue_request_states_thread.get()
        if self.current_frame != self.MAIN_FRAME:
            LogMesssage('Discard request message: {}'.format(request['type'] == glo_va.REQUEST_UPDATE_OSO2))
            return

        if request['type'] == glo_va.REQUEST_UPDATE_OSO2:
            # print(request['data'])
            if request['data']['status'] == 0:
                self.__has_oso2 = True
                LogMesssage('Received last OSO2 messgae')
                if self.__has_esp or self.__has_oso2:
                    self.progress_bar.setValue(50)
                elif self.__has_esp and self.__has_oso2:
                    self.progress_bar.setValue(100)
                else:
                    self.progress_bar.setValue(0)
                    
            self.heart_rate.setText(str(int(request['data']['heart_rate'])))
            self.spo2.setText(str(int(request['data']['spo2'])))
        
        if request['type'] == glo_va.REQUEST_NOTIFY_DISCONNECT_OSO2_DEVICE:
            self.__notifyDisconnectOSO2Device()

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
            self.current_frame = self.INSTRUCTION_FRAME
            self.image_stack.setCurrentWidget(self.first_image)
            self.stackedWidget.setCurrentWidget(self.guide)
            LogMesssage('Patient change to instruction measure sensor frame')
            
        elif opt == glo_va.BUTTON_QUIT_GUILDE_SENSOR:
            self.index_image = 0
            self.current_frame = self.MAIN_FRAME
            self.stackedWidget.setCurrentWidget(self.main_step)
            LogMesssage('Patient change to measure sensor frame')

        elif opt == glo_va.BUTTON_CAPTURE_SENSOR:
            self.__measureSenSor()

        elif opt == glo_va.BUTTON_CONFIRM_SENSOR:
            self.confirmSensor()
    
    def __measureSenSor(self):
        try:
            ret_measure_sensor = self.__sensor_measurement.startMeasure()
            if ret_measure_sensor == -1:
                self.__notifyDisconnectOSO2Device()

            elif ret_measure_sensor == 0:
                ret = None
                data = {}
                data['opt'] = 4
                self.submit_dialog = OkDialogClass(-2, data)
                self.submit_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
                if self.submit_dialog.exec_() == QtWidgets.QDialog.Accepted:
                    glo_va.button = glo_va.BUTTON_OKAY

        except Exception as e:
            LogMesssage('Has error at __measureSenSor in measure_sensor_gui: {e}'.format(e=e))
    
    def __notifyDisconnectOSO2Device(self):
        ret = None
        data = {}
        data['opt'] = 3
        self.submit_dialog = OkDialogClass(-2, data)
        self.submit_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if self.submit_dialog.exec_() == QtWidgets.QDialog.Accepted:
            glo_va.button = glo_va.BUTTON_OKAY
    
    def confirmSensor(self):
        try:
            ret = None
            dialog = QDialogClass(ret, glo_va.CONFIRM_SENSOR_INFORMATION)
            dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            if dialog.exec_() == QtWidgets.QDialog.Accepted and int(dialog.ret) == -1:
                return

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
                self.__closeMeasureSensor()
                LogMesssage('Patient successfully have all sensor information')
                self.close()
            else:
                self.ret['heart_pulse'] = hear_rate
                self.ret['spo2'] = spo2
                self.__closeMeasureSensor()
                LogMesssage('Patient successfully have all sensor information')
                self.close()

        except Exception as e:
            LogMesssage('Fail to confirm MeasureSensor: {e}'.format(e=e), opt=2)
        
    def closeEvent(self, event):
        self.__closeMeasureSensor()
        self.accept()

    def __closeMeasureSensor(self):
        if self.__init_device == True:
            self.__sensor_measurement.closeDevice()
            self.__init_device = False