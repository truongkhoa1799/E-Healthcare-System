# from identifying_users.face_detector_CenterFace import FaceDetector
from identifying_users.face_recognition import Face_Recognition
from identifying_users.camera_detecting import CameraDetecting
from identifying_users.count_face import CountFace

from communicate_server.server import Server

from utils.parameters import *
from identifying_users.identifying_users_functions import *
from utils.common_functions import Compose_Embedded_Face
from utils.timer import Timer

import time
from threading import Lock
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

def Start_Timer():
    print("Starting Init Timer")
    glo_va.timer = Timer()
    time.sleep(0.5)
    print("Done start Timer")
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
    glo_va.has_response_server = False

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

    # Init GUI
    Start_GUI()
    glo_va.flg_init_GUI = True

    # Init Timer
    Start_Timer()
    glo_va.flg_init_timer = True

    # Init lock response from server and timer
    glo_va.lock_response_server = Lock()

#########################################################################
# End FUNCTION                                                          #
#########################################################################
def End():
    if glo_va.flg_init_count_face:
        Stop_Count_Face()

    if glo_va.flg_init_timer:
        Stop_Timer()

    if glo_va.flg_init_GUI:
        glo_va.window_GUI.close()

    if glo_va.flg_init_camera:
        Stop_Camera_Detecting()
    
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
        if event == sg.WIN_CLOSED:
            glo_va.STATE = -1
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

                display_image = ConvertToDisplay(glo_va.img)
                glo_va.window_GUI['image'].update(data=display_image)

                if glo_va.has_response_server == True:
                    if user_infor.Get_Status() == 0:
                        glo_va.STATE = 2
                        glo_va.count_face.Clear()
                        user_infor.Update_Screen()
                    elif user_infor.Get_Status() == -1 and glo_va.times_missing_face == TIMES_MISSING_FACE:
                        glo_va.STATE = 5
                        glo_va.times_missing_face = 0

                        
                    glo_va.is_sending_message = False
                    glo_va.has_response_server = False

            # STATE CONFIRMING PATIENT INFORMATION
            elif glo_va.STATE == 2:
                if event == 'Confirm':
                    glo_va.window_GUI[f'-COL1-'].update(visible=False)
                    glo_va.window_GUI[f'-COL2-'].update(visible=True)
                    user_infor.Clear()
                    user_infor.Update_Screen()
                    glo_va.STATE = 3
                    glo_va.measuring_sensor = False
                elif event == 'Reject':
                    user_infor.Clear()
                    user_infor.Update_Screen()
                    glo_va.STATE = 1

            # STATE MEASURING PATIENT' BIOLOGICAL PARAMETERS
            elif glo_va.STATE == 3:
                if event == 'Capture':
                    # glo_va.window_GUI[f'-COL2-'].update(visible=False)
                    # glo_va.window_GUI[f'-COL1-'].update(visible=True)
                    glo_va.measuring_sensor = True
                    # glo_va.STATE = 0

                if glo_va.measuring_sensor == True:
                    progress_bar = glo_va.window_GUI.FindElement('sensor_progress')
                    for i in range(10):
                        progress_bar.UpdateBar(10*(i+1), 100)
                        time.sleep(1)
                    sensor_info = {'blood_pressure': 120, 'pulse':98, 'thermal':38, 'spo2':90}
                    sensor.Update_Sensor(sensor_info)
                    sensor.Update_Screen()
                    glo_va.measuring_sensor = False

                    glo_va.STATE = 4

            # STATE CLASSIFYING ROOM
            elif glo_va.STATE == 4:
                continue
            
            # STATE CONFIRM NEW USER
            elif glo_va.STATE == 5:
                if is_new_user() == 'No':
                    glo_va.STATE = 1
                else:
                    glo_va.STATE = 6
                    glo_va.window_GUI[f'-COL1-'].update(visible=False)
                    glo_va.window_GUI[f'-COL3-'].update(visible=True)
                continue
            
            # STATE FOR NEW USER
            elif glo_va.STATE == 6:
                if event == 'Capture':
                    glo_va.embedded_face_new_user = glo_va.embedded_face
                    review_image = cv2.resize(glo_va.detected_face, (300,300))
                    display_review_image = ConvertToDisplay(review_image)
                    glo_va.window_GUI['review_photo'].update(data=display_review_image)
                    glo_va.has_capture = True
                elif event == 'Confirm' and glo_va.has_capture == True:
                    temp_embedded_face = Compose_Embedded_Face(glo_va.embedded_face_new_user)
                    glo_va.list_embedded_face_new_user += temp_embedded_face + ' '
                    glo_va.num_images_new_user += 1
                    glo_va.has_capture = False
                    glo_va.window_GUI['review_photo'].update('')
                    if glo_va.num_images_new_user == 5:
                        glo_va.START == 7
                    glo_va.window_GUI['-NUM_IMAGES-'].update(str(glo_va.num_images_new_user))

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

                display_image_new_user = ConvertToDisplay(glo_va.img)
                glo_va.window_GUI['photo_new_user'].update(data=display_image_new_user)
            
            elif glo_va.STATE == 7:
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