from CameraDetecting import CameraDetecting
from face_detector_CenterFace import FaceDetector
from FaceIdentifying import FaceIdentify
from CountFace import CountFace
from common_functions import *

import pycuda.driver as cuda
from PIL import Image, ImageTk
import cv2
import time
import PySimpleGUI as sg
import numpy as np
from queue import Queue
from threading import Event, Thread

def InitGUI():
    # sg.theme('Black')

    # define the window layout
    camera_layout = [[sg.Image(filename='', key='image', size=(300,360), visible=True)],]
    information_layout = [
            [sg.Text('Name', size=(40, 1), justification='left', font='Helvetica 20')],
            [sg.Input('Name', size=(50, 1), justification='left', border_width=1, background_color='white', font='Helvetica 15', disabled=True, key='patient_name')],
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

def StartFaceRecognizer():
    print('TrtThread: loading the TRT model...')
    glo_va.cuda_ctx = cuda.Device(0).make_context()  # GPU 0
    print("Load Face Detector model")
    glo_va.face_detector = FaceDetector(landmarks=False)

def StopFaceRecognizer():
    del glo_va.face_detector
    glo_va.cuda_ctx.pop()
    del glo_va.cuda_ctx
    print('TrtThread: stopped...')

def Init():
    # Init face regonizer
    StartFaceRecognizer()
    time.sleep(0.5)

    # Init camera detecting
    glo_va.camera = CameraDetecting()
    time.sleep(0.5)
    
    # Init face identifying
    glo_va.face_identifying = FaceIdentify()
    time.sleep(0.5)
    glo_va.count_face = CountFace()
    # Init GUI
    InitGUI()


def End():
    glo_va.count_face.stop()
    glo_va.window_GUI.close()
    glo_va.camera.StopCamera()
    StopFaceRecognizer()

if __name__ == "__main__":
    Init()
    while True:
        event, values = glo_va.window_GUI.read(timeout=1)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            glo_va.STATE = 2
        elif event == 'Start':
            glo_va.STATE = 1
        try:
            if glo_va.STATE == 1:
                # Read camera
                # time_read_frame = time.time()
                glo_va.camera.RunCamera()
                # print("\tTime to read frame: {}".format(time.time() - time_read_frame))

                # Face detecting
                # time_detecting = time.time()
                LocateFaces()
                # print("\tTime to detect face: {}".format(time.time() - time_detecting))

                # Face Identifying
                # time_identifying = time.time()
                FaceIdentifying()
                # print("\tTime to iden face: {}".format(time.time() - time_identifying))

                face_id, dist = glo_va.face_identifying.GetFaceID()
                if face_id != "Null":
                    glo_va.count_face.CountFace(face_id) 
                # if dist != 0:
                #    print("face id: {} with dist: {}".format(face_id, dist))

                rgb = cv2.cvtColor(glo_va.img, cv2.COLOR_BGR2RGB)  # to RGB
                rgb = Image.fromarray(rgb)  # to PIL format
                rgb = ImageTk.PhotoImage(rgb)  # to ImageTk format
                glo_va.window_GUI['image'].update(data=rgb)

            elif glo_va.STATE == 2:
                End()
                break
            
        except Exception as e:
            print(e)
            End()
            break
    print("Turn off E-Healthcare system")