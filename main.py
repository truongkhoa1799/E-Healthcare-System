from identifying_users.states import *
from identifying_users.init import Init
from identifying_users.end import End

from gui.gui import GUI
from PyQt5 import QtWidgets

from utils.parameters import *

import pycuda.driver as cuda

import sys, threading
from signal import signal, SIGINT

from identifying_users.face_detector_centerface import FaceDetector

def EndProcHandler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    try:
        glo_va.stop_program.set()
        glo_va.main_thread.join()

    except:
        pass

    End()

def main():
    LogMesssage('Start init Center Face', opt=0)
    cuda_ctx = cuda.Device(0).make_context()
    glo_va.centerface_detector = FaceDetector()

    while not glo_va.stop_program.is_set():
        while not glo_va.start_program.is_set():
            continue
        
        try:
            # STATE DETECTING AND RECOGNIZING PATIENT
            if glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT:
                State_1()

            # STATE CONFIRMING PATIENT INFORMATION
            elif glo_va.STATE == glo_va.STATE_CONFIRM_PATIENT:
                State_2()

            # STATE MEASURING PATIENT' BIOLOGICAL PARAMETERS
            elif glo_va.STATE == glo_va.STATE_MEASURE_SENSOR:
                State_3()

            # STATE CLASSIFYING ROOM
            elif glo_va.STATE == glo_va.STATE_VIEW_DEPARTMENTS:
                State_4()

            # STATE CONFIRM NEW USER
            elif glo_va.STATE == glo_va.STATE_CONFIRM_NEW_PATIENT:
                State_5()
            
            # STATE FOR NEW USER
            elif glo_va.STATE == glo_va.STATE_NEW_PATIENT:
                State_6()
            
            elif glo_va.STATE == glo_va.STATE_WAITING_SUB_EXAM:
                State_7()
            
            elif glo_va.STATE == glo_va.STATE_MEASURING_SENSOR:
                State_8()

        except Exception as e:
            print("Error at module main in main: {}".format(e))
            
            cuda_ctx.pop()
            del cuda_ctx
            LogMesssage('Stop Center Face', opt=0)

            # clear all services
            End()
            exit(0)

    cuda_ctx.pop()
    del cuda_ctx
    LogMesssage('Stop Center Face', opt=0)

def Init_Gui():
    app = QtWidgets.QApplication(sys.argv)
    glo_va.gui = GUI()
    glo_va.gui.show()
    glo_va.flg_init_GUI = True
    glo_va.start_program.set()
    app.exec_()
    
#########################################################################
# Main FUNCTION                                                         #
#########################################################################

if __name__ == "__main__":
    signal(SIGINT, EndProcHandler)
    # while True:
    try:
        ret = Init()
        if ret == -1:
            End()
            exit(0)
            
        glo_va.main_thread = threading.Thread(target=main, args=())
        glo_va.main_thread.daemon = True
        glo_va.main_thread.start()

        Init_Gui()
    except Exception as e:
        print("Error at Init module: {}".format(e))
        try:
            glo_va.stop_program.set()
            glo_va.main_thread.join()
        except:
            pass
        End()
        exit(0)