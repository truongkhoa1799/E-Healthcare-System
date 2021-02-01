from identifying_users.face_detector_CenterFace import FaceDetector
from identifying_users.face_identifying import FaceIdentify
from identifying_users.camera_detecting import CameraDetecting
from identifying_users.count_face import CountFace

from utils.parameters import *
from identifying_users.identifying_users_functions import *

import time
import pycuda.driver as cuda

def StartFaceDetector():
    print('TrtThread: loading the TRT model...')
    glo_va.cuda_ctx = cuda.Device(0).make_context()  # GPU 0
    print("Load Face Detector model")
    glo_va.face_detector = FaceDetector(landmarks=False)

def StopFaceDetector():
    del glo_va.face_detector
    del glo_va.face_identifying
    glo_va.cuda_ctx.pop()
    del glo_va.cuda_ctx
    print('TrtThread: stopped...')

def Init():
    # Init face regonizer
    print("Starting init Face Detector")
    StartFaceDetector()
    glo_va.flg_init_face_detector = True
    time.sleep(0.5)
    print("Done start init Face Detector")
    print()

    # Init camera detecting
    print("Starting init Camera")
    glo_va.camera = CameraDetecting()
    glo_va.flg_init_camera = True
    time.sleep(0.5)
    print("Done start init Camera")
    print()
    
    # Init face identifying
    print("Starting init Face Identifier")
    glo_va.face_identifying = FaceIdentify()
    time.sleep(0.5)
    # Init face identifying
    print("Done start init Face Identifier")
    print()

    # Init count face
    print("Starting Init CountFace")
    glo_va.count_face = CountFace()
    glo_va.flg_init_count_face = True
    print("Done start CountFace")
    print()

    # Init GUI
    print("Starting Init GUI")
    InitGUI()
    glo_va.flg_init_GUI = True
    print("Done Init GUI")


def End():
    if glo_va.flg_init_count_face:
        glo_va.count_face.stop()

    if glo_va.flg_init_GUI:
        glo_va.window_GUI.close()

    if glo_va.flg_init_camera:
        glo_va.camera.StopCamera()

    if glo_va.flg_init_face_detector:
        StopFaceDetector()

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
                ret = LocateFaces()
                # print("\tTime to detect face: {}".format(time.time() - time_detecting))

                # Face Identifying
                # time_identifying = time.time()
                FaceIdentifying()
                # print("\tTime to iden face: {}".format(time.time() - time_identifying))

                face_id, dist = glo_va.face_identifying.GetFaceID()

                if ret == -3:
                    print("Error Face locations")
                    glo_va.STATE = 2
                    continue
                elif ret == -2:
                    print("There is more than 1 patient detected")
                    glo_va.count_face.Error()
                elif ret == 0 and face_id != "Null":
                    glo_va.count_face.CountFace(face_id)

                ConvertToDisplay()
                if glo_va.patient_id is not None:
                    glo_va.window_GUI['-NAME-'].update(str(glo_va.patient_id))
                glo_va.window_GUI['image'].update(data=glo_va.display_image)
            
        except Exception as e:
            print(e)
            End()
            break
    print("Turn off E-Healthcare system")