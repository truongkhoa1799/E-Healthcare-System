from identifying_users.identifying_users_functions import *
from utils.common_functions import Compose_Embedded_Face
from utils.parameters import *
import time

# Button: Exist, reject, Confirm
#           1       2       3
def State_1():
    # Read camera
    glo_va.camera.RunCamera()

    # Face detecting
    ret = Locating_Faces()
    if ret == -2:
        print("Error Face locations")
        glo_va.STATE = -1
        return
    elif ret == 0:
        # Face Identifying
        glo_va.face_recognition.Encoding_Face()
        glo_va.count_face.Count_Face()

    display_image = ConvertToDisplay(glo_va.img)
    glo_va.window_GUI['image'].update(data=display_image)

    if glo_va.has_response_server == True:
        if user_infor.Get_Status() == 0:
            glo_va.STATE = 2

            # Clear all previous detected faces
            glo_va.count_face.Clear()

            # Update UI
            user_infor.Update_Screen()
        elif user_infor.Get_Status() == -1 and glo_va.times_missing_face == TIMES_MISSING_FACE:
            # Go to state for new User
            glo_va.STATE = 5
            glo_va.times_missing_face = 0
        
        # set parameters for receive response to server. Make sure that there will not has dump response
        glo_va.is_sending_message = False
        glo_va.has_response_server = False

    return

def State_2(event):
    # If user confirm, press button 3
    if event == 'button_3':
        glo_va.window_GUI[f'-COL2-'].update(visible=True)
        glo_va.window_GUI[f'-COL1-'].update(visible=False)

        # Get and save patient id for examination
        glo_va.patient_ID = user_infor.patient_ID

        # Change Button 3 from Confirm to Measure
        #        Button 2 from reject to Confirm
        glo_va.window_GUI['button_3'].update('Measure')
        glo_va.window_GUI['button_2'].update('Confirm')

        # After user confrim their information, Clear user_infor, Ui and go to STATE measuring sensor
        user_infor.Clear()
        user_infor.Update_Screen()
        glo_va.STATE = 3
    elif event == 'button_2':
        # If user reject, Clear user_infor, Ui and go to first state
        Init_State()
    elif event == 'exist':
        ret = popUpYesNo('Are you sure?')
        if ret == 'Yes':
            Init_State()

# Button: Exist, Confirm, measure
#           1       2       3
def State_3(event):
    if event == 'button_3':
        glo_va.measuring_sensor = True
        # Communicate with ESP to measuring patient information
    # When user press confirm, check:
    #   1: whether Jetson has sensor values or not
    #   2: whether Jetson has examination room or not
    elif event == 'button_2':
        if glo_va.has_examination_room == True and glo_va.has_sensor_values == True:
            glo_va.STATE = 4
            # turn of parameters communication with server
            glo_va.has_response_server = False
            glo_va.is_sending_message = False
            glo_va.has_examination_room = False

            # Has sensor parameters
            glo_va.has_sensor_values = False
            glo_va.measuring_sensor = False

            # open examination room layout
            glo_va.examination_GUI = Render_Examanination_Room_Table()
        else:
            if glo_va.has_sensor_values == False:
                popUpWarning('You did not have sensor results yet')
    elif event == 'exist':
        ret = popUpYesNo('Are you sure?')
        if ret == 'Yes':
            Init_State()
    
    if glo_va.measuring_sensor == True:
        # Read the signal from ESP with loop 1s to check whether they has values or not
        progress_bar = glo_va.window_GUI.FindElement('sensor_progress')
        for i in range(10):
            progress_bar.UpdateBar(10*(i+1), 100)
            time.sleep(1)
        sensor_info = {'blood_pressure': 120, 'pulse':98, 'thermal':38, 'spo2':90}
        sensor.Update_Sensor(sensor_info)
        sensor.Update_Screen()

        # If ESP has values, enable flag has values
        glo_va.measuring_sensor = False
        glo_va.has_sensor_values = True
    
    if glo_va.has_response_server == True:
        if glo_va.has_examination_room == False:
            glo_va.timer.Start_Timer(OPT_TIMER_GET_EXAMINATION_ROOM)
            glo_va.has_response_server = False
            glo_va.is_sending_message = True
            glo_va.server.Get_Examination_Room()
    
    if glo_va.is_sending_message == False and glo_va.has_examination_room == False and glo_va.STATE == 3:
        glo_va.timer.Start_Timer(OPT_TIMER_GET_EXAMINATION_ROOM)
        glo_va.is_sending_message = True
        glo_va.server.Get_Examination_Room()

def State_4(event):
    if event != '__TIMEOUT__' and event != sg.WIN_CLOSED and event != 'exist_exam_room':
        temp = event.split('\n')
        msg = 'You chose department {}.\nAre you sure?'.format(temp[0])
        answer = popUpYesNo(msg)
        if answer == 'Yes':
            glo_va.dep_ID_chosen = temp[-1]
            glo_va.STATE = 7

            # Change Button 3 from Measure to Submit
            #        Button 2 from Confirm to Back
            glo_va.window_GUI['button_3'].update('Submit')
            glo_va.window_GUI['button_2'].update('Back')

            # Get room and department for updating Examination
            room = ""
            for i in glo_va.list_examination_room:
                if i['dep_ID'] == int(glo_va.dep_ID_chosen):
                    room = i['building_code'] + '-' + i['room_code']
            # Update department and room on UI
            exam.Update_Examination({'dep':temp[0],'room':room})
            exam.Update_Screen()

            # Clear examination room layout
            glo_va.examination_GUI.close()
            glo_va.examination_GUI = None
    elif event == 'exist_exam_room':
        ret = popUpYesNo('Are you sure?')
        if ret == 'Yes':
            Init_State()

def State_5(event):
    if isNewUser() == 'No':
        glo_va.STATE = 1
    else:
        glo_va.STATE = 6
        glo_va.window_GUI[f'-COL3-'].update(visible=True)
        glo_va.window_GUI[f'-COL1-'].update(visible=False)
    
    if event == 'exist':
        ret = popUpYesNo('Are you sure?')
        if ret == 'Yes':
            Init_State()

def State_6(event):
    if event == 'button_3':
        glo_va.embedded_face_new_user = glo_va.embedded_face
        review_image = cv2.resize(glo_va.detected_face, (300,300))
        display_review_image = ConvertToDisplay(review_image)
        glo_va.window_GUI['review_photo'].update(data=display_review_image)
        glo_va.has_capture = True
    elif event == 'Confirm' and glo_va.has_capture == True:
        temp_embedded_face = Compose_Embedded_Face(glo_va.embedded_face_new_user)
        glo_va.list_embedded_face_new_user += temp_embedded_face + ' '
        glo_va.num_images_new_user += 1
        glo_va.has_capture = False
        glo_va.window_GUI['review_photo'].update('')
        if glo_va.num_images_new_user == 5:
            glo_va.START == 7
        glo_va.window_GUI['-NUM_IMAGES-'].update(str(glo_va.num_images_new_user))
    elif event == 'exist':
        ret = popUpYesNo('Are you sure?')
        if ret == 'Yes':
            Init_State()

    # Read camera
    glo_va.camera.RunCamera()

    # # Face detecting
    ret = Locating_Faces()
    if ret == -2:
        print("Error Face locations")
        glo_va.STATE = -1
        return
    elif ret == 0:
        # Face Identifying
        glo_va.face_recognition.Encoding_Face()

    display_image_new_user = ConvertToDisplay(glo_va.img)
    glo_va.window_GUI['photo_new_user'].update(data=display_image_new_user)

# Button: Exist, Back, Submit
#           1       2       3
def State_7(event):
    if event == 'button_2':
        # Clear current Examination and go back state 4
        exam.Clear()
        exam.Update_Screen()

        glo_va.STATE = 4
        glo_va.examination_GUI = Render_Examanination_Room_Table()
    elif event == 'exist':
        ret = popUpYesNo('Are you sure?')
        if ret == 'Yes':
            Init_State()
    elif event == 'button_3' and glo_va.is_sending_message == False:
        ret = popUpYesNo('Are you sure?')
        if ret == 'Yes':
            glo_va.timer.Start_Timer(OPT_TIMER_SUBMIT_EXAMINATION)
            glo_va.is_sending_message = True
            glo_va.server.Submit_Examination()
    
    if glo_va.has_response_server == True:
        if glo_va.return_stt is not None:
            print(glo_va.return_stt)
            time.sleep(5)
            glo_va.STATE = -1
        else:
            ret = Submit_Again()
            glo_va.is_sending_message = False

    # time.sleep(1)

def Init_State():
    if glo_va.STATE == 1:
        return
    elif glo_va.STATE == 2:
        # If user reject, Clear user_infor, Ui and go to first state
        user_infor.Clear()
        user_infor.Update_Screen()
        glo_va.patient_ID = None

        # State 1
        glo_va.STATE = 1
    elif glo_va.STATE == 3:
        # Clear timer preveting timeout getting examination room
        glo_va.timer.Clear_Timer()

        # for server communiation
        glo_va.has_response_server = False
        glo_va.is_sending_message = False

        # For sensor
        glo_va.measuring_sensor = False
        glo_va.has_sensor_values = False

        # Clear sensor values
        sensor.Clear()
        sensor.Update_Screen()
        progress_bar = glo_va.window_GUI.FindElement('sensor_progress')
        progress_bar.UpdateBar(0)

        # For examination
        glo_va.patient_ID = None
        glo_va.list_examination_room = []
        glo_va.hospital_ID = None
        glo_va.has_examination_room = False

        # Set Ui for STATE 1
        glo_va.STATE = 1
        glo_va.window_GUI[f'-COL1-'].update(visible=True)
        glo_va.window_GUI[f'-COL2-'].update(visible=False)
    elif glo_va.STATE == 4:
        # Clear examination room layout
        glo_va.examination_GUI.close()
        glo_va.examination_GUI = None

        # Clear sensor values
        sensor.Clear()
        sensor.Update_Screen()
        progress_bar = glo_va.window_GUI.FindElement('sensor_progress')
        progress_bar.UpdateBar(0)

        # Clear patient_Id and list of examination room
        glo_va.patient_ID = None
        glo_va.list_examination_room = []
        glo_va.hospital_ID = None

        # STATE 1
        glo_va.STATE = 1
        glo_va.window_GUI[f'-COL1-'].update(visible=True)
        glo_va.window_GUI[f'-COL2-'].update(visible=False)
    elif glo_va.STATE == 6:
        glo_va.list_embedded_face_new_user = ""
        glo_va.embedded_face_new_user = None
        glo_va.num_images_new_user = 0
        glo_va.has_capture = False

        glo_va.window_GUI['review_photo'].update('')
        glo_va.window_GUI['-NUM_IMAGES-'].update(str(glo_va.num_images_new_user))
        glo_va.window_GUI['photo_new_user'].update(data='')

        glo_va.STATE = 1
        glo_va.window_GUI[f'-COL1-'].update(visible=True)
        glo_va.window_GUI[f'-COL3-'].update(visible=False)
    elif glo_va.STATE == 7:
        # Clear sensor values
        sensor.Clear()
        sensor.Update_Screen()
        progress_bar = glo_va.window_GUI.FindElement('sensor_progress')
        progress_bar.UpdateBar(0)

        # Clear patient_ID and list of examination room
        glo_va.patient_ID = None
        glo_va.hospital_ID = None
        glo_va.list_examination_room = []

        # Clear Examination
        exam.Clear()
        exam.Update_Screen()

        # Set Ui for STATE 1
        glo_va.STATE = 1
        glo_va.window_GUI[f'-COL1-'].update(visible=True)
        glo_va.window_GUI[f'-COL2-'].update(visible=False)

    # config button at STATE 1
    glo_va.window_GUI['button_3'].update('Confirm')
    glo_va.window_GUI['button_2'].update('Reject')

