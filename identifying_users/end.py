import sys, time, pathlib
PROJECT_PATH = pathlib.Path().absolute()
sys.path.append(PROJECT_PATH)

from utils.parameters import *
from utils.kill_python_process import KillPythonProcess

#########################################################################
# STOP FUNCTIONS                                                        #
#########################################################################
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
# End FUNCTION                                                          #
#########################################################################
def End():
    glo_va.START_RUN = False
    glo_va.ENABLE_RUN = False
    if glo_va.main_thread is not None:
        glo_va.main_thread.join()

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
    
    print("Turn off E-Healthcare system")
    KillPythonProcess()