from identifying_users.states import *
from identifying_users.init import Init
from identifying_users.end import End

from gui.gui import GUI
from PyQt5 import QtWidgets

from utils.parameters import *

import sys, threading
from signal import signal, SIGINT

def EndProcHandler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    End()

def main():
    while glo_va.ENABLE_PROGRAM_RUN:
        if glo_va.START_RUN == False:
            continue
        
        try:
            if glo_va.STATE == -1:
                End()

            # STATE DETECTING AND RECOGNIZING PATIENT
            elif glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT:
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
            End()
            return
        except KeyboardInterrupt:
            print('Interrupted')
            End()
            return

def Init_Gui():
    app = QtWidgets.QApplication(sys.argv)
    glo_va.gui = GUI()
    glo_va.gui.show()
    glo_va.flg_init_GUI = True
    glo_va.START_RUN = True
    app.exec_()
    
#########################################################################
# Main FUNCTION                                                         #
#########################################################################

if __name__ == "__main__":
    signal(SIGINT, EndProcHandler)
    try:
        Init()
        glo_va.main_thread = threading.Thread(target=main, args=())
        glo_va.main_thread.daemon = True
        glo_va.main_thread.start()

        Init_Gui()
    except Exception as e:
        print("Error at Init module: {}".format(e))

    End()
    exit(0)