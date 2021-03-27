from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QLabel, QTableWidgetItem
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import cv2
import sys, time

# sys.path.append('/home/thesis/Documents/thesis/E-Healthcare-System')
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')
from utils.parameters import *

import queue

YesNoQDialog = uic.loadUiType("gui/dialog.ui")[0]
OkDialog = uic.loadUiType("gui/okpopup.ui")[0]
ProgressBarDialog = uic.loadUiType("gui/progressbar.ui")[0]
# YesNoQDialog = uic.loadUiType("dialog.ui")[0]

class OkDialogClass(QDialog, OkDialog):
    def __init__(self, ret, text, parent=None):
        QDialog.__init__(self, parent)
        self.ret = -2
        self.text = text
        self.setupUi(self)

        self.text_dialog.setText(text)
        self.accept_exist.clicked.connect(lambda: self.__onButtonListenning())
    
    def __onButtonListenning(self):
        self.ret = 0
        self.accept()
        self.close()
    
    def closeEvent(self, event):
        if self.ret == -2:
            self.ret = -1
            self.accept()

class QDialogClass(QDialog, YesNoQDialog):
    def __init__(self, ret, text, parent=None):
        QDialog.__init__(self, parent)
        self.ret = -2
        self.text = text
        self.setupUi(self)

        self.text_dialog.setText(text)
        self.accept_exist.clicked.connect(lambda: self.__onButtonListenning(0))
        self.deny_exist.clicked.connect(lambda: self.__onButtonListenning(1))
    
    def __onButtonListenning(self, opt):
        if opt == 0:
            self.ret = 0
        elif opt == 1:
            self.ret = -1
        self.accept()
        self.close()
    
    def closeEvent(self, event):
        if self.ret == -2:
            self.ret = -1
            self.accept()

class ProgressBarDialogClass(QDialog, ProgressBarDialog):
    def __init__(self, ret, parent=None):
        QDialog.__init__(self, parent)
        self.ret = -2
        self.setupUi(self)

        self.capture_but.clicked.connect(lambda: self.__onButtonListenning(0))
        self.cancel_but.clicked.connect(lambda: self.__onButtonListenning(1))

        self.progress_bar.setValue(0)
        self.measureSenSor()
    
    def __onButtonListenning(self, opt):
        if opt == 0:
            self.progress_bar.setValue(0)
            self.measureSenSor()
            self.ret = 0
            self.accept()
            self.close()
        elif opt == 1:
            self.ret = -1
            self.accept()
            self.close()
    
    def measureSenSor(self):
        for i in range(100):
            self.progress_bar.setValue(i + 1)
            time.sleep(0.05)


    def closeEvent(self, event):
        if self.ret == -2:
            self.ret = -1
            self.accept()

class GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(GUI, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('gui/form.ui', self) # Load the .ui file
        # uic.loadUi('form.ui', self) # Load the .ui file
        
        # register listenning button
        self.exist_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_EXIST))
        self.confirm_user_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_CONFIRM_PATIENT))
        self.view_dep_list.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_VIEW_LIST_DEP))
        self.confirm_dep_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_CONFIRM_DEP))
        self.capture_sensor_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_CAPTURE_SENSOR))
        self.submit_exam_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_SUBMIT_EXAM))

        # All frame of gui
        self.stackedWidget.addWidget(self.recognize_frame)
        self.stackedWidget.addWidget(self.measure_sensor_frame)
        self.stackedWidget.addWidget(self.add_new_patient_frame)
        self.stackedWidget.addWidget(self.view_departments)
        
        self.stackedWidget.setCurrentWidget(self.view_departments)

        # Fix header table widget
        self.table_list_department.horizontalHeader().setSectionResizeMode(2)

        self.queue_request_states_thread = queue.Queue(maxsize = 10)
        check_request_states_thread = QTimer(self)
        check_request_states_thread.timeout.connect(self.__CheckRequestStatesThread)
        check_request_states_thread.start(50)

        self.image_display = None
        self.image_new_user = None
        update_image_timer = QTimer(self)
        update_image_timer.timeout.connect(self.__UpdateImage)
        update_image_timer.start(33)

        # test = QTimer(self)
        # test.timeout.connect(self.__test)
        # test.start(3000)

        self.list_shape_face = [self.front_face, self.up_face, self.down_face, self.left_face, self.right_face]

        # img = cv2.imread('/Users/khoa1799/GitHub/E-Healthcare-System-Server/Manipulate_Data/Original_Face/train/1/IMG_3415.jpg')
        # img = cv2.imread('/home/thesis/Documents/E-Healthcare-System-Server/Manipulate_Data/Original_Face/train/1/IMG_3415.jpg')
        # img = cv2.resize(img, (700,400))
        # qp_image = self.__Convert_To_Display(img)
        # self.img_new_user.setPixmap(qp_image)

        # self.__SetBackgroudMainFrame(1)
        # self.__UpdateListDepartments()
        # self.__MeasureSensor()
        # self.__notificationDialog('Please capture sensor\ninformation and select\nexamination department', 0)
    
    # def __test(self):
    #     # print('hoho')
    #     self.dialog.setFinish('hooho')


    def __onButtonsListenning(self, opt):
        if opt == glo_va.BUTTON_EXIST:
            ret = self.__OpenDialog(glo_va.EXIST_DIALOG)
            print(ret)
            if ret == 0:
                glo_va.button = glo_va.BUTTON_EXIST

        elif opt == glo_va.BUTTON_CONFIRM_PATIENT:
            if glo_va.STATE != glo_va.STATE_CONFIRM_PATIENT:
                return
            ret = self.__OpenDialog(glo_va.CONFIRM_PATIENT_DIALOG)
            if ret == -1:
                glo_va.button = glo_va.BUTTON_CANCEL_CONFIRM_PATIENT
            else:
                glo_va.button = glo_va.BUTTON_ACCEPT_CONFIRM_PATIENT

        elif opt == glo_va.BUTTON_VIEW_LIST_DEP:
            if glo_va.STATE != glo_va.STATE_MEASURE_SENSOR:
                return
            
            glo_va.button = glo_va.BUTTON_VIEW_LIST_DEP
            print('BUTTON_VIEW_LIST_DEP')

        elif opt == glo_va.BUTTON_CAPTURE_SENSOR:
            if glo_va.STATE != glo_va.STATE_MEASURE_SENSOR:
                return
            
            glo_va.button = glo_va.BUTTON_CAPTURE_SENSOR
            print('BUTTON_CAPTURE_SENSOR')
            
        elif opt == glo_va.BUTTON_SUBMIT_EXAM:
            if glo_va.STATE != glo_va.STATE_MEASURE_SENSOR:
                return
            
            glo_va.button = glo_va.BUTTON_SUBMIT_EXAM
        
        elif opt == glo_va.BUTTON_CONFIRM_DEP:
            if glo_va.STATE != glo_va.STATE_VIEW_DEPARTMENTS:
                return
            index = self.table_list_department.currentRow()
            if index != -1:
                self.__ConfirmExamRoom(index)

    # def __submitExamination(self):

    def __notificationDialog(self, message):
        self.submit_dialog = OkDialogClass(-2, message)
        self.submit_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if self.submit_dialog.exec_() == QtWidgets.QDialog.Accepted:
            glo_va.button = glo_va.BUTTON_OKAY

    def __OpenDialog(self, opt):
        ret = None
        if opt == glo_va.EXIST_DIALOG:
            text = 'Are you sure to quit?'
        elif opt == glo_va.CONFIRM_PATIENT_DIALOG:
            text = 'Is it your information?'
        elif opt == glo_va.CONFIRM_NEW_PATIENT_DIALOG:
            text = 'Are you new user?'

        dialog = QDialogClass(ret, text)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            return int(dialog.ret)
    
    def __SetBackgroudMainFrame(self, opt):
        if opt == 0:
            # White background
            self.main_frame.setStyleSheet('background-color: rgb(255,255,255);')
        elif opt == 1:
            # black background
            self.main_frame.setStyleSheet('background-color: rgb(0,0,0);')

    def __CheckRequestStatesThread(self):
        if self.queue_request_states_thread.empty():
            return
        
        request = self.queue_request_states_thread.get()

        if request['type'] == glo_va.REQUEST_CONFIRM_NEW_PATIENT:
            ret = self.__OpenDialog(glo_va.CONFIRM_NEW_PATIENT_DIALOG)
            print(ret)
            if ret == 0:
                glo_va.button = glo_va.BUTTON_ACCEPT_NEW_PATIENT
            else:
                glo_va.button = glo_va.BUTTON_DENY_NEW_PATIENT

        elif request['type'] == glo_va.REQUEST_CHANGE_GUI:
            self.__ChangeUI()

        elif request['type'] == glo_va.REQUEST_UPDATE_PATIENT_INFO:
            info = request['data']
            self.__UpdatePatientInfo(info)

        elif request['type'] == glo_va.REQUEST_CLEAR_PATIENT_INFO:
            self.__ClearPatientInfo()
        
        elif request['type'] == glo_va.REQUEST_ACTIVATE_NEW_FACE:
            current_shape = request['data']
            self.__ActivateFaceRecored(current_shape)
        
        elif request['type'] == glo_va.REQUEST_UPDATE_SENSOR:
            self.__UpdateSensorInfo()
        
        elif request['type'] == glo_va.REQUEST_CLEAR_SENSOR:
            self.__ClearSensorInfo()
        
        elif request['type'] == glo_va.REQUEST_CLEAR_EXAM_ROOM:
            self.__ClearExamRoom()
        
        elif request['type'] == glo_va.REQUEST_CLEAR_DEPARTMENT_LIST:
            self.__ClearListDepartments()
        
        elif request['type'] == glo_va.REQUEST_MEASURE_SENSOR:
            self.__MeasureSensor()

        elif request['type'] == glo_va.REQUEST_NOTIFY_MESSAGE:
            message = request['data']
            self.__notificationDialog(message)

        return

    def __Convert_To_Display(self, img):
        # Get ndarray and return QImage
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = QImage(img, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888)
        qp_image = QPixmap(image)

        return qp_image
    
    def __MeasureSensor(self):
        ret = -2
        progress_bar = ProgressBarDialogClass(ret)
        progress_bar.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if progress_bar.exec_() == QtWidgets.QDialog.Accepted:
            ret = int(progress_bar.ret)
            # print(ret)
        
        if ret == 0:
            sensor_info = {'blood_pressure': 120, 'heart_pulse':98, 'temperature':38, 'spo2':90, 'height': 1.78, 'weight': 78}
            sensor.Update_Sensor(sensor_info)
            self.__UpdateSensorInfo()

        glo_va.done_measuring_sensor = True
    
    def __UpdateImage(self):
        if self.image_display is None:
            return

        qp_image = self.__Convert_To_Display(self.image_display)

        if glo_va.STATE == glo_va.STATE_NEW_PATIENT:
            self.img_new_user.setPixmap(qp_image)
        elif glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT:
            self.image_patient.setPixmap(qp_image)
    
    def __UpdatePatientInfo(self, infor):
        self.patient_name.setText(infor['name'])
        self.patient_birthday.setText(infor['birthday'])
        self.patient_phone.setText(infor['phone'])
    
    def __ClearPatientInfo(self):
        self.patient_name.setText('')
        self.patient_birthday.setText('')
        self.patient_phone.setText('')
    
    def __UpdateSensorInfo(self):
        sensor_infor = sensor.sensor_infor
        # print(sensor_infor)

        self.height.setText(str(sensor_infor['height']) + ' m')
        self.weight.setText(str(sensor_infor['weight'])+ ' kg')
        self.spo2.setText(str(sensor_infor['spo2']))
        self.temperature.setText(str(sensor_infor['temperature'])+ ' C')
        self.heart_pulse.setText(str(sensor_infor['heart_pulse']))
        self.blood_pressure.setText(str(sensor_infor['blood_pressure']))
    
    def __ClearSensorInfo(self):
        self.blood_pressure.setText('')
        self.heart_pulse.setText('')
        self.temperature.setText('')
        self.spo2.setText('')
        self.weight.setText('')
        self.height.setText('')
    
    def __ConfirmExamRoom(self, index):
        dep = glo_va.list_examination_room[index]
        exam.Update_Examination(dep)
        self.__UpdateExamRoom()
    
    def __UpdateExamRoom(self):
        dep_name, building, room = exam.Get_Exam_Room_Infor()
        temp = dep_name.split(' ')
        ret_dep = ""
        for i in range(len(temp)):
            if i % 2 == 0 and i != 0:
                ret_dep += '\n'
            else:
                ret_dep += ' '
            ret_dep += temp[i]

        self.building_code.setText(building)
        self.room_code.setText(room)
        self.dep_name.setText(ret_dep)
    
    def __ClearExamRoom(self):
        self.building_code.setText('')
        self.room_code.setText('')
        self.dep_name.setText('')

    def __ChangeUI(self):
        if glo_va.STATE == glo_va.STATE_NEW_PATIENT:
            self.__SetBackgroudMainFrame(1)
            self.stackedWidget.setCurrentWidget(self.add_new_patient_frame)
        elif glo_va.STATE == glo_va.STATE_MEASURE_SENSOR:
            self.__SetBackgroudMainFrame(0)
            self.stackedWidget.setCurrentWidget(self.measure_sensor_frame)
        elif glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT:
            self.__SetBackgroudMainFrame(0)
            self.stackedWidget.setCurrentWidget(self.recognize_frame)
        elif glo_va.STATE == glo_va.STATE_VIEW_DEPARTMENTS:
            self.__UpdateListDepartments()
            self.__SetBackgroudMainFrame(1)
            self.stackedWidget.setCurrentWidget(self.view_departments)
        
        self.image_display = None
    
    def __UpdateListDepartments(self):
        count = 0
        for dep in glo_va.list_examination_room:
            room = dep['building_code'] + '-' + dep['room_code']
            dep_name = dep['dep_name']
            self.table_list_department.setItem(count, 0, QTableWidgetItem(room))
            self.table_list_department.setItem(count, 1, QTableWidgetItem(dep_name))
            count += 1
    
    def __ClearListDepartments(self):
        count = 0
        for dep in glo_va.list_examination_room:
            self.table_list_department.setItem(count, 0, QTableWidgetItem(''))
            self.table_list_department.setItem(count, 1, QTableWidgetItem(''))
            count += 1

    def __ActivateFaceRecored(self, direction):
        self.list_shape_face[direction].setStyleSheet('''
            QLabel {
                border-radius: 30px;
                background-color: rgb(255, 155, 54);
                border: 5px solid rgb(255, 168, 75);
                background-position: center;
                background-repeat: no-repeat;
            }
        ''')


app = QtWidgets.QApplication(sys.argv)
gui = GUI()
gui.show()
app.exec_()