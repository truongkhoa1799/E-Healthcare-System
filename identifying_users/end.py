from utils.parameters import *
from utils.kill_python_process import KillPythonProcess
from utils.common_functions import LogMesssage

#########################################################################
# STOP FUNCTIONS                                                        #
#########################################################################
def Stop_Face_Recognition():
    LogMesssage("Stop Face Recognition", opt=0)
    del glo_va.face_recognition
    print()

def Stop_Camera_Detecting():
    glo_va.camera.StopCamera()
    LogMesssage("Stop Camera Detecting", opt=0)
    print()

def Stop_Connecting_Server():
    glo_va.server.Close()
    LogMesssage("Stop Connecting Server", opt=0)
    print()

def Stop_Count_Face():
    glo_va.count_face.Stop()
    LogMesssage("Stop Count Face", opt=0)
    print()

def Stop_Timer():
    glo_va.timer.Stop()
    LogMesssage("Stop Timer", opt=0)
    print()

def Stop_GUI():
    glo_va.gui.close()
    LogMesssage("Stop GUI", opt=0)
    print()

#########################################################################
# End FUNCTION                                                          #
#########################################################################
def End():
    LogMesssage('End program', opt=0)

    glo_va.START_RUN = False
    glo_va.ENABLE_PROGRAM_RUN = False

    if glo_va.flg_init_count_face:
        Stop_Count_Face()
        glo_va.flg_init_count_face = False

    if glo_va.flg_init_timer:
        Stop_Timer()
        glo_va.flg_init_timer = False

    if glo_va.flg_init_GUI:
        Stop_GUI()
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
    
    if glo_va.flg_init_momo_assistant:
        LogMesssage("Stop Momo Assistant", opt=0)
        del glo_va.momo_assis
        glo_va.flg_init_momo_assistant = False
    
    LogMesssage("Turn off E-Healthcare system", opt=0)
    KillPythonProcess()