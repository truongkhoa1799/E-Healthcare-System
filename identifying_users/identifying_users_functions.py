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
    # 370 ngang, 330 doc
    camera_layout = [[sg.Image(filename='', key='image', size=(LOCATION_FACE_WIDTH,LOCATION_FACE_HEIGHT), visible=True)],]
    examination_info = [[sg.Text('Smart E-Healthcare', size=(CAM_EXAM_LAYOUT_WIDTH,CAM_EXAM_LAYOUT_HEIGHT), justification='left', font='Helvetica 20')]]
    
    information_layout = [
            [sg.Text('Name', size=(40, 1), justification='left', font='Helvetica 16')],
            [sg.Text(user_infor.name, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-NAME-', text_color='black')],
            [sg.Text('Birth Date', size=(40, 1), justification='left', font='Helvetica 16')],
            [sg.Text(user_infor.birthday, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-BD-', text_color='black')],
            [sg.Text('Phone', size=(40, 1), justification='left', font='Helvetica 16')],
            [sg.Text(user_infor.phone, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-PHONE-', text_color='black')],
            [sg.Text('Address', size=(40, 1), justification='left', font='Helvetica 16')],
            [sg.Text(user_infor.address, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-ADDRESS-', text_color='black')],
            [sg.Text('Confirm Information', size=(50, 1), justification='left', font='Helvetica 12')],
            [
                sg.Button('Confirm', size=(15, 1), font='Helvetica 14'),
                sg.Button('Reject', size=(15, 1), font='Helvetica 14'),
            ],
    ]
    sensor_information_layout = [
            [sg.Text('Blood Pressure', size=(40, 1), justification='left', font='Helvetica 16')],
            [sg.Text(sensor.blood_pressure, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-BLOOD_PRESSURE-', text_color='black')],
            [sg.Text('Pulse Sensor', size=(40, 1), justification='left', font='Helvetica 16')],
            [sg.Text(sensor.pulse, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-PULSE-', text_color='black')],
            [sg.Text('Thermal Sensor', size=(40, 1), justification='left', font='Helvetica 16')],
            [sg.Text(sensor.thermal, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-THERMAL-', text_color='black')],
            [sg.Text('SPO2', size=(40, 1), justification='left', font='Helvetica 16')],
            [sg.Text(sensor.spo2, size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-SPO2-', text_color='black')],
            [sg.Text('Measuring sensor', size=(50, 1), justification='left', font='Helvetica 12')],
            [sg.ProgressBar(100, orientation='h', size=(50, 15), key='sensor_progress')],
    ]
   
    layout1 = [
        [
            sg.Column(camera_layout, size=(CAM_EXAM_LAYOUT_WIDTH,CAM_EXAM_LAYOUT_HEIGHT)), 
            sg.VSeparator(),
            sg.Column(information_layout, size=(INFOR_SENSOR_LAYOUT_WIDTH,INFOR_SENSOR_LAYOUT_HEIGHT))
        ],
    ]

    layout2 = [
        [
            sg.Column(examination_info, size=(CAM_EXAM_LAYOUT_WIDTH,CAM_EXAM_LAYOUT_HEIGHT)), 
            sg.VSeparator(),
            sg.Column(sensor_information_layout, size=(INFOR_SENSOR_LAYOUT_WIDTH,INFOR_SENSOR_LAYOUT_HEIGHT))
        ],
    ]


    main_layout = [
        [sg.Text('Smart E-Healthcare', size=(40, 1), justification='center', font='Helvetica 20')],
        [
            sg.Column(layout1, visible=True, key='-COL1-'),
            sg.Column(layout2, visible=False, key='-COL2-'),
        ], 
        [
            sg.Button('Start', size=(35, 1), font='Helvetica 14'),
            sg.Button('Exit', size=(35, 1), font='Helvetica 14'),
        ],
    ]
    # create the window and show it without the plot


    glo_va.window_GUI = sg.Window('Demo Application - OpenCV Integration', main_layout, location=(400, 400), size=(WIDTH_GUI, HEIGHT_GUI), element_justification='c')

    # original_logo = cv2.imread('/home/thesis/Documents/E-Healthcare-System/model_engine/logo.jpeg')
    # original_logo = cv2.resize(original_logo, (CAMERA_DISPLAY_WIDTH,CAMERA_DISPLAY_HEIGHT))

    # margin_width = int((original_logo.shape[1] - LOCATION_FACE_WIDTH) / 2)
    # margin_height = int((original_logo.shape[0] - LOCATION_FACE_HEIGHT) / 2)
    # glo_va.img = original_logo[margin_height:LOCATION_FACE_HEIGHT+margin_height , margin_width:LOCATION_FACE_WIDTH+margin_width]

    # ConvertToDisplay()
    # glo_va.window_GUI['image'].update(data=glo_va.display_image)

    # cv2.imshow('test', display_image)
    # cv2.waitKey(2000)
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