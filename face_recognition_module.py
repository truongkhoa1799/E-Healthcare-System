from identifying_users.face_detector_CenterFace import FaceDetector
from identifying_users.face_identifying import FaceIdentifier
from identifying_users.camera_detecting import CameraDetecting
from identifying_users.count_face import CountFace

from utils.parameters import *
from identifying_users.identifying_users_functions import *

import time
import pycuda.driver as cuda


#########################################################################
# START FUNCTIONS                                                       #
#########################################################################
def Start_Face_Detector():
    print("Starting init Face Detector")

    print('\tTrtThread: loading the TRT model...')
    glo_va.cuda_ctx = cuda.Device(0).make_context()  # GPU 0
    
    print("\tLoad Face Detector model")
    glo_va.face_detector = FaceDetector(landmarks=False)

    time.sleep(0.5)
    print("Done start init Face Detector")
    print()

def Start_Face_Identifier():
    print("Starting init Face Identifier")
    glo_va.face_identifier = FaceIdentifier()

    time.sleep(0.5)
    print("Done start init Face Identifier")
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
    print("Done start CountFace")
    print()

def Start_GUI():
    print("Starting Init GUI")
    InitGUI()
    print("Done Init GUI")

#########################################################################
# STOP FUNCTIONS                                                        #
#########################################################################
def Stop_Face_Detector():
    print("Stop Face Detector")
    del glo_va.face_detector
    print("Stop Face Identifier")
    del glo_va.face_identifier
    glo_va.cuda_ctx.pop()
    del glo_va.cuda_ctx
    print('\tTrtThread: stopped...')

def Stop_Camera_Detecting():
    print("Stop Camera Detecting")
    glo_va.camera.StopCamera()

#########################################################################
# INIT FUNCTION                                                         #
#########################################################################
def Init():
    # Init Face Detector
    Start_Face_Detector()
    glo_va.flg_init_face_detector = True

    # Init face identifying
    Start_Face_Identifier()

    # Init camera detecting
    Start_Camera_Detecting()
    glo_va.flg_init_camera = True
    
    # Init count face
    Start_Count_Face()
    glo_va.flg_init_count_face = True

    # Init GUI
    Start_GUI()
    glo_va.flg_init_GUI = True

#########################################################################
# End FUNCTION                                                          #
#########################################################################
def End():
    if glo_va.flg_init_count_face:
        glo_va.count_face.stop()

    if glo_va.flg_init_GUI:
        glo_va.window_GUI.close()

    if glo_va.flg_init_camera:
        Stop_Camera_Detecting()

    if glo_va.flg_init_face_detector:
        Stop_Face_Detector()

        
#########################################################################
# Main FUNCTION                                                          #
#########################################################################
if __name__ == "__main__":
    try:
        Init()
    except Exception as e:
        print(e)
        End()
        exit(-1)
        
    while True:
        event, values = glo_va.window_GUI.read(timeout=1)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            glo_va.STATE = 2
        elif event == 'Start':
            glo_va.count_face.StartCountingFace()
            glo_va.STATE = 1
        try:
            if glo_va.STATE == 2:
                End()
                break
            elif glo_va.STATE == 1:
                # Read camera
                # time_read_frame = time.time()
                glo_va.camera.RunCamera()
                # print("\tTime to read frame: {}".format(time.time() - time_read_frame))

                # Face detecting
                # time_detecting = time.time()
                ret = Locating_Faces()

                if ret == -2:
                    print("Error Face locations")
                    glo_va.STATE = 2
                    continue
                    glo_va.count_face.Error()
                elif ret == 0:
                    # Face Identifying
                    # time_identifying = time.time()
                    Encoding_Face()
                    user_id = glo_va.face_identifier.Get_User_ID()
                    # print("\tTime to iden face: {}".format(time.time() - time_identifying))

                    glo_va.count_face.CountFace(user_id)

                ConvertToDisplay()
                if glo_va.patient_id is not None:
                    glo_va.window_GUI['-NAME-'].update(str(glo_va.patient_id))
                glo_va.window_GUI['image'].update(data=glo_va.display_image)
            
        except Exception as e:
            print(e)
            End()
            break
    print("Turn off E-Healthcare system")