import sys, time, pathlib
PROJECT_PATH = pathlib.Path().absolute()
sys.path.append(PROJECT_PATH)

from utils.parameters import *

from identifying_users.face_recognition import Face_Recognition
from identifying_users.camera_detecting import CameraDetecting
from identifying_users.count_face import CountFace

from communicate_server.server import Server
from utils.timer import Timer

from threading import Lock
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
    time.sleep(0.5)
    print("Done Init GUI")
    print()

def Start_Server_Connection():
    print("Starting Init Server Connection")
    glo_va.server = Server()
    print("Done Init Server Connection")
    print()

