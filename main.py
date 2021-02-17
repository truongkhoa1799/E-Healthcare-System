# from identifying_users.face_detector_CenterFace import FaceDetector
from identifying_users.face_recognition import Face_Recognition
from identifying_users.camera_detecting import CameraDetecting
from identifying_users.count_face import CountFace

from communicate_server.server import Server

from utils.parameters import *
from identifying_users.identifying_users_functions import *

import time
# import pycuda.driver as cuda

from utils.common_functions import Preprocessing_Img

#########################################################################
# START FUNCTIONS                                                       #
#########################################################################
# def Start_Face_Detector():
#     print("Starting init Face Detector")

#     print('\tTrtThread: loading the TRT model...')
#     glo_va.cuda_ctx = cuda.Device(0).make_context()  # GPU 0
    
#     print("\tLoad Face Detector model")
#     glo_va.face_detector = FaceDetector(landmarks=False)

#     time.sleep(0.5)
#     print("Done start init Face Detector")
#     print()

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

def Start_GUI():
    print("Starting Init GUI")
    InitGUI()
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

#########################################################################
# INIT FUNCTION                                                         #
#########################################################################
def Init():
    glo_va.has_response_server = False

    # # # Init Face Detector
    # # Start_Face_Detector()
    # # glo_va.flg_init_face_detector = True

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
    glo_va.flg_server_connected = True

    # Init GUI
    Start_GUI()
    glo_va.flg_init_GUI = True

#########################################################################
# End FUNCTION                                                          #
#########################################################################
def End():
    if glo_va.flg_init_count_face:
        glo_va.count_face.Stop()

    if glo_va.flg_init_GUI:
        glo_va.window_GUI.close()

    if glo_va.flg_init_camera:
        Stop_Camera_Detecting()

    # if glo_va.flg_init_face_detector:
    #     Stop_Face_Detector()
    
    if glo_va.flg_init_face_recognition:
        Stop_Face_Recognition()

    if glo_va.flg_server_connected:
        Stop_Connecting_Server()
        
#########################################################################
# Main FUNCTION                                                         #
#########################################################################
if __name__ == "__main__":
    try:
        Init()
    except Exception as e:
        print("Error at Init module: {}".format(e))
        End()
        exit(-1)
        
    while True:
        event, values = glo_va.window_GUI.read(timeout=1)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            glo_va.STATE = -1
        elif event == 'Start' and glo_va.STATE == 0:
            glo_va.count_face.Start_Counting_Face()
            glo_va.STATE = 1
            # glo_va.window_GUI[f'-COL1-'].update(visible=False)
            # glo_va.window_GUI[f'-COL2-'].update(visible=True)
            # progress_bar = glo_va.window_GUI.FindElement('sensor_progress')
            # progress_bar.UpdateBar(20, 100)
        try:
            # STATE INIT
            if glo_va.STATE == -1:
                End()
                break

            # STATE DETECTING AND RECOGNIZING PATIENT
            elif glo_va.STATE == 1:
                # Read camera
                glo_va.camera.RunCamera()

                # # Face detecting
                ret = Locating_Faces()
                if ret == -2:
                    print("Error Face locations")
                    glo_va.STATE = -1
                    continue
                elif ret == 0:
                    # Face Identifying
                    glo_va.face_recognition.Encoding_Face()
                    glo_va.count_face.Count_Face()

                ConvertToDisplay()
                glo_va.window_GUI['image'].update(data=glo_va.display_image)

                if glo_va.has_response_server == True:
                    if user_infor.status == 0:
                        glo_va.STATE = 2
                        user_infor.Update()
                        
                    glo_va.is_sending_message = False
                    glo_va.has_response_server = False

            # STATE CONFIRMING PATIENT INFORMATION
            elif glo_va.STATE == 2:
                if event == 'Confirm':
                    glo_va.window_GUI[f'-COL1-'].update(visible=False)
                    glo_va.window_GUI[f'-COL2-'].update(visible=True)
                    user_infor.Clear()
                    user_infor.Update()
                    glo_va.STATE = 3
                elif event == 'Reject':
                    user_infor.Clear()
                    user_infor.Update()
                    glo_va.STATE = 1

            # STATE MEASURING PATIENT' BIOLOGICAL PARAMETERS
            elif glo_va.STATE == 3:
                continue
        except Exception as e:
            print("Error at module main in main: {}".format(e))
            End()
            break
        except KeyboardInterrupt:
            print('Interrupted')
            End()
            break
    print("Turn off E-Healthcare system")