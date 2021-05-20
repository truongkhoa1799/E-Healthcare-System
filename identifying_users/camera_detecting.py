import cv2
from threading import Thread

from utils.parameters import *
from utils.csi_camera import CSI_Camera
from utils.common_functions import LogMesssage

# import pycuda.driver as cuda
# from face_detector_CenterFace import FaceDetector
# from FaceIdentifying import FaceIdentify
# from CountFace import CountFace

class CameraDetecting(Thread):
    def __init__(self):
        self.__csi_camera = CSI_Camera()

        LogMesssage("Init camera", opt=0)
        self.__csi_camera.open()
        self.__csi_camera.start()
        
        if show_fps == True:
            self.__csi_camera.start_counting_fps()

    def __DrawLabel(self,cv_image, label_text, label_position):
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.5
        color = (255,255,255)
        # You can get the size of the string with cv2.getTextSize here
        cv2.putText(cv_image, label_text, label_position, font_face, scale, color, 1, cv2.LINE_AA)
    
    def RunCamera(self):
        original_img = self.__csi_camera.read()
        
        if glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT:
            margin_width = int((original_img.shape[1] - glo_va.LOCATION_RECOGNIZE_FACE_WIDTH) / 2)
            margin_height = int((original_img.shape[0] - glo_va.LOCATION_RECOGNIZE_FACE_HEIGHT) / 2)

            glo_va.img = original_img[margin_height:glo_va.LOCATION_RECOGNIZE_FACE_HEIGHT+margin_height , margin_width:glo_va.LOCATION_RECOGNIZE_FACE_WIDTH+margin_width]
        
        elif glo_va.STATE == glo_va.STATE_NEW_PATIENT:
            margin_width = int((original_img.shape[1] - glo_va.LOCATION_ADD_FACE_WIDTH) / 2)
            margin_height = int((original_img.shape[0] - glo_va.LOCATION_ADD_FACE_HEIGHT) / 2)

            glo_va.img = original_img[margin_height:glo_va.LOCATION_ADD_FACE_HEIGHT+margin_height , margin_width:glo_va.LOCATION_ADD_FACE_WIDTH+margin_width]

        if show_fps == True:
            # show_fps:
            self.__DrawLabel(glo_va.img, "Frames Displayed (PS): "+str(self.__csi_camera.last_frames_displayed),(10,20))
            self.__DrawLabel(glo_va.img, "Frames Read (PS): "+str(self.__csi_camera.last_frames_read),(10,40))

            self.__csi_camera.frames_displayed += 1
    
    def currentStopCamera(self):
        self.__csi_camera.stop()
        LogMesssage("[currentStopCamera]: Temporarily stop camera detecting")
    
    def runBackCamera(self):
        self.__csi_camera.start()
        LogMesssage("[currentStopCamera]: Run back camera detecting")
    
    def StopCamera(self):
        LogMesssage("Stop camera", opt=0)
        self.__csi_camera.stop()
        self.__csi_camera.release()
        print()
