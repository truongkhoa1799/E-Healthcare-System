from utils.parameters import *
from utils.kill_python_process import KillPythonProcess
from utils.common_functions import LogMesssage

#########################################################################
# STOP FUNCTIONS                                                        #
#########################################################################
def Stop_Face_Recognition():
    LogMesssage("Stop Face Recognition", opt=0)
    del glo_va.face_recognition
    

def Stop_Camera_Detecting():
    glo_va.camera.StopCamera()
    LogMesssage("Stop Camera Detecting", opt=0)
    

def Stop_Connecting_Server():
    glo_va.server.Close()
    LogMesssage("Stop Connecting Server", opt=0)
    

def Stop_Count_Face():
    glo_va.count_face.Stop()
    LogMesssage("Stop Count Face", opt=0)
    

def Stop_Timer():
    glo_va.timer.Stop()
    LogMesssage("Stop Timer", opt=0)
    

def Stop_GUI():
    glo_va.gui.close()
    LogMesssage("Stop GUI", opt=0)
    

#########################################################################
# End FUNCTION                                                          #
#########################################################################
def End():
    LogMesssage('End program', opt=0)

    if glo_va.flg_init_count_face:
        Stop_Count_Face()

    if glo_va.flg_init_timer:
        Stop_Timer()

    if glo_va.flg_init_GUI:
        Stop_GUI()

    if glo_va.flg_init_camera:
        Stop_Camera_Detecting()
        glo_va.flg_init_camera = False
    
    if glo_va.flg_init_face_recognition:
        Stop_Face_Recognition()

    if glo_va.flg_server_connected:
        Stop_Connecting_Server()
    
    if glo_va.flg_init_momo_assistant:
        LogMesssage("Stop Momo Assistant", opt=0)
        del glo_va.momo_assis
    
    # Close esp connection
    try:
        glo_va.measuring_sensor.closeDevice()
    except:
        pass
    
    LogMesssage("Turn off E-Healthcare system", opt=0)
    KillPythonProcess()