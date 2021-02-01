import cv2
import numpy as np
import PySimpleGUI as sg
from PIL import Image, ImageTk

from utils.parameters import *
from utils.common_functions import AdjustBright
    
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

    # Pre-processing
    resized_img = cv2.resize(iden_new_img, (IMAGE_SIZE,IMAGE_SIZE))
    resized_img = AdjustBright(resized_img)
    RGB_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

    glo_va.embedded_face = glo_va.face_identifying.face_encodings(RGB_resized_img, [(0, IMAGE_SIZE, IMAGE_SIZE,0)])[0]
    glo_va.embedded_face = np.array(glo_va.embedded_face).reshape(1,-1)