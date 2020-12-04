from csi_camera import CSI_Camera
from common_functions import *
import cv2
import time
from threading import Thread

# import pycuda.driver as cuda
# from face_detector_CenterFace import FaceDetector
# from FaceIdentifying import FaceIdentify
# from CountFace import CountFace

class CameraDetecting(Thread):
    def __init__(self, count_face = 0):
        self.__left_camera = CSI_Camera()
        self.__left_camera.create_gstreamer_pipeline(
                sensor_id=0,
                sensor_mode=SENSOR_MODE_720,
                framerate=30,
                flip_method=2,
                display_height=DISPLAY_HEIGHT,
                display_width=DISPLAY_WIDTH,
        )
        print("Init camera")
        self.__left_camera.open(self.__left_camera.gstreamer_pipeline)
        self.__left_camera.start()
        cv2.namedWindow("Face Detect", cv2.WINDOW_AUTOSIZE)
        if( not self.__left_camera.video_capture.isOpened() ):
            print("Unable to open any cameras")
            self.__left_camera.stop()
            self.__left_camera.release()
            cv2.destroyAllWindows()
            SystemExit(0)

        self.__left_camera.start_counting_fps()

    def __DrawLabel(self,cv_image, label_text, label_position):
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.5
        color = (255,255,255)
        # You can get the size of the string with cv2.getTextSize here
        cv2.putText(cv_image, label_text, label_position, font_face, scale, color, 1, cv2.LINE_AA)

    def __ReadCamera(self,csi_camera,display_fps):
        _ , camera_image=csi_camera.read()
        if display_fps:
            __DrawLabel(camera_image, "Frames Displayed (PS): "+str(csi_camera.last_frames_displayed),(10,20))
            __DrawLabel(camera_image, "Frames Read (PS): "+str(csi_camera.last_frames_read),(10,40))
        return camera_image
    
    def RunCamera(self):
        glo_va.img = self.__ReadCamera(self.__left_camera,False)

        margin_width = int((glo_va.img.shape[1] - LOCATION_FACE_WIDTH) / 2)
        margin_height = int((glo_va.img.shape[0] - LOCATION_FACE_HEIGHT) / 2)

        glo_va.img = glo_va.img[margin_height:LOCATION_FACE_HEIGHT+margin_height , margin_width:LOCATION_FACE_WIDTH+margin_width]
        # self.__LocateFaces(img)
        
        # show_fps:
        self.__DrawLabel(glo_va.img, "Frames Displayed (PS): "+str(self.__left_camera.last_frames_displayed),(10,20))
        self.__DrawLabel(glo_va.img, "Frames Read (PS): "+str(self.__left_camera.last_frames_read),(10,40))

        # cv2.imshow("Face Detect", glo_va.img)

        self.__left_camera.frames_displayed += 1
    
    def StopCamera(self):
        print("Stop camera")
        self.__left_camera.stop()
        self.__left_camera.release()
        cv2.destroyAllWindows()