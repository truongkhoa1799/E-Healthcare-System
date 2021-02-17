import cv2
import numpy as np
import PySimpleGUI as sg
from PIL import Image, ImageTk

from utils.parameters import *
    
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
            [sg.Text(user_infor.name, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', key='-NAME-', text_color='black')],
            [sg.Text('Birth Date', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Text(user_infor.birthday, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', key='-BD-', text_color='black')],
            [sg.Text('Phone', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Text(user_infor.phone, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', key='-PHONE-', text_color='black')],
            [sg.Text('Address', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Text(user_infor.address, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', key='-ADDRESS-', text_color='black')],
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

def Locating_Faces():
    face_area = 0
    max_face_area = 0

    if glo_va.img is not None:
        # # locate faces in the images
        # face_locations = glo_va.face_detector(glo_va.img)
        
        # if len(face_locations) == 0:
        #     # glo_va.face_location = (1, LOCATION_FACE_HEIGHT, 1, LOCATION_FACE_WIDTH)
        #     return -1

        # area = 0
        # max_area = 0
        # try:
        #     for face_location in face_locations:
        #         boxes, score = face_location[:4], face_location[4]
        #         left = int(face_location[0])
        #         top = int(face_location[1])
        #         right = int(face_location[2])
        #         bottom = int(face_location[3])

        #         area = (right - left)*(bottom - top)
        #         if area > max_area:
        #             glo_va.face_location = (top, bottom, left, right)
        #             max_area = area
        # except:
        #     return -2

        # locate faces in the images
        fra = MAX_LENGTH_IMG / max(glo_va.img.shape[0], glo_va.img.shape[1]) 
        resized_img = cv2.resize(glo_va.img, (int(glo_va.img.shape[1] * fra), int(glo_va.img.shape[0] * fra)))
        GRAY_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
        
        face_locations = glo_va.face_recognition.Get_Face_Locations(GRAY_resized_img)

        if len(face_locations) == 0:
            return -1

        try:
            for face_location in face_locations:
                top = int(face_location[0] / fra)
                bottom = int(face_location[2] / fra)
                left = int(face_location[3] / fra)
                right = int(face_location[1] / fra)

                face_area = (right - left)*(bottom - top)
                if face_area > max_face_area:
                    glo_va.face_location = (top, bottom, left, right)
                    max_face_area = face_area
        except:
            return -2

        if max_face_area > MIN_FACE_AREA:
            glo_va.detected_face = glo_va.img[glo_va.face_location[0] : glo_va.face_location[1], glo_va.face_location[2] : glo_va.face_location[3]]
            cv2.rectangle(glo_va.img, (left, top), (right, bottom) , (2, 255, 0), 2)
            return 0
        else:
            return -1

    return -1