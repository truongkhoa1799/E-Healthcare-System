from utils.common_functions import LogMesssage
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import sys, time, threading, queue

sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')

from utils.parameters import *

class QDialogClass(QDialog, glo_va.yes_no_dialog):
    def __init__(self, ret, opt, parent=None):
        QDialog.__init__(self, parent)
        # uic.loadUi(glo_va.YES_NO_DIALOG_PATH, self) # Load the .ui file
        self.ret = -2
        self.text = None
        self.setupUi(self)

        if opt == glo_va.EXIST_DIALOG:
            self.text = 'Are you sure to quit?'
        elif opt == glo_va.CONFIRM_PATIENT_DIALOG:
            self.text = 'Is it your information?'
        elif opt == glo_va.CONFIRM_NEW_PATIENT_DIALOG:
            self.text = 'Are you new user?'
        elif opt == glo_va.CONFIRM_SENSOR_INFORMATION:
            self.text = 'Are you sure about these sensor'

        self.text_dialog.setText(self.text)
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