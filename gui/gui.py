from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import cv2
import sys
# from utils.parameters import *

# TestQDialog = uic.loadUiType("gui/dialog.ui")[0]
TestQDialog = uic.loadUiType("dialog.ui")[0]

class QDialogClass(QDialog, TestQDialog):
    def __init__(self, ret, text, parent=None):
        QDialog.__init__(self, parent)
        self.ret = ret
        self.text = text
        self.setupUi(self)

        self.text_dialog.setText(text)
        self.accept_exist.clicked.connect(self.__OnAcceptListenning)
        self.deny_exist.clicked.connect(self.__OnDenyCancelListenning)
    
    def __OnAcceptListenning(self):
        # print("exist")
        self.ret = 0
        self.accept()
        self.close()
    
    def __OnDenyCancelListenning(self):
        # print("deny exist")
        self.ret = -1
        self.accept()
        self.close()
    

class GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(GUI, self).__init__() # Call the inherited classes __init__ method
        # uic.loadUi('gui/form.ui', self) # Load the .ui file
        uic.loadUi('form.ui', self) # Load the .ui file
        
        # register listenning button
        # Button recognize state
        self.confirm_user_but.clicked.connect(self.__OnConfirmInforListenning)

        # Button measure sensor state
        self.capture_sensor_but.clicked.connect(self.__OnCaptureSensorListenning)
        self.submit_exam_but.clicked.connect(self.__OnSubmitExamListenning)
        self.view_dep_list.clicked.connect(self.__OnChooseDepListenning)

        # Exist state
        # opt = 0: exist
        self.exist_but.clicked.connect(self.__OneExistListenning, 0)

        # All frame of gui
        self.stackedWidget.addWidget(self.recognize_frame)
        self.stackedWidget.addWidget(self.measure_sensor_frame)
        self.stackedWidget.addWidget(self.add_new_patient_frame)
        self.stackedWidget.addWidget(self.page)
        
        self.stackedWidget.setCurrentWidget(self.recognize_frame)
        # Fix header table widget
        self.table_list_department.horizontalHeader().setSectionResizeMode(2)

        self.image_display = None
        self.image_new_user = None
        timer = QTimer(self)
        timer.timeout.connect(self.__UpdateImage)
        timer.start(33)

        self.list_shape_face = [self.up_face, self.down_face, self.left_face, self.right_face, self.front_face]

        img = cv2.imread('/Users/khoa1799/GitHub/E-Healthcare-System-Server/Manipulate_Data/Original_Face/train/1/IMG_3415.jpg')
        img = cv2.resize(img, (430,400))
        qp_image = self.__Convert_To_Display(img)
        self.image_patient.setPixmap(qp_image)

    def __OnConfirmInforListenning(self):
        # opt = 1: confirm user
        if glo_va.STATE == glo_va.STATE_CONFIRM_PATIENT:
            ret = self.__OpenDialog(opt = 1)
            if ret == -1:
                glo_va.button = glo_va.BUTTON_CANCEL_CONFIRM_PATIENT
            else:
                glo_va.button = glo_va.BUTTON_ACCEPT_CONFIRM_PATIENT
    
    def __OneExistListenning(self):
        # opt = 1: confirm user
        ret = self.__OpenDialog(opt = 0)
        if ret == 0:
            print('GUI: exist button clicked')
            glo_va.button = glo_va.BUTTON_EXIST

    def __OnCaptureSensorListenning(self):
        print("Hello")
        
    def __OnSubmitExamListenning(self):
        print("Hello")

    def __OnChooseDepListenning(self):
        self.stackedWidget.setCurrentWidget(self.choose_deparment_frame)
    
    def __OpenDialog(self, opt):
        ret = None
        if opt == 0:
            text = 'Are you sure to quit?'
        elif opt == 1:
            text = 'Is it your information?'
        elif opt == 2:
            text = 'Are you new user?'

        dialog = QDialogClass(ret, text)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            return int(dialog.ret)
    
    def IsNewUser(self):
        ret = self.__OpenDialog(opt = 2)
        return ret
        
    def __Convert_To_Display(self, img):
        # Get ndarray and return QImage
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = QImage(img, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888)
        qp_image = QPixmap(image)

        return qp_image
    
    def __UpdateImage(self):
        if self.image_display is None:
            return

        qp_image = self.__Convert_To_Display(self.image_display)

        if glo_va.STATE == glo_va.STATE_NEW_PATIENT:
            self.img_new_user.setPixmap(qp_image)
        elif glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT:
            self.image_patient.setPixmap(qp_image)
    
    def UpdatePatientInfo(self, infor):
        self.patient_name.setText(infor['name'])
        self.patient_birthday.setText(infor['birthday'])
        self.patient_phone.setText(infor['phone'])
    
    def ClearPatientInfo(self):
        self.patient_name.setText('')
        self.patient_birthday.setText('')
        self.patient_phone.setText('')
    
    def UpdateSensorInfo(self, sensor):
        self.patient_name.setText(sensor['height'])
        self.patient_name.setText(sensor['weight'])
        self.patient_name.setText(sensor['spo2'])
        self.patient_name.setText(sensor['temperature'])
        self.patient_name.setText(sensor['heart_pulse'])
        self.patient_name.setText(sensor['blood_pressure'])
    
    def ClearSensorInfo(self):
        self.patient_name.setText('')
        self.patient_name.setText('')
        self.patient_name.setText('')
        self.patient_name.setText('')
        self.patient_name.setText('')
        self.patient_name.setText('')
    
    def UpdateExamRoom(self, exam_room):
        self.patient_name.setText(exam_room['building_code'])
        self.patient_name.setText(exam_room['room_code'])
        temp_dep_name = exam_room['dep_name'].strip()
        temp_dep_name_list = temp_dep_name.split(' ')
        dep_name = ""
        for i in range(len(temp_dep_name_list)):
            if i%2 == 0:
                dep_name += '\n'
            
            dep_name += temp_dep_name_list[i]
        
        self.patient_name.setText(dep_name)
    
    def ClearExamRoom(self):
        self.patient_name.setText('')
        self.patient_name.setText('')
        self.patient_name.setText('')

    def ChangeUI(self):
        if glo_va.STATE == glo_va.STATE_NEW_PATIENT:
            self.stackedWidget.setCurrentWidget(self.add_new_patient_frame)
        elif glo_va.STATE == glo_va.STATE_MEASURE_SENSOR:
            self.stackedWidget.setCurrentWidget(self.measure_sensor_frame)
        elif glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT:
            self.stackedWidget.setCurrentWidget(self.recognize_frame)
        
        self.image_display = None

    def ActivateFaceRecored(self, direction):
        self.list_shape_face[direction].setStyleSheet('''
            QLabel {
                border-radius: 38px;
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