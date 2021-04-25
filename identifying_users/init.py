import time
from utils.parameters import *

from identifying_users.face_recognition import Face_Recognition
from identifying_users.camera_detecting import CameraDetecting
from identifying_users.count_face import CountFace

from assistant.momo_assistant import MomoAssistant

from communicate_server.server import Server
from utils.timer import Timer
from utils.common_functions import LogMesssage

from threading import Lock
#########################################################################
# INIT FUNCTION                                                         #
#########################################################################
def Init():
    if glo_va.STATE == 1:
        LogMesssage('Start init program', opt=0)

        # Init momo assistant
        StartMomoAssistant()
        glo_va.flg_init_momo_assistant = True
        # exit(0)
        
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

        # Init Timer
        Start_Timer()
        glo_va.flg_init_timer = True

        # Init lock response from server and timer
        glo_va.lock_init_state = Lock()
        glo_va.lock_response_server = Lock()

        # Get init parameters
        loadParametersFromServer()
    
    # glo_va.STATE = 6
    time.sleep(2)

#########################################################################
# START FUNCTIONS                                                       #
#########################################################################
def Start_Face_Recognition():
    LogMesssage("Starting init Face Recognition", opt=0)
    glo_va.face_recognition = Face_Recognition()

    time.sleep(0.5)
    LogMesssage("Done start init Face Encoder", opt=0)
    print()

def Start_Camera_Detecting():
    LogMesssage("Starting init Camera", opt=0)
    glo_va.camera = CameraDetecting()

    time.sleep(0.5)
    LogMesssage("Done start init Camera", opt=0)
    print()

def Start_Count_Face():
    LogMesssage("Starting Init CountFace", opt=0)
    glo_va.count_face = CountFace()
    time.sleep(0.5)
    LogMesssage("Done start CountFace", opt=0)
    print()

def Start_Timer():
    LogMesssage("Starting Init Timer", opt=0)
    glo_va.timer = Timer()
    time.sleep(0.5)
    LogMesssage("Done start Timer", opt=0)
    print()

def Start_Server_Connection():
    LogMesssage("Starting Init Server Connection", opt=0)
    glo_va.server = Server()
    LogMesssage("Done Init Server Connection", opt=0)
    print()

def StartMomoAssistant():
    LogMesssage("Starting Momo Assistant", opt=0)
    glo_va.momo_assis = MomoAssistant()
    LogMesssage("Done Init Server Connection", opt=0)
    print()

def loadParametersFromServer():
    glo_va.is_sending_message = False
    glo_va.has_response_server = False
    LogMesssage('Load init parameters', opt=0)

    glo_va.timer.Start_Timer(glo_va.OPT_TIMER_GET_INIT_PARAMETERS)
    glo_va.is_sending_message = True
    glo_va.server.getInitParameters()
    
    while init_parameters.status == glo_va.NOT_HAS_INIT_PARAMETERS and glo_va.ENABLE_PROGRAM_RUN:
        if glo_va.has_response_server == True:
            glo_va.is_sending_message = False
            glo_va.has_response_server = False
            LogMesssage('Has init parameters', opt=0)
        
        if init_parameters.status == glo_va.NOT_HAS_INIT_PARAMETERS and glo_va.is_sending_message == False:
            LogMesssage('Fail to get init parameters. Resend request')
            glo_va.timer.Start_Timer(glo_va.OPT_TIMER_GET_INIT_PARAMETERS)
            glo_va.is_sending_message = True
            glo_va.server.getInitParameters()
    
    LogMesssage('Done load init parameters', opt=0)