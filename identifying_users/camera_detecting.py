import cv2
from threading import Thread

from utils.parameters import *
from utils.csi_camera import CSI_Camera

# import pycuda.driver as cuda
# from face_detector_CenterFace import FaceDetector
# from FaceIdentifying import FaceIdentify
# from CountFace import CountFace

class CameraDetecting(Thread):
    def __init__(self):
        self.__csi_camera = CSI_Camera()
        self.__csi_camera.create_gstreamer_pipeline(
            sensor_id=0,
            sensor_mode=SENSOR_MODE_720,
            framerate=30,
            flip_method=2,
            display_height=DISPLAY_HEIGHT,
            display_width=DISPLAY_WIDTH,
        )

        print("Init camera")
        self.__csi_camera.open(self.__csi_camera.gstreamer_pipeline)
        self.__csi_camera.start()
        
        cv2.namedWindow("Face Detect", cv2.WINDOW_AUTOSIZE)
        if( not self.__csi_camera.video_capture.isOpened() ):
            print("Unable to open any cameras")
            self.__csi_camera.stop()
            self.__csi_camera.release()
            cv2.destroyAllWindows()
            SystemExit(0)
        
        if show_fps == True:
            self.__csi_camera.start_counting_fps()

    def __DrawLabel(self,cv_image, label_text, label_position):
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.5
        color = (255,255,255)
        # You can get the size of the string with cv2.getTextSize here
        cv2.putText(cv_image, label_text, label_position, font_face, scale, color, 1, cv2.LINE_AA)
    
    def RunCamera(self):
        _ , original_img = self.__csi_camera.read()

        margin_width = int((original_img.shape[1] - LOCATION_FACE_WIDTH) / 2)
        margin_height = int((original_img.shape[0] - LOCATION_FACE_HEIGHT) / 2)

        glo_va.img = original_img[margin_height:LOCATION_FACE_HEIGHT+margin_height , margin_width:LOCATION_FACE_WIDTH+margin_width]
        
        if show_fps == True:
            # show_fps:
            self.__DrawLabel(glo_va.img, "Frames Displayed (PS): "+str(self.__csi_camera.last_frames_displayed),(10,20))
            self.__DrawLabel(glo_va.img, "Frames Read (PS): "+str(self.__csi_camera.last_frames_read),(10,40))

            self.__csi_camera.frames_displayed += 1
    
    def StopCamera(self):
        print("Stop camera")
        self.__csi_camera.stop()
        self.__csi_camera.release()
        cv2.destroyAllWindows()
        print()