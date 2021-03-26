import numpy as np
import PySimpleGUI as sg
from PIL import Image, ImageTk

from utils.parameters import *

def InitMainGui():
    camera_layout = [[sg.Image(filename='', key='image', size=(glo_va.LOCATION_RECOGNIZE_FACE_WIDTH,glo_va.LOCATION_RECOGNIZE_FACE_HEIGHT), visible=True)],]
    
    take_photo_layout = [[sg.Image(filename='', key='photo_new_user', size=(glo_va.CAM_EXAM_LAYOUT_WIDTH,glo_va.LOCATION_RECOGNIZE_FACE_HEIGHT), visible=True)],]
    
    review_cam_layout = [
        [
            sg.Text('Number of images:', size=(15, 1), justification='left', font='Helvetica 16'),
            sg.Text("0", size=(15, 1), justification='left', font='Helvetica 14', key='-NUM_IMAGES-')
        ],
        [sg.Image(filename='', key='review_photo', size=(glo_va.LOCATION_RECOGNIZE_FACE_WIDTH,glo_va.LOCATION_RECOGNIZE_FACE_HEIGHT), visible=True)],
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
            sg.Column(camera_layout, size=(glo_va.CAM_EXAM_LAYOUT_WIDTH,glo_va.CAM_EXAM_LAYOUT_HEIGHT)), 
            sg.VSeparator(),
            sg.Column(information_layout, size=(glo_va.INFOR_SENSOR_LAYOUT_WIDTH,glo_va.INFOR_SENSOR_LAYOUT_HEIGHT))
        ],
    ]

    layout2 = [
        [
            sg.Column(examination_info, size=(glo_va.CAM_EXAM_LAYOUT_WIDTH,glo_va.CAM_EXAM_LAYOUT_HEIGHT)), 
            sg.VSeparator(),
            sg.Column(sensor_information_layout, size=(glo_va.INFOR_SENSOR_LAYOUT_WIDTH,glo_va.INFOR_SENSOR_LAYOUT_HEIGHT))
        ]
    # create the window and show it without the plot,
    ]

    layout_new_user = [
        [
            sg.Column(review_cam_layout, size=(glo_va.CAM_EXAM_LAYOUT_WIDTH,glo_va.INFOR_SENSOR_LAYOUT_HEIGHT)), 
            sg.VSeparator(),
            sg.Column(take_photo_layout, size=(glo_va.INFOR_SENSOR_LAYOUT_WIDTH,glo_va.INFOR_SENSOR_LAYOUT_HEIGHT))
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

    ret_gui = sg.Window('E-HealthCare System', main_layout, font=('Oswald SemiBold', 20),location=(0, 0), size=(glo_va.WIDTH_GUI, glo_va.HEIGHT_GUI), element_justification='c')
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
            sg.Column(examination_room_layout, size=(glo_va.WIDTH_GUI, 400))
        ],
        [
            sg.Button('Exist', size=(15, 2), font='Helvetica 14', key='exist_exam_room'),
        ]
    ]

    ret_gui = sg.Window('Choose your department', layout_choose_department, font=('Oswald SemiBold', 20),location=(0, 0), size=(glo_va.WIDTH_GUI, glo_va.HEIGHT_GUI), element_justification='c')
    return ret_gui

def isNewUser():
    return sg.popup_yes_no("Are you new user?", title="New user?", font=('Oswald SemiBold', 14),keep_on_top=True)

def popUpWarning(msg):
    return sg.popup(msg, title="Warning?", font=('Oswald SemiBold', 14),keep_on_top=True)

def popUpYesNo(msg):
    return sg.popup_yes_no(msg, title="Question?", font=('Oswald SemiBold', 14),keep_on_top=True)

def Submit_Again():
    return sg.popup('Has error when submit. Please try again.', title="Warning", font=('Oswald SemiBold', 14),keep_on_top=True)
                