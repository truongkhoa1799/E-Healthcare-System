from utils.common_functions import LogMesssage
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import sys, time, threading, queue

sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')

import queue
from utils.parameters import *

class MomoGuiDialog(QDialog, glo_va.momo_gui_dialog):
    def __init__(self, ret, parent=None):
        QDialog.__init__(self, parent)
        # uic.loadUi(glo_va.OKAY_DIALOG_PATH, self) # Load the .ui file
        self.ret = ""
        self.text = None
        self.setupUi(self)

        self.confirm_symptoms.clicked.connect(lambda: self.__onButtonListenning())

        self.queue_request_states_thread = queue.Queue(maxsize = 10)
        check_request_states_thread = QTimer(self)
        check_request_states_thread.timeout.connect(self.__CheckRequestStatesThread)
        check_request_states_thread.start(10)
        # self.__updateConversation('Vậy bạn có thể cho Momo biết bạn bị đau hoặc cảm thấy khó chịu ở chỗ nào được không? Để Momo có thể giúp bạn tìm khoa phù hợp', 0)
    
    def __CheckRequestStatesThread(self):
        if self.queue_request_states_thread.empty():
            return
        
        request = self.queue_request_states_thread.get()

        if request['type'] == glo_va.REQUEST_UPDATE_DEP_MOMO_GUI:
            dep_name = request['data']
            self.__updateDepartmentName(dep_name)
        elif request['type'] == glo_va.REQUEST_UPDATE_CONVERSATION_MOMO_GUI:
            data = request['data']
            text = data['text']
            opt = int(data['opt'])
            self.__updateConversation(text, opt)
            
    def __updateDepartmentName(self, dep_name):
        self.department_predicted.setText(dep_name)

    def __onButtonListenning(self):
        self.ret = self.department_predicted.text()
        self.accept()
        self.close()
    
    def __updateConversation(self, text, opt):
        # patient conversation
        ret_text = self.__extractConversation(text)
        if opt == 0:
            # print(ret_text)
            self.patient_conversation.setText(ret_text)
        else:
            self.momo_conversation.setText(ret_text)

    def __extractConversation(self, text):
        list_text = text.split(' ')
        num_text_one_line = 32
        ret_text = ""
        current_len = 0

        for i in range(len(list_text)):
            # print(current_len)
            if list_text[i] != '':
                if current_len + len(list_text[i]) > num_text_one_line:
                    ret_text += "\n"
                    current_len = len(list_text[i])
                else:
                    if len(ret_text) != 0: ret_text += " "
                    current_len += len(list_text[i]) + 1
                
                ret_text += list_text[i]

        return ret_text

    
    def closeEvent(self, event):
        if self.ret == "":
            self.ret = ""
            self.accept()
