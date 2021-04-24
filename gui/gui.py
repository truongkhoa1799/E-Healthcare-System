from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import sys, time

# sys.path.append('/home/thesis/Documents/thesis/E-Healthcare-System')
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')

from utils.parameters import *
from utils.common_functions import LogMesssage, Convert_To_Display

from gui.momo_gui import MomoGuiDialog
from gui.ok_dialog import OkDialogClass
from gui.yes_no_dialog import QDialogClass

# from momo_gui import MomoGuiDialog
# from ok_dialog import OkDialogClass
# from yes_no_dialog import QDialogClass

import queue

class GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(GUI, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi(glo_va.MAIN_GUI_PATH, self) # Load the .ui file
        
        # register listenning button
        self.exist_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_EXIST))
        self.confirm_user_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_CONFIRM_PATIENT))
        self.view_dep_list.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_VIEW_LIST_DEP))
        self.confirm_dep_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_CONFIRM_DEP))
        self.capture_sensor_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_CAPTURE_SENSOR))
        self.submit_exam_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_SUBMIT_EXAM))
        self.select_dep_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_SELECT_DEP))
        self.diagnose_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_DIAGNOSE_SYMPTOMS))

        # All frame of gui
        self.stackedWidget.addWidget(self.recognize_frame)
        self.stackedWidget.addWidget(self.measure_sensor_frame)
        self.stackedWidget.addWidget(self.add_new_patient_frame)
        self.stackedWidget.addWidget(self.view_departments)
        self.stackedWidget.addWidget(self.measuring_sensor_frame)
        
        self.stackedWidget.setCurrentWidget(self.recognize_frame)
        # Fix header table widget
        self.table_list_department.horizontalHeader().setSectionResizeMode(2)

        # # Show full screen
        # self.showFullScreen()
        # # Hide currsor
        # self.setCursor(QtCore.Qt.BlankCursor)

        self.queue_request_states_thread = queue.Queue(maxsize = 10)
        check_request_states_thread = QTimer(self)
        check_request_states_thread.timeout.connect(self.__CheckRequestStatesThread)
        check_request_states_thread.start(10)

        self.image_display = None
        self.image_new_user = None
        update_image_timer = QTimer(self)
        update_image_timer.timeout.connect(self.__UpdateImage)
        update_image_timer.start(33)

        # test = QTimer(self)
        # test.timeout.connect(self.__test)
        # test.start(3000)

        self.list_shape_face = [self.front_face, self.up_face, self.down_face, self.left_face, self.right_face]
        self.__map_department = None
        self.__list_department = None

        ########################################################
        # MEASURING SENSOR FRAME                               #
        ########################################################
        self.index_instruction = 0
        self.num_instruction = 3

        self.MAIN_FRAME = 0
        self.INSTRUCTION_FRAME = 1

        self.pre_instruction.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_BACK_GUILDE_SENSOR))
        self.next_instruction.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_NEXT_GUILDE_SENSOR))
        self.instruction_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_GUILDE_SENSOR))
        self.back_measuring_frame_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_QUIT_GUILDE_SENSOR))
        self.connect_device_sensor_but.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_CONNECT_DEVICE_SENSOR))
        self.confirm_measuring_sensor.clicked.connect(lambda: self.__onButtonsListenning(glo_va.BUTTON_CONFIRM_SENSOR))

        self.measure_sensor_stack.addWidget(self.measuring_frame)
        self.measure_sensor_stack.addWidget(self.guilde_frame)

        self.measure_sensor_stack.setCurrentWidget(self.measuring_frame)

        self.instruction_stack.addWidget(self.first_instruction)
        self.instruction_stack.addWidget(self.second_instruction)
        self.instruction_stack.addWidget(self.third_instruction)
        # 0: main frame
        # 1: instruction frame
        self.current_frame = self.MAIN_FRAME

        self.__list_image = [self.first_instruction, self.second_instruction, self.third_instruction]

        # self.__UpdateListDepartments()
        # self.__openMomoChatbotGui()
        

    def closeEvent(self, event):
        glo_va.flg_init_GUI = False
    
    ############################################################################
    # DIALOG MODULE                                                            #
    ############################################################################
    def __notificationDialog(self, data):
        self.submit_dialog = OkDialogClass(-2, data)
        self.submit_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if self.submit_dialog.exec_() == QtWidgets.QDialog.Accepted:
            glo_va.button = glo_va.BUTTON_OKAY

    def __OpenDialog(self, opt):
        ret = None

        dialog = QDialogClass(ret, opt)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            return int(dialog.ret)
    
    def __openMomoChatbotGui(self):
        ret = None

        dialog = MomoGuiDialog(ret)
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            ret = int(dialog.ret)
            glo_va.button = glo_va.BUTTON_CLOSE_MOMO_GUI
            return ret
        

    ############################################################################
    # CONTROL MODULE                                                            #
    ############################################################################
    def __onButtonsListenning(self, opt):
        if opt == glo_va.BUTTON_EXIST:
            ret = self.__OpenDialog(glo_va.EXIST_DIALOG)
            # print(ret)
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
            # print('BUTTON_VIEW_LIST_DEP')

        elif opt == glo_va.BUTTON_CAPTURE_SENSOR:
            if glo_va.STATE != glo_va.STATE_MEASURE_SENSOR:
                return
            
            glo_va.button = glo_va.BUTTON_CAPTURE_SENSOR
            # print('BUTTON_CAPTURE_SENSOR')
            
        elif opt == glo_va.BUTTON_SUBMIT_EXAM:
            if glo_va.STATE != glo_va.STATE_MEASURE_SENSOR:
                return
            
            glo_va.button = glo_va.BUTTON_SUBMIT_EXAM
        
        elif opt == glo_va.BUTTON_CONFIRM_DEP:
            if glo_va.STATE != glo_va.STATE_VIEW_DEPARTMENTS:
                return

            self.__ConfirmExamRoom()
            glo_va.button = glo_va.BUTTON_CONFIRM_DEP
        
        elif opt == glo_va.BUTTON_SELECT_DEP:
            if glo_va.STATE != glo_va.STATE_VIEW_DEPARTMENTS:
                return

            index = self.table_list_department.currentRow()
            if index != -1:
                dep_name = self.__list_department[index]
                self.__UpdateSelectedRoom(dep_name)
        
        elif opt == glo_va.BUTTON_DIAGNOSE_SYMPTOMS:
            if glo_va.STATE != glo_va.STATE_VIEW_DEPARTMENTS:
                return

            glo_va.button = glo_va.BUTTON_DIAGNOSE_SYMPTOMS

        ########################
        # Measuing frame       #
        ########################
        elif opt == glo_va.BUTTON_BACK_GUILDE_SENSOR:
            if glo_va.STATE != glo_va.STATE_MEASURING_SENSOR:
                return

            if self.index_instruction > 0:
                self.index_instruction -= 1
                # print(self.state)
                self.instruction_stack.setCurrentWidget(self.__list_image[self.index_instruction])

                message = 'measure_sensor_inform_{}'.format(str(self.index_instruction))
                # MOMO saying
                glo_va.momo_assis.Say(glo_va.momo_messages[message])

        elif opt == glo_va.BUTTON_NEXT_GUILDE_SENSOR:
            if glo_va.STATE != glo_va.STATE_MEASURING_SENSOR:
                return

            if self.index_instruction < self.num_instruction - 1:
                self.index_instruction += 1
                # print(self.state)
                self.instruction_stack.setCurrentWidget(self.__list_image[self.index_instruction])

                message = 'measure_sensor_inform_{}'.format(str(self.index_instruction))
                # MOMO saying
                glo_va.momo_assis.Say(glo_va.momo_messages[message])

        elif opt == glo_va.BUTTON_GUILDE_SENSOR:
            if glo_va.STATE != glo_va.STATE_MEASURING_SENSOR:
                return

            self.current_frame = self.INSTRUCTION_FRAME
            self.instruction_stack.setCurrentWidget(self.first_instruction)
            self.measure_sensor_stack.setCurrentWidget(self.guilde_frame)

            message = 'measure_sensor_inform_0'
            # MOMO saying
            glo_va.momo_assis.Say(glo_va.momo_messages[message])

            LogMesssage('Patient change to instruction measure sensor frame')
            
        elif opt == glo_va.BUTTON_QUIT_GUILDE_SENSOR:
            if glo_va.STATE != glo_va.STATE_MEASURING_SENSOR:
                return

            self.index_instruction = 0
            self.current_frame = self.MAIN_FRAME
            self.measure_sensor_stack.setCurrentWidget(self.measuring_frame)
            LogMesssage('Patient change to measure sensor frame')

        elif opt == glo_va.BUTTON_CONNECT_DEVICE_SENSOR:
            if glo_va.STATE != glo_va.STATE_MEASURING_SENSOR:
                return

            # self.__measureSenSor()
            glo_va.button = glo_va.BUTTON_CONNECT_DEVICE_SENSOR

        elif opt == glo_va.BUTTON_CONFIRM_SENSOR:
            if glo_va.STATE != glo_va.STATE_MEASURING_SENSOR:
                return

            # self.confirmSensor()
            glo_va.button = glo_va.BUTTON_CONFIRM_SENSOR

    def __CheckRequestStatesThread(self):
        if self.queue_request_states_thread.empty():
            return
        
        request = self.queue_request_states_thread.get()

        if request['type'] == glo_va.REQUEST_CONFIRM_NEW_PATIENT:
            ret = self.__OpenDialog(glo_va.CONFIRM_NEW_PATIENT_DIALOG)
            # print(ret)
            if ret == 0:
                glo_va.button = glo_va.BUTTON_ACCEPT_NEW_PATIENT
            else:
                glo_va.button = glo_va.BUTTON_DENY_NEW_PATIENT

        elif request['type'] == glo_va.REQUEST_CHANGE_GUI:
            self.__ChangeUI()

        elif request['type'] == glo_va.REQUEST_UPDATE_PATIENT_INFO:
            info = request['data']
            self.__UpdatePatientInfo(info)
        
        elif request['type'] == glo_va.REQUEST_ACTIVATE_NEW_FACE:
            current_shape = request['data']
            self.__ActivateFaceRecored(current_shape)
        
        elif request['type'] == glo_va.REQUEST_DEACTIVATE_NEW_FACE:
            self.__DeactivateFaceRecored()
        
        elif request['type'] == glo_va.REQUEST_UPDATE_SENSOR:
            self.__UpdateSensorInfo()
        
        elif request['type'] == glo_va.REQUEST_CLEAR_SENSOR:
            self.__ClearSensorInfo()
        
        elif request['type'] == glo_va.REQUEST_CLEAR_EXAM_ROOM:
            self.__ClearExamRoom()
        
        elif request['type'] == glo_va.REQUEST_CLEAR_DEPARTMENT_LIST:
            self.__ClearListDepartments()

        elif request['type'] == glo_va.REQUEST_NOTIFY_MESSAGE:
            data = request['data']
            self.__notificationDialog(data)
        
        elif request['type'] == glo_va.REQUEST_CLEAR_SELECTED_EXAM_ROOM:
            self.__ClearSelectedRoom()
        
        elif request['type'] == glo_va.REQUEST_UPDATE_SELECTED_EXAM_ROOM:
            dep_name = request['data']
            self.__UpdateSelectedRoom(dep_name=dep_name)
        
        elif request['type'] == glo_va.REQUEST_OPEN_MOMO_GUI:
            self.__openMomoChatbotGui()
        
        ########################
        # Measuing frame       #
        ########################
        elif request['type'] == glo_va.REQUEST_UPDATE_OSO2:
            if self.current_frame != self.MAIN_FRAME:
                LogMesssage('Discard request message: {}'.format(request['type'] == glo_va.REQUEST_UPDATE_OSO2))
                return

            # print(request['data'])
            if request['data']['final'] == 0:
                if glo_va.measuring_sensor.has_oso2 and glo_va.measuring_sensor.has_esp:
                    self.progress_bar.setValue(100)
                elif glo_va.measuring_sensor.has_oso2 or glo_va.measuring_sensor.has_esp:
                    self.progress_bar.setValue(50)
                else:
                    self.progress_bar.setValue(0)
                
                self.spo2.setText(str(int(request['data']['spo2'])))
                self.heart_pulse.setText(str(int(request['data']['heart_pulse'])))
                    
            self.measuring_heart_pulse.setText(str(int(request['data']['heart_pulse'])))
            self.measuring_spo2.setText(str(int(request['data']['spo2'])))
        
        elif request['type'] == glo_va.REQUEST_UPDATE_ESP:
            self.measuring_height.setText(request['data']['height'])
            self.measuring_weight.setText(request['data']['weight'])
            self.measuring_temperature.setText(request['data']['temperature'])
            self.measuring_BMI.setText(request['data']['bmi'])
            
            self.height.setText(request['data']['height'])
            self.weight.setText(request['data']['weight'])
            self.temperature.setText(request['data']['temperature'])
            self.bmi.setText(request['data']['bmi'])

            if glo_va.measuring_sensor.has_oso2 and glo_va.measuring_sensor.has_esp:
                self.progress_bar.setValue(100)
            elif glo_va.measuring_sensor.has_oso2 or glo_va.measuring_sensor.has_esp:
                self.progress_bar.setValue(50)
            else:
                self.progress_bar.setValue(0)

        return
    
    def __ChangeUI(self):
        if glo_va.STATE == glo_va.STATE_NEW_PATIENT:
            # self.__SetBackgroudMainFrame(1)
            self.stackedWidget.setCurrentWidget(self.add_new_patient_frame)
        elif glo_va.STATE == glo_va.STATE_MEASURE_SENSOR:
            # self.__SetBackgroudMainFrame(0)
            self.stackedWidget.setCurrentWidget(self.measure_sensor_frame)
        elif glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT:
            # self.__SetBackgroudMainFrame(1)
            self.__ClearPatientInfo()
            self.stackedWidget.setCurrentWidget(self.recognize_frame)
        elif glo_va.STATE == glo_va.STATE_VIEW_DEPARTMENTS:
            self.__UpdateListDepartments()
            # self.__SetBackgroudMainFrame(0)
            self.stackedWidget.setCurrentWidget(self.view_departments)
        elif glo_va.STATE == glo_va.STATE_MEASURING_SENSOR:
            # self.__SetBackgroudMainFrame(1)
            self.__clearMeasuringSensorsFrame()
            self.stackedWidget.setCurrentWidget(self.measuring_sensor_frame)
        
        self.image_display = None
    
    def __ActivateFaceRecored(self, direction):
        self.list_shape_face[direction].setStyleSheet('''
            QLabel {
                border-radius: 45px;
                background-color: rgb(255, 155, 54);
                border: 5px solid rgb(255, 168, 75);
                background-position: center;
                background-repeat: no-repeat;
            }
        ''')

    def __DeactivateFaceRecored(self):
        for shape in self.list_shape_face:
            shape.setStyleSheet('''
                QLabel {
                    border-radius: 45px;
                    background-color: rgb(44, 49, 60);
                    border: 5px solid rgb(39, 44, 54);
                    background-position: center;
                    background-repeat: no-repeat;
                }
            ''')

    ############################################################################
    # SENSOR MODULE                                                            #
    ############################################################################
    # def __MeasureSensor(self):
    #     ret = {}
    #     glo_va.measure_sensor_dialog = MeasureSensorDialog(ret)
    #     glo_va.measure_sensor_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    #     if glo_va.measure_sensor_dialog.exec_() == QtWidgets.QDialog.Accepted:
    #         ret = glo_va.measure_sensor_dialog.ret
    #         print(ret)
        
    #     self.__UpdateSensorInfo()
    
    def __ClearSensorInfo(self):
        self.bmi.setText('')
        self.heart_pulse.setText('')
        self.temperature.setText('')
        self.spo2.setText('')
        self.weight.setText('')
        self.height.setText('')
    
    ############################################################################
    # PATIENT MODULE                                                           #
    ############################################################################
    def __UpdateImage(self):
        if self.image_display is None:
            return

        qp_image = Convert_To_Display(self.image_display)

        if glo_va.STATE == glo_va.STATE_NEW_PATIENT:
            self.img_new_user.setPixmap(qp_image)
        elif glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT:
            self.image_patient.setPixmap(qp_image)
    
    def __UpdatePatientInfo(self, infor):
        self.patient_name.setText(infor['name'])
        self.patient_birthday.setText(infor['birthday'])
        self.patient_phone.setText(infor['phone'])
        self.patient_address.setText(infor['address'])
    
    def __ClearPatientInfo(self):
        self.patient_name.setText('')
        self.patient_birthday.setText('')
        self.patient_phone.setText('')
        self.patient_address.setText('')

    ############################################################################
    # EXAM ROOM MODULE                                                         #
    ############################################################################    
    def __ConfirmExamRoom(self):
        dep_name = str(self.selected_dep.text())
        room_code = str(self.selected_room.text())
        if dep_name == '' or room_code == '':
            return

        exam.Update_Examination(dep_name, room_code)
        self.__UpdateExamRoom()
    
    def __UpdateExamRoom(self):
        dep_name, building, room = exam.Get_Exam_Room_Infor()

        self.building_code.setText(building)
        self.room_code.setText(room)
        self.dep_name.setText(dep_name)
    
    def __ClearExamRoom(self):
        self.building_code.setText('')
        self.room_code.setText('')
        self.dep_name.setText('')
    
    def __UpdateSelectedRoom(self, dep_name):
        list_rooms = self.__map_department[dep_name]
        min_patients = 100
        building_code = None
        room_code = None

        for i in list_rooms:
            if i['num_patients'] < min_patients:
                room_code = i['room_code']
                building_code = i['building_code']

        self.selected_dep.setText(dep_name)
        self.selected_room.setText('{}-{}'.format(building_code, room_code))
    
    def __ClearSelectedRoom(self):
        self.selected_dep.setText('')
        self.selected_room.setText('')
    
    def __UpdateListDepartments(self):
        count = 0
        self.__map_department = {}
        self.__list_department = []
        for dep in list_exam_rooms.list_examination_room:
            dep_name = dep['dep_name']

            if dep_name in self.__map_department:
                self.__map_department[dep_name].append(dep)
            else:
                self.__map_department[dep_name] = [dep]
                self.__list_department.append(dep_name)

                self.table_list_department.setItem(count, 0, QTableWidgetItem(str(count + 1)))
                self.table_list_department.setItem(count, 1, QTableWidgetItem(dep_name))
                count += 1
        
        # print(self.__map_department)
    
    def __ClearListDepartments(self):
        for count in range(len(list_exam_rooms.list_examination_room)):
            self.table_list_department.setItem(count, 0, QTableWidgetItem(''))
            self.table_list_department.setItem(count, 1, QTableWidgetItem(''))
    
    def __clearMeasuringSensorsFrame(self):
        self.measuring_temperature.setText('')
        self.measuring_height.setText('')
        self.measuring_weight.setText('')
        self.measuring_BMI.setText('')
        self.measuring_heart_pulse.setText('')
        self.measuring_spo2.setText('')
        self.progress_bar.setValue(0)


# app = QtWidgets.QApplication(sys.argv)
# gui = GUI()
# gui.show()
# app.exec_()