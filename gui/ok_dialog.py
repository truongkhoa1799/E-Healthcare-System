from utils.common_functions import LogMesssage
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
import sys, time, threading, queue

sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')

from utils.parameters import *

class OkDialogClass(QDialog):
    def __init__(self, ret, data, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(glo_va.OKAY_DIALOG_PATH, self) # Load the .ui file
        self.ret = -2
        self.text = None
        # self.setupUi(self)

        # submit success
        if data['opt'] == 0:
            self.icon.setStyleSheet('''background: transparent;
                background-image: url(icons/icons8-checkmark-90.png);
                background-position: center;
                background-repeat: no-repeat;
            ''')
            self.text = '             Your STT     : {}        \n             At Room      : {}'.format(data['stt'], data['room'])
        # fail to submit
        elif data['opt'] == 1:
            self.icon.setStyleSheet('''background: transparent;
                background-image: url(icons/warning.png);
                background-position: center;
                background-repeat: no-repeat;
            ''')
            self.text = '    False to submit examination.\n                Please try again.'
        # ask capture sensor
        elif data['opt'] == 2:
            self.icon.setStyleSheet('''background: transparent;
                background-image: url(icons/warning.png);
                background-position: center;
                background-repeat: no-repeat;
            ''')
            self.text = '  Please capture sensor information\nand select examination department'
        
        # Ask patient must have enought sensor information
        elif data['opt'] == 3:
            self.icon.setStyleSheet('''background: transparent;
                background-image: url(icons/warning.png);
                background-position: center;
                background-repeat: no-repeat;
            ''')
            self.text = '       Please turn on OSO2 device\n                or see instruction'
        
        if data['opt'] == 4:
            self.icon.setStyleSheet('''background: transparent;
                background-image: url(icons/icons8-checkmark-90.png);
                background-position: center;
                background-repeat: no-repeat;
            ''')
            self.text = '    You connect sensor successfully'
        

        self.text_dialog.setText(self.text)
        self.accept_exist.clicked.connect(lambda: self.__onButtonListenning())
    
    def __onButtonListenning(self):
        self.ret = 0
        self.accept()
        self.close()
    
    def closeEvent(self, event):
        if self.ret == -2:
            self.ret = -1
            self.accept()