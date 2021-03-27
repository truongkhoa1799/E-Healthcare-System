from identifying_users.identifying_users_functions import *
from utils.common_functions import Compose_Embedded_Face
from utils.common_functions import Capture_New_Patient
from utils.parameters import *
import time


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
        
        glo_va.button = -1
        return
    
    elif glo_va.button == glo_va.BUTTON_CANCEL_CONFIRM_PATIENT:
        # If user reject, Clear user_infor, Ui and go to first state
        Init_State()
        return
    
    elif glo_va.button == glo_va.BUTTON_EXIST:
        Init_State()
        return
    

def State_3():
    # print(glo_va.button)
    if glo_va.button == glo_va.BUTTON_CAPTURE_SENSOR:
        glo_va.measuring_sensor = True
        glo_va.done_measuring_sensor = False
        # Clear button
        glo_va.button = -1

        request = {'type': glo_va.REQUEST_MEASURE_SENSOR, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

        # Communicate with ESP to measuring patient information

    elif glo_va.button == glo_va.BUTTON_VIEW_LIST_DEP:
        if glo_va.has_examination_room == True:
            # Clear before get new exam room, easy to check when want to back from state 4
            exam.Clear()
            glo_va.STATE = glo_va.STATE_VIEW_DEPARTMENTS

            request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
            glo_va.gui.queue_request_states_thread.put(request)
            glo_va.button = -1
            return
        
        glo_va.button = -1

    elif glo_va.button == glo_va.BUTTON_SUBMIT_EXAM:
        if exam.status == 0 and sensor.status == 0 and glo_va.patient_ID is not None:
            glo_va.is_sending_message = False
            glo_va.has_response_server = False
            glo_va.button = -1
            glo_va.STATE = glo_va.STATE_WAITING_SUB_EXAM

            glo_va.timer.Start_Timer(glo_va.OPT_TIMER_SUBMIT_EXAMINATION)
            glo_va.is_sending_message = True
            glo_va.server.Submit_Examination()
            return
            
        else:
            message = 'Please capture sensor\ninformation and select\nexamination department'
            request = {'type': glo_va.REQUEST_NOTIFY_MESSAGE, 'data': message}
            glo_va.gui.queue_request_states_thread.put(request)

        # Clear button
        glo_va.button = -1
    elif glo_va.button == glo_va.BUTTON_EXIST:
        Init_State()
        return
    elif glo_va.button == glo_va.BUTTON_OKAY:
        glo_va.button = -1
    else:
        if glo_va.measuring_sensor == True and glo_va.done_measuring_sensor == True:
            glo_va.measuring_sensor = False
            glo_va.done_measuring_sensor = False

        elif glo_va.measuring_sensor == True and glo_va.done_measuring_sensor == False:
            # print('Measuring sensor')
            return
        
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
    

def State_4():
    if exam.status == 0:
        glo_va.STATE = glo_va.STATE_MEASURE_SENSOR
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

    if glo_va.button == glo_va.BUTTON_EXIST:
        Init_State()
        return


def State_5():
    if glo_va.button == -1:
        return

    if glo_va.button == glo_va.BUTTON_DENY_NEW_PATIENT:
        Init_State()
    elif glo_va.button == glo_va.BUTTON_ACCEPT_NEW_PATIENT:
        # Set patient_ID = -1 for new user
        glo_va.patient_ID = -1

        # Set state for next state
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
                glo_va.STATE = glo_va.STATE_MEASURE_SENSOR

                # send request change ui
                request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
                glo_va.gui.queue_request_states_thread.put(request)
            
    glo_va.gui.image_display = glo_va.img

    return

def State_7():
    if glo_va.button_ok_pressed == True:
        if glo_va.has_response_server == True:
            if glo_va.return_stt is None:
                message = 'False to submit examination.\nPlease try again.'
            else:
                message = 'your STT: {}'.format(glo_va.return_stt)

            request = {'type': glo_va.REQUEST_NOTIFY_MESSAGE, 'data': message}
            glo_va.gui.queue_request_states_thread.put(request)

            glo_va.has_response_server = False
            glo_va.is_sending_message = False

            glo_va.button_ok_pressed = False
        elif glo_va.has_response_server == False and glo_va.is_sending_message == False:
            message = 'False to submit examination.\nPlease try again.'
            request = {'type': glo_va.REQUEST_NOTIFY_MESSAGE, 'data': message}
            glo_va.gui.queue_request_states_thread.put(request)
            glo_va.button_ok_pressed = False

            glo_va.has_response_server = False
            glo_va.is_sending_message = False
    
    elif glo_va.button_ok_pressed == False:
        if glo_va.button == glo_va.BUTTON_OKAY:
            if glo_va.return_stt is None:
                glo_va.STATE = glo_va.STATE_MEASURE_SENSOR
                glo_va.button_ok_pressed = True
            elif glo_va.return_stt is not None:
                Init_State()
                return

    glo_va.button = -1

def Init_State():
    print('Reset at STATE: {}'.format(glo_va.STATE))

    # SERVER PARAMETERS-----------------------------------------------
    # Clear timer preveting timeout getting examination room
    glo_va.timer.Clear_Timer()

    # for server communiation
    glo_va.has_response_server = False
    glo_va.is_sending_message = False

    # EXAMINATION PARAMETERS-----------------------------------------------
    exam.Clear()
    # send request clear exam room and dep lsit
    request = {'type': glo_va.REQUEST_CLEAR_EXAM_ROOM, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)
    request = {'type': glo_va.REQUEST_CLEAR_DEPARTMENT_LIST, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)
    
    # Clear STT
    glo_va.return_stt = None
    glo_va.button_ok_pressed = True
    # Clear patient_Id and list of examination room
    glo_va.patient_ID = -1
    glo_va.list_examination_room = []
    glo_va.hospital_ID = None
    glo_va.has_examination_room = False

    # USER PARAMETERS-----------------------------------------------
    user_infor.Clear()
    # send request clear patient inof
    request = {'type': glo_va.REQUEST_CLEAR_PATIENT_INFO, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

    # Clear list embedded face, embedded face and num images
    glo_va.list_embedded_face_new_user = ""
    glo_va.embedded_face_new_user = None

    glo_va.current_shape = 0
    glo_va.user_pose = None

    # SENSOR PARAMETERS-----------------------------------------------
    sensor.Clear()
    request = {'type': glo_va.REQUEST_CLEAR_SENSOR, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

    glo_va.measuring_sensor = False
    glo_va.done_measuring_sensor = False

    # Clear button
    glo_va.button = -1
    
    # STATE 1
    glo_va.STATE = glo_va.STATE_RECOGNIZE_PATIENT
    # send request change ui
    request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

