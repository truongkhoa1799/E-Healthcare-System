import os
import cv2
import time
import numpy as np
import numpy as numpy
import face_recognition
import PySimpleGUI as sg
from PIL import Image, ImageTk
from threading import Lock, Timer
#######################################################################################
# Define parameters                                                                   #
#######################################################################################
DATA_PATH = "/home/thesis/Documents/E-Healthcare-System/Face/"
PATH_USER_IMG_ENCODED = "/home/thesis/Documents/E-Healthcare-System/Data/Encoded_Face"
PATH_USER_ID = "/home/thesis/Documents/E-Healthcare-System/Data/ID_Face"
KNN_MODEL_PATH = "/home/thesis/Documents/E-Healthcare-System/Data/knn_clf_model.clf"

FACE_TEST_PATH = "/home/thesis/Documents/E-Healthcare-System/Data/test"
FACE_TRAIN_PATH = "/home/thesis/Documents/E-Healthcare-System/Data/train"

SAVING_IMG_PATH = "/home/thesis/Documents/E-Healthcare-System/TEST_FACE/Test"
SAVING_IMGDetec_PATH = "/home/thesis/Documents/E-Healthcare-System/TEST_FACE/Detect"

CENTER_FACE_TRT_PATH = '/home/thesis/Documents/E-Healthcare-System/Data/face_detector_320_192.trt'

PATIENT_FILE = 'Patients.json'

IMAGE_SIZE = 150
THRESHOLD_FACE_REC = 0.5
NUM_JITTERS = 1
NUM_NEIGHBROS = 3
KNN_ALGORITHM = 'ball_tree'
KNN_WEIGHTS = 'distance'

CYCLE_COUNT_FACE_PERIOD = 2.0
THRESHOLD_PATIENT_REC = 20
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
        self.display_image = None
        self.window_GUI = None
        self.face_detector = None
        self.cuda_ctx = None
        self.face_location = None
        self.face_identifying = None
        self.embedded_face = None
        self.patient_id = None
        self.count_face = None

        # flag init
        self.flg_init_count_face = False
        self.flg_init_GUI = False
        self.flg_init_camera = False
        self.flg_init_face_detector = False

glo_va = GlobalVariable()

def SaveFace(opt,dir_name,img_name, img,locations):
    count = 0
    if opt==0:
        os.chdir(SAVING_IMG_PATH) 
        for (top, right, bottom, left) in locations:
            img_name_1 = dir_name+'-'+str(count)+'-'+img_name
            cv2.imwrite(img_name_1, img[top:bottom,left:right]) 
            count += 1

def ConvertToDisplay():
    glo_va.display_image = cv2.cvtColor(glo_va.img, cv2.COLOR_BGR2RGB)  # to RGB
    glo_va.display_image = Image.fromarray(glo_va.display_image)  # to PIL format
    glo_va.display_image = ImageTk.PhotoImage(glo_va.display_image)  # to ImageTk format

def InitGUI():
    # sg.theme('Black')

    # define the window layout
    camera_layout = [[sg.Image(filename='', key='image', size=(300,360), visible=True)],]
    information_layout = [
            [sg.Text('Name', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Text('Name', size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', key='-NAME-', text_color='black')],
            [sg.Text('Birth Date', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Input('Birth Date', size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', disabled=True, key='patient_bd')],
            [sg.Text('Phone', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Input('Phone', size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', disabled=True, key='patient_phone')],
            [sg.Text('Address', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Input('Address', size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', disabled=True, key='patient_address')],
            [
            sg.Button('Start', size=(10, 1), font='Helvetica 14'),
            sg.Button('Exit', size=(10, 1), font='Helvetica 14'),
            ],
    ]
    sensor_information_layout = [
            [sg.Text('Blood Pressure', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Input('Blood Pressure', size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', disabled=True, key='patient_bp')],
            [sg.Text('Pulse Sensor', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Input('Pulse Sensor', size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', disabled=True, key='patient_ps')],
            [sg.Text('Thermal Sensor', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Input('Thermal Sensor', size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', disabled=True, key='patient_ts')],
            [sg.Text('SPO2', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Input('SPO2', size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', disabled=True, key='patient_spo2')],
    ]

    layout = [
        [sg.Text('Smart E-Healthcare', size=(40, 1), justification='center', font='Helvetica 20')],
        [
        sg.Column(camera_layout, key='column1', size=(300,400)),
        sg.VSeperator(),
        sg.Column(information_layout,size=(500,400))
        ], 
    ]
    # create the window and show it without the plot
    glo_va.window_GUI = sg.Window('Demo Application - OpenCV Integration', layout, location=(800, 400), size=(800, 400))
    print("OPENED GUI")

def LocateFaces():
    # CenterFace
    if glo_va.img is not None:
        # locate faces in the images
        face_locations = glo_va.face_detector(glo_va.img)
        
        if len(face_locations) == 0:
            glo_va.face_location = (1, LOCATION_FACE_HEIGHT, 1, LOCATION_FACE_WIDTH)
            return -1
        elif len(face_locations) > 1:
            glo_va.face_location = (1, LOCATION_FACE_HEIGHT, 1, LOCATION_FACE_WIDTH)
            return -2

        try:
            for face_location in face_locations:
                boxes, score = face_location[:4], face_location[4]
                left = int(face_location[0])
                top = int(face_location[1])
                right = int(face_location[2])
                bottom = int(face_location[3])
                cv2.rectangle(glo_va.img, (left, top), (right, bottom) , (2, 255, 0), 2)
                glo_va.face_location = (top, bottom, left, right)
                return 0
        except:
            return -3
    
    return -1

def FaceIdentifying():
    iden_new_img = glo_va.img[glo_va.face_location[0] : glo_va.face_location[1], glo_va.face_location[2] : glo_va.face_location[3]]
    fra = IMAGE_SIZE / max(iden_new_img.shape[0], iden_new_img.shape[1]) 
    resized_img = cv2.resize(iden_new_img, (int(iden_new_img.shape[1] * fra), int(iden_new_img.shape[0] * fra)))
    RGB_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

    glo_va.embedded_face = face_recognition.face_encodings(RGB_resized_img, [(0, IMAGE_SIZE, IMAGE_SIZE,0)])[0]
    glo_va.embedded_face = np.array(glo_va.embedded_face).reshape(1,-1)
        