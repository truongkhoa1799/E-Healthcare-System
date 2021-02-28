import cv2
import numpy as np
import PySimpleGUI as sg
from PIL import Image, ImageTk

from utils.parameters import *
    
def ConvertToDisplay(image):
    display_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # to RGB
    display_image = Image.fromarray(display_image)  # to PIL format
    display_image = ImageTk.PhotoImage(display_image)  # to ImageTk format
    return display_image

def InitMainGui():
    camera_layout = [[sg.Image(filename='', key='image', size=(LOCATION_FACE_WIDTH,LOCATION_FACE_HEIGHT), visible=True)],]
    
    take_photo_layout = [[sg.Image(filename='', key='photo_new_user', size=(CAM_EXAM_LAYOUT_WIDTH,LOCATION_FACE_HEIGHT), visible=True)],]
    
    review_cam_layout = [
        [
            sg.Text('Number of images:', size=(15, 1), justification='left', font='Helvetica 16'),
            sg.Text("0", size=(15, 1), justification='left', font='Helvetica 14', key='-NUM_IMAGES-')
        ],
        [sg.Image(filename='', key='review_photo', size=(LOCATION_FACE_WIDTH,LOCATION_FACE_HEIGHT), visible=True)],
    ]

    examination_info = [
        [sg.Text('NOTE: Please put your hand on sensors\nand press "Measure\" button', size=(50, 4),border_width=1, justification='left', text_color='red', font='Helvetica 13')],
    
        [sg.Text('Department', size=(35, 1), justification='left', font='Helvetica 15')],
        [sg.Text("None", size=(35, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-DEPARTMENT-', text_color='black')],
        [sg.Text('\nRoom', size=(35, 2), justification='left', font='Helvetica 15')],
        [sg.Text("None", size=(35, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-ROOM-', text_color='black')],
        [sg.Text('\nMeasuring sensor', size=(35, 2), justification='left', font='Helvetica 15')],
        [sg.ProgressBar(100, orientation='h', size=(32, 15), key='sensor_progress')],
    ]
    
    information_layout = [
        [sg.Text('Name', size=(35, 1), justification='left', font='Helvetica 15')],
        [sg.Text("None", size=(35, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-NAME-', text_color='black')],
        [sg.Text('\nBirth Date', size=(35, 2), justification='left', font='Helvetica 15')],
        [sg.Text("None", size=(35, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-BD-', text_color='black')],
        [sg.Text('\nPhone', size=(35, 2), justification='left', font='Helvetica 15')],
        [sg.Text("None", size=(35, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-PHONE-', text_color='black')],
        [sg.Text('\nAddress', size=(35, 2), justification='left', font='Helvetica 15')],
        [sg.Text("None", size=(35, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-ADDRESS-', text_color='black')],
    ]
    sensor_information_layout = [
        [sg.Text('Blood Pressure', size=(35, 1), justification='left', font='Helvetica 15')],
        [sg.Text("None", size=(35, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-BLOOD_PRESSURE-', text_color='black')],
        [sg.Text('\nPulse Sensor', size=(35, 2), justification='left', font='Helvetica 15')],
        [sg.Text("None", size=(35, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-PULSE-', text_color='black')],
        [sg.Text('\nThermal Sensor', size=(35, 2), justification='left', font='Helvetica 15')],
        [sg.Text("None", size=(35, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-THERMAL-', text_color='black')],
        [sg.Text('\nSPO2', size=(35, 2), justification='left', font='Helvetica 15')],
        [sg.Text("None", size=(35, 1), justification='left', border_width=1, background_color='white', font='Helvetica 14', key='-SPO2-', text_color='black')],
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
        ]
    # create the window and show it without the plot,
    ]

    layout_new_user = [
        [
            sg.Column(review_cam_layout, size=(CAM_EXAM_LAYOUT_WIDTH,INFOR_SENSOR_LAYOUT_HEIGHT)), 
            sg.VSeparator(),
            sg.Column(take_photo_layout, size=(INFOR_SENSOR_LAYOUT_WIDTH,INFOR_SENSOR_LAYOUT_HEIGHT))
        ],
    ]

    main_layout = [
        [sg.Text('Smart E-Healthcare', size=(40, 1), justification='center', font='Helvetica 20')],
        [
            sg.Column(layout1, visible=True, key='-COL1-'),
            sg.Column(layout2, visible=False, key='-COL2-'),
            sg.Column(layout_new_user, visible=False, key='-COL3-'),
        ], 
        [
            sg.Button('Exist', size=(15, 1), font='Helvetica 14', key='exist'),
            sg.Button('Reject', size=(15, 1), font='Helvetica 14', key='button_2'),
            sg.Button('Confirm', size=(34, 1), font='Helvetica 14', key='button_3'),
        ],
    ]

    ret_gui = sg.Window('E-HealthCare System', main_layout, font=('Oswald SemiBold', 20),location=(400, 400), size=(WIDTH_GUI, HEIGHT_GUI), element_justification='c')
    print("OPENED GUI")
    return ret_gui

def Render_Examanination_Room_Table():
    size_row = -1
    list_keys = list(glo_va.map_num_departments.keys())
    first_key = list_keys[0]
    if len(glo_va.list_examination_room) <= first_key:
        size_row = first_key
    else:
        for i in range(1, len(list_keys)):
            if size_row < len(glo_va.list_examination_room) and len(glo_va.list_examination_room) <= list_keys[i]:
                size_row = list_keys[i]
                break
    
    if size_row == -1:
        size_row = list_keys[-1]
    
    # print(len(glo_va.list_examination_room))
    # print(size_row)
    
    examination_room_layout = []
    rows = (len(glo_va.list_examination_room) // 3) + 1
    for i in range(rows):
        temp_1 = []
        for j in range(3):
            if i*3 + j < len(glo_va.list_examination_room):
                name = glo_va.list_examination_room[i*3 + j]['dep_name'] + '\n'+ str(glo_va.list_examination_room[i*3 + j]['dep_ID'])
                temp_1.append(sg.Button(f'{name}', size=(22, glo_va.map_num_departments[size_row]), font='Helvetica 14'))
        examination_room_layout.append(temp_1)
    
    layout_choose_department = [
        [
            sg.Column(examination_room_layout, size=(WIDTH_GUI, 400))
        ],
        [
            sg.Button('Exist', size=(15, 2), font='Helvetica 14', key='exist_exam_room'),
        ]
    ]

    ret_gui = sg.Window('Choose your department', layout_choose_department, font=('Oswald SemiBold', 20),location=(400, 400), size=(WIDTH_GUI, HEIGHT_GUI), element_justification='c')
    return ret_gui

def Locating_Faces():
    face_area = 0
    max_face_area = 0

    if glo_va.img is not None:
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

def isNewUser():
    return sg.popup_yes_no("Are you new user?", title="New user?", font=('Oswald SemiBold', 14),keep_on_top=True)

def popUpWarning(msg):
    return sg.popup(msg, title="Warning?", font=('Oswald SemiBold', 14),keep_on_top=True)

def popUpYesNo(msg):
    return sg.popup_yes_no(msg, title="Question?", font=('Oswald SemiBold', 14),keep_on_top=True)