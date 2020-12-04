import cv2
import numpy as np
import os
from threading import Lock, Timer
import face_recognition
import time
#######################################################################################
# Define parameters                                                                   #
#######################################################################################
DATA_PATH = "/home/thesis/Documents/E-Healthcare-System/Face/"
PATH_USER_IMG_ENCODED = "/home/thesis/Documents/E-Healthcare-System/Data/Encoded_Face"
PATH_USER_ID = "/home/thesis/Documents/E-Healthcare-System/Data/ID_Face"
KNN_MODEL_PATH = "/home/thesis/Documents/E-Healthcare-System/Model/knn_clf_model.clf"

FACE_TEST_PATH = "/home/thesis/Documents/E-Healthcare-System/Data/test"
FACE_TRAIN_PATH = "/home/thesis/Documents/E-Healthcare-System/Data/train"

SAVING_IMG_PATH = "/home/thesis/Documents/E-Healthcare-System/TEST_FACE/Test"
SAVING_IMGDetec_PATH = "/home/thesis/Documents/E-Healthcare-System/TEST_FACE/Detect"

PATIENT_FILE = 'Patients.json'

IMAGE_SIZE = 150
THRESHOLD_FACE_REC = 0.5
NUM_JITTERS = 1
NUM_NEIGHBROS = 3
KNN_ALGORITHM = 'ball_tree'
KNN_WEIGHTS = 'distance'

NUMBER_LOSS_FACE=1
CYCLE_COUNT_FACE_PERIOD = 2.0
show_fps = True
# Good for 1280x720
DISPLAY_WIDTH=640
DISPLAY_HEIGHT=360

LOCATION_FACE_WIDTH = 300
LOCATION_FACE_HEIGHT = 360

# image for center face
SCALE_WIDTH=320
SCALE_HEIGHT=192

# For 1920x1080
# DISPLAY_WIDTH=960
# DISPLAY_HEIGHT=540

# 1920x1080, 30 fps
SENSOR_MODE_1080=2
# 1280x720, 60 fps
SENSOR_MODE_720=3

time_detecting = 0
time_identifying = 0
time_read_frame = 0

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class GlobalVariable:
    def __init__(self):
        self.gui = None
        self.camera = None
        self.STATE = 0
        self.img = None
        self.window_GUI = None
        self.face_detector = None
        self.cuda_ctx = None
        self.face_location = None
        self.face_identifying = None
        self.embedded_face = None
        # self.finished_iden = None
        # self.finish_flag = None
        # self.queue = []
        # self.inden_thread = None
        self.count_face = None

glo_va = GlobalVariable()

def SaveFace(opt,dir_name,img_name, img,locations):
    count = 0
    if opt==0:
        os.chdir(SAVING_IMG_PATH) 
        for (top, right, bottom, left) in locations:
            img_name_1 = dir_name+'-'+str(count)+'-'+img_name
            cv2.imwrite(img_name_1, img[top:bottom,left:right]) 
            count += 1

def LocateFaces():
    # CenterFace
    if glo_va.img is not None:
        # locate faces in the images
        face_locations = glo_va.face_detector(glo_va.img)
        if len(face_locations) == 0:
            glo_va.face_location = (1, LOCATION_FACE_HEIGHT, 1, LOCATION_FACE_WIDTH)
            return
        try:
            for face_location in face_locations:
                boxes, score = face_location[:4], face_location[4]
                left = int(face_location[0])
                top = int(face_location[1])
                right = int(face_location[2])
                bottom = int(face_location[3])
                cv2.rectangle(glo_va.img, (left, top), (right, bottom) , (2, 255, 0), 2)
                glo_va.face_location = (top, bottom, left, right)
                return
        except:
            print("Error Face locations")
            return
    
    return

def FaceIdentifying():
    iden_new_img = glo_va.img[glo_va.face_location[0] : glo_va.face_location[1], glo_va.face_location[2] : glo_va.face_location[3]]
    fra = IMAGE_SIZE / max(iden_new_img.shape[0], iden_new_img.shape[1]) 
    resized_img = cv2.resize(iden_new_img, (int(iden_new_img.shape[1] * fra), int(iden_new_img.shape[0] * fra)))
    RGB_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

    glo_va.embedded_face = face_recognition.face_encodings(RGB_resized_img, [(0, IMAGE_SIZE, IMAGE_SIZE,0)])[0]
    glo_va.embedded_face = np.array(glo_va.embedded_face).reshape(1,-1)
        