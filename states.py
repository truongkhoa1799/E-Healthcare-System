from identifying_users.identifying_users_functions import *
from utils.common_functions import Compose_Embedded_Face
from utils.common_functions import Capture_New_Patient
# from utils.common_functions import ConvertToDisplay
# from utils.common_functions import UpdateImage
from utils.parameters import *
import time

# Button: Exist, reject, Confirm
#           1       2       3
def State_1():
    # Read camera
    glo_va.camera.RunCamera()

    # Face detecting
    ret = glo_va.face_recognition.Get_Face()
    if ret == -2:
        print("Error Face locations")
        glo_va.STATE = -1
        return
    elif ret == 0:
        # Face Identifying
        glo_va.face_recognition.Encoding_Face()
        glo_va.count_face.Count_Face()

    # display_image = ConvertToDisplay(glo_va.img)
    # glo_va.window_GUI['image'].update(data=display_image)

    # Update image to display
    glo_va.gui.image_display = glo_va.img

    # If has_response_server:
    #   1. Has user information:
    #       change to state 2
    #       Clear all face detected in disk
    #   2. Do not has face
    #       If number missing faces > threshold
    #           Ask for new user
    #   3. Set flag is_sending_message and has_response_server = False
    if glo_va.has_response_server == True:
        if user_infor.status == 0:
            glo_va.STATE = glo_va.STATE_CONFIRM_PATIENT

            # Clear all previous detected faces
            glo_va.count_face.Clear()

            # Update UI
            request = {'type': glo_va.REQUEST_UPDATE_PATIENT_INFO, 'data': user_infor.user_info}
            glo_va.gui.queue_request_states_thread.put(request)
        elif user_infor.status == -1 and glo_va.times_missing_face == glo_va.TIMES_MISSING_FACE:
            # Go to state for new User
            # Ask patient to looking up
            glo_va.STATE = glo_va.STATE_CONFIRM_NEW_PATIENT

            # send request data to GUI
            request = {'type': glo_va.REQUEST_CONFIRM_NEW_PATIENT, 'data': ''}
            glo_va.gui.queue_request_states_thread.put(request)
            glo_va.times_missing_face = 0
        
        # set parameters for receive response to server. Make sure that there will not has dump response
        glo_va.is_sending_message = False
        glo_va.has_response_server = False

    return

def State_2():
    if glo_va.button == -1:
        return
    # If user confirm, press button 3
    if glo_va.button == glo_va.BUTTON_ACCEPT_CONFIRM_PATIENT:
        # Get and save patient id for examination
        glo_va.patient_ID = user_infor.patient_ID

        # After user confrim their information, Clear user_infor, Ui and go to STATE measuring sensor

        glo_va.STATE = glo_va.STATE_MEASURE_SENSOR

        # send request clear patient inof
        user_infor.Clear()
        request = {'type': glo_va.REQUEST_CLEAR_PATIENT_INFO, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

        # send request change ui
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)
    
    elif glo_va.button == glo_va.BUTTON_CANCEL_CONFIRM_PATIENT:
        # If user reject, Clear user_infor, Ui and go to first state
        Init_State()
        return
    
    elif glo_va.button == glo_va.BUTTON_EXIST:
        Init_State()
        return
    
    glo_va.button = -1

# Button: Exist, Confirm, measure
#           1       2       3
def State_3():
    # print(glo_va.button)
    if glo_va.button == glo_va.BUTTON_CAPTURE_SENSOR:
        glo_va.measuring_sensor = True
        # Communicate with ESP to measuring patient information

    # When user press confirm, check:
    #   1: whether Jetson has sensor values or not
    #   2: whether Jetson has examination room or not
    elif glo_va.button == glo_va.BUTTON_VIEW_LIST_DEP:
        print('Hello')
        if glo_va.has_examination_room == True:
            # Clear before get new exam room, easy to check when want to back from state 4
            exam.Clear()
            glo_va.STATE = glo_va.STATE_VIEW_DEPARTMENTS
            # turn of parameters communication with server
            # glo_va.has_response_server = False
            # glo_va.is_sending_message = False
            # glo_va.has_examination_room = False

            # # Has sensor parameters
            # glo_va.has_sensor_values = False
            # glo_va.measuring_sensor = False

            # # open examination room layout
            # glo_va.examination_GUI = Render_Examanination_Room_Table()

            # If you do not return, it will send request for get examination room
            # in the below code

            request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
            glo_va.gui.queue_request_states_thread.put(request)
            glo_va.button = -1
            return
        # else:
        #     if glo_va.has_sensor_values == False:
        #         popUpWarning('You did not have sensor results yet')
    elif glo_va.button == glo_va.BUTTON_SUBMIT_EXAM:
        if exam.status == 0 and sensor.status == 0 and patient_ID is not None:
            print('send exam')
    elif glo_va.button == glo_va.BUTTON_EXIST:
        Init_State()
        # If you do not return, it will send request for get examination room
        # in the below code
        return
    
    if glo_va.measuring_sensor == True:
        # Read the signal from ESP with loop 1s to check whether they has values or not
        # progress_bar = glo_va.window_GUI.FindElement('sensor_progress')
        # for i in range(10):
        #     progress_bar.UpdateBar(10*(i+1), 100)
        #     time.sleep(1)
        # sensor_info = {'blood_pressure': 120, 'pulse':98, 'thermal':38, 'spo2':90}
        # sensor.Update_Sensor(sensor_info)
        # sensor.Update_Screen()
        print('Measuring sensor')

        # If ESP has values, enable flag has values
        glo_va.measuring_sensor = False

        sensor_info = {'blood_pressure': 120, 'heart_pulse':98, 'temperature':38, 'spo2':90, 'height': 1.78, 'weight': 78}
        sensor.Update_Sensor(sensor_info)
        request = {'type': glo_va.REQUEST_UPDATE_SENSOR, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)
    
    # If has_response_server:
    #   1. Has examination room:
    #       
    #   2. Do not has examination room
    #        = False. Therefore, next execution will send again message
    #   3. Set has_response_server and is_sending_message = False
    if glo_va.has_response_server == True:        
        glo_va.is_sending_message = False
        glo_va.has_response_server = False
    
    if glo_va.has_examination_room == False and glo_va.is_sending_message == False:
        glo_va.timer.Start_Timer(glo_va.OPT_TIMER_GET_EXAMINATION_ROOM)
        glo_va.is_sending_message = True
        glo_va.server.Get_Examination_Room()
    
    # Clear button
    glo_va.button = -1

def State_4():
    if exam.status == 0:
        glo_va.STATE = glo_va.STATE_MEASURE_SENSOR
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

    if glo_va.button == glo_va.BUTTON_EXIST:
        Init_State()
        return

    glo_va.button = -1
    return

def State_5():
    if glo_va.button == -1:
        return

    if glo_va.button == glo_va.BUTTON_DENY_NEW_PATIENT:
        Init_State()
    elif glo_va.button == glo_va.BUTTON_ACCEPT_NEW_PATIENT:
        glo_va.STATE = glo_va.STATE_NEW_PATIENT
        print(glo_va.list_shape_face[glo_va.current_shape])

        # send request change ui
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)
    
    glo_va.button = -1
    return

def State_6():
    if glo_va.button == glo_va.BUTTON_EXIST:
        Init_State()
        return

    # Read camera
    glo_va.camera.RunCamera()

    # Face detecting
    ret = glo_va.face_recognition.Get_Face()
    if ret == -2:
        print("Error Face locations")
        glo_va.STATE = -1
        return
    elif ret == 0:
        # Face Identifying
        glo_va.face_recognition.Encoding_Face()
    
        if glo_va.user_pose == glo_va.current_shape:
            # Activate image in the UI
            request = {'type': glo_va.REQUEST_ACTIVATE_NEW_FACE, 'data': glo_va.current_shape}
            glo_va.gui.queue_request_states_thread.put(request)

            # save the current embedded face
            temp_embedded_face = Compose_Embedded_Face(glo_va.embedded_face)
            glo_va.list_embedded_face_new_user += temp_embedded_face + ' '

            # Change to take next pose of user
            glo_va.current_shape += 1

            if glo_va.current_shape == glo_va.num_face_new_user:
                print('Done get face new user')
                # Change layout
                # glo_va.window_GUI[f'-COL2-'].update(visible=True)
                # glo_va.window_GUI[f'-COL3-'].update(visible=False)

                # # Change Button 3 from Confirm to Measure
                # #        Button 2 from reject to Confirm
                # glo_va.window_GUI['button_3'].update('Measure')
                # glo_va.window_GUI['button_2'].update('Confirm')
                glo_va.STATE = glo_va.STATE_MEASURE_SENSOR

                # send request change ui
                request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
                glo_va.gui.queue_request_states_thread.put(request)
            
    #         # Ask patient to add new face
    #         else:
    #             print(glo_va.list_shape_face[glo_va.current_shape])

    # Update image to display
    glo_va.gui.image_display = glo_va.img

    return


# Button: Exist, Back, Submit
#           1       2       3
def State_7(event):
    if event == 'button_2':
        # Clear current Examination and go back state 4
        exam.Clear()
        exam.Update_Screen()

        glo_va.STATE = 4
        glo_va.examination_GUI = Render_Examanination_Room_Table()
        return
    elif event == 'exist':
        ret = popUpYesNo('Are you sure?')
        if ret == 'Yes':
            Init_State()
            return
    elif event == 'button_3' and glo_va.is_sending_message == False:
        ret = popUpYesNo('Are you sure?')
        if ret == 'Yes':
            glo_va.timer.Start_Timer(glo_va.OPT_TIMER_SUBMIT_EXAMINATION)
            glo_va.is_sending_message = True
            glo_va.server.Submit_Examination()
    
    if glo_va.has_response_server == True:
        if glo_va.return_stt is not None:
            ret = popUpWarning("Your STT: {}, at room: {}".format(glo_va.return_stt, exam.Get_Room()))
            Init_State()
            return
        else:
            ret = Submit_Again()
            glo_va.is_sending_message = False
            glo_va.has_response_server = False

    # time.sleep(1)

def Init_State():
    print('Reset at STATE: {}'.format(glo_va.STATE))
    if glo_va.STATE == glo_va.STATE_MEASURE_SENSOR:
        # Clear timer preveting timeout getting examination room
        glo_va.timer.Clear_Timer()

        # Clear sensor values
        # sensor.Clear()
        # sensor.Update_Screen()
        # progress_bar = glo_va.window_GUI.FindElement('sensor_progress')
        # progress_bar.UpdateBar(0)
    elif glo_va.STATE == glo_va.STATE_VIEW_DEPARTMENTS:
        # Clear examination room layout
        # glo_va.examination_GUI.close()
        # glo_va.examination_GUI = None

        # # Clear sensor values
        # sensor.Clear()
        # sensor.Update_Screen()
        # progress_bar = glo_va.window_GUI.FindElement('sensor_progress')
        # progress_bar.UpdateBar(0)
        print('gele')

    elif glo_va.STATE == 7:
        # Clear sensor values
        # sensor.Clear()
        # sensor.Update_Screen()
        # progress_bar = glo_va.window_GUI.FindElement('sensor_progress')
        # progress_bar.UpdateBar(0)


        # Clear Examination
        # exam.Clear()
        # exam.Update_Screen()


        print('gele')

    # Clear sensor, exam and patient
    exam.Clear()
    # send request clear exam room and dep lsit
    request = {'type': glo_va.REQUEST_CLEAR_EXAM_ROOM, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)
    request = {'type': glo_va.REQUEST_CLEAR_DEPARTMENT_LIST, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

    user_infor.Clear()
    # send request clear patient inof
    request = {'type': glo_va.REQUEST_CLEAR_PATIENT_INFO, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

    sensor.Clear()
    request = {'type': glo_va.REQUEST_CLEAR_SENSOR, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

    # Clear list embedded face, embedded face and num images
    glo_va.list_embedded_face_new_user = ""
    glo_va.embedded_face_new_user = None
    glo_va.has_capture = False

    glo_va.current_shape = 0
    glo_va.user_pose = None

    # for server communiation
    glo_va.has_response_server = False
    glo_va.is_sending_message = False

    # For sensor
    glo_va.measuring_sensor = False

    # Clear patient_Id and list of examination room
    glo_va.patient_ID = None
    glo_va.list_examination_room = []
    glo_va.hospital_ID = None
    glo_va.has_examination_room = False

    # Clear STT
    glo_va.return_stt = None

    # Clear button
    glo_va.button = -1
    
    # STATE 1
    glo_va.STATE = glo_va.STATE_RECOGNIZE_PATIENT
    # send request change ui
    request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

