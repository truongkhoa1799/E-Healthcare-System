# from identifying_users.face_detector_CenterFace import FaceDetector
from identifying_users.face_recognition import Face_Recognition
from identifying_users.camera_detecting import CameraDetecting
from identifying_users.count_face import CountFace
from communicate_server.server import Server
from utils.timer import Timer

from gui.gui import GUI
from PyQt5 import QtWidgets

import threading

from utils.parameters import *
from identifying_users.identifying_users_functions import *
from states import *

# import time
import cv2
from threading import Lock
#########################################################################
# START FUNCTIONS                                                       #
#########################################################################
def Start_Face_Recognition():
    print("Starting init Face Recognition")
    glo_va.face_recognition = Face_Recognition()

    time.sleep(0.5)
    print("Done start init Face Encoder")
    print()

def Start_Camera_Detecting():
    print("Starting init Camera")
    glo_va.camera = CameraDetecting()

    time.sleep(0.5)
    print("Done start init Camera")
    print()

def Start_Count_Face():
    print("Starting Init CountFace")
    glo_va.count_face = CountFace()
    time.sleep(0.5)
    print("Done start CountFace")
    print()

def Start_Timer():
    print("Starting Init Timer")
    glo_va.timer = Timer()
    time.sleep(0.5)
    print("Done start Timer")
    print()

def Start_GUI():
    print("Starting Init GUI")
    glo_va.window_GUI = InitMainGui()
    # glo_va.window_GUI = Render_Examanination_Room_Table()
    time.sleep(0.5)
    print("Done Init GUI")
    print()

def Start_Server_Connection():
    print("Starting Init Server Connection")
    glo_va.server = Server()
    print("Done Init Server Connection")
    print()

#########################################################################
# STOP FUNCTIONS                                                        #
#########################################################################
# def Stop_Face_Detector():
#     print("Stop Face Detector")
#     del glo_va.face_detector

#     glo_va.cuda_ctx.pop()
#     del glo_va.cuda_ctx
#     print('\tTrtThread: stopped...')
#     print()

def Stop_Face_Recognition():
    print("Stop Face Recognition")
    del glo_va.face_recognition
    print()

def Stop_Camera_Detecting():
    glo_va.camera.StopCamera()
    print("Stop Camera Detecting")
    print()

def Stop_Connecting_Server():
    glo_va.server.Close()
    print("Stop Connecting Server")
    print()

def Stop_Count_Face():
    glo_va.count_face.Stop()
    print("Stop Count Face")
    print()

def Stop_Timer():
    glo_va.timer.Stop()
    print("Stop Timer")
    print()

#########################################################################
# INIT FUNCTION                                                         #
#########################################################################
def Init():
    if glo_va.STATE == 1:
        print('Start init program')
        # Init face recognition
        Start_Face_Recognition()
        glo_va.flg_init_face_recognition = True

        # Init camera detecting
        Start_Camera_Detecting()
        glo_va.flg_init_camera = True
        
        # Init count face
        Start_Count_Face()
        glo_va.flg_init_count_face = True

        # Init server connection
        Start_Server_Connection()
        # glo_va.flg_server_connected = True

        # Init Timer
        Start_Timer()
        glo_va.flg_init_timer = True
    
        # Init lock response from server and timer
        glo_va.lock_response_server = Lock()

    # Init GUI
    # Start_GUI()


#########################################################################
# End FUNCTION                                                          #
#########################################################################
def End():
    if glo_va.flg_init_count_face:
        Stop_Count_Face()
        glo_va.flg_init_count_face = False

    if glo_va.flg_init_timer:
        Stop_Timer()
        glo_va.flg_init_timer = False

    if glo_va.flg_init_GUI:
        # glo_va.window_GUI.close()
        glo_va.gui.close()
        glo_va.flg_init_GUI = False

    if glo_va.flg_init_camera:
        Stop_Camera_Detecting()
        glo_va.flg_init_camera = False
    
    if glo_va.flg_init_face_recognition:
        Stop_Face_Recognition()
        glo_va.flg_init_face_recognition = False

    if glo_va.flg_server_connected:
        Stop_Connecting_Server()
        glo_va.flg_server_connected = False

import time
def main():
    while glo_va.ENABLE_RUN:
        if glo_va.START_RUN == False:
            continue

        try:
            event = 1
            if glo_va.STATE == -1:
                End()
                break

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
            
            # Confirm final submission
            elif glo_va.STATE == 7:
                State_7(event)

            # time.sleep(5)
            # End()
            # return    

        except Exception as e:
            print("Error at module main in main: {}".format(e))
            End()
            return
        except KeyboardInterrupt:
            print('Interrupted')
            End()
            return
    
#########################################################################
# Main FUNCTION                                                         #
#########################################################################
# import cv2
if __name__ == "__main__":
    try:
        Init()
        main_thread = threading.Thread(target=main, args=())
        main_thread.daemon = True
        main_thread.start()

        app = QtWidgets.QApplication(sys.argv)
        glo_va.gui = GUI()
        glo_va.gui.show()
        glo_va.flg_init_GUI = True
        glo_va.START_RUN = True
        app.exec_()
    except Exception as e:
        print("Error at Init module: {}".format(e))

    glo_va.START_RUN = False
    glo_va.ENABLE_RUN = False
    main_thread.join()
    End()
    # print("Turn off E-Healthcare system")
    # cv2.imshow('test', glo_va.detected_face)
    # cv2.waitKey(2000)