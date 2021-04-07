import numpy as np
import threading, time
from utils.parameters import *
from utils.common_functions import Compose_Embedded_Face
from utils.common_functions import LogMesssage
from assistant.momo_core import MomoCore
from utils.assis_parameters import msg_for_states

def State_1():
    # Read camera
    glo_va.camera.RunCamera()

    # Face detecting
    ret = glo_va.face_recognition.Get_Face()
    if ret == -2:
        LogMesssage("\t[State_1]: Error Face locations", opt=0)
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
        if user_infor.status == glo_va.USER_INFOR_HAS_FACE:
            LogMesssage('\t[State_1]: Patient: {id} has been detected'.format(id=user_infor.patient_ID))
            glo_va.STATE = glo_va.STATE_CONFIRM_PATIENT

            # Clear all previous detected faces
            glo_va.count_face.Clear()

            # Update UI
            request = {'type': glo_va.REQUEST_UPDATE_PATIENT_INFO, 'data': user_infor.user_info}
            glo_va.gui.queue_request_states_thread.put(request)
        elif user_infor.status == glo_va.USER_INFOR_NO_FACE and glo_va.times_missing_face == glo_va.TIMES_MISSING_FACE:
            LogMesssage('\t[State_1]: Patient exceed number of trying identify')
            # Go to state for new User
            # Ask patient to looking up
            glo_va.STATE = glo_va.STATE_CONFIRM_NEW_PATIENT

            # send request data to GUI
            request = {'type': glo_va.REQUEST_CONFIRM_NEW_PATIENT, 'data': ''}
            glo_va.gui.queue_request_states_thread.put(request)
            glo_va.times_missing_face = 0
        else:
            LogMesssage('\t[State_1]: Dummy response from server')

        
        # set parameters for receive response to server. Make sure that there will not has dump response
        glo_va.is_sending_message = False
        glo_va.has_response_server = False
    
    if glo_va.button == glo_va.BUTTON_EXIST:
        LogMesssage('[State_1]: Patient exist program')
        # If user reject, Clear user_infor, Ui and go to first state
        Init_State()
        return

    return

def State_2():
    if glo_va.button == -1:
        return
    # If user confirm, press button 3
    if glo_va.button == glo_va.BUTTON_ACCEPT_CONFIRM_PATIENT:
        LogMesssage('[State_2]: Patient accept information of patient with ID: {id}'.format(id=user_infor.patient_ID))
        # Get and save patient id for examination
        glo_va.patient_ID = user_infor.patient_ID

        # send request clear patient inof
        user_infor.Clear()
        request = {'type': glo_va.REQUEST_CLEAR_PATIENT_INFO, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

        # After user confrim their information, Clear user_infor, Ui and go to STATE measuring sensor
        glo_va.STATE = glo_va.STATE_MEASURE_SENSOR
        # send request change ui
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)
        
        LogMesssage('[State_2]: Clear patient information and screen. Save patient_id detected')
        
        glo_va.button = -1
        return
    
    elif glo_va.button == glo_va.BUTTON_CANCEL_CONFIRM_PATIENT or glo_va.button == glo_va.BUTTON_EXIST:
        LogMesssage('[State_2]: Patient reject information of patient with ID: {id}'.format(id=user_infor.patient_ID))
        # If user reject, Clear user_infor, Ui and go to first state
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

    elif glo_va.button == glo_va.BUTTON_VIEW_LIST_DEP:
        if glo_va.has_examination_room == True:
            glo_va.STATE = glo_va.STATE_VIEW_DEPARTMENTS

            request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
            glo_va.gui.queue_request_states_thread.put(request)
            glo_va.button = -1

            # Clear state momo and Say first word. DO NOT NEED TO CLEAR WHEN RESET
            glo_va.ClearAssisPara()
            # Init MOMO Assistant
            # This thread will end when change to new state which != STATE_VIEW_DEPARTMENTS
            glo_va.thread_assis = threading.Thread(target=MomoCore, args=())
            glo_va.thread_assis.daemon = True
            glo_va.thread_assis.start()
            
            LogMesssage('[State_3]: Patient choose view department')

            return
        
        glo_va.button = -1

    elif glo_va.button == glo_va.BUTTON_SUBMIT_EXAM:
        if exam.status == glo_va.EXAM_HAS_VALUE and sensor.status == glo_va.SENSOR_HAS_VALUE and glo_va.patient_ID is not None:
            glo_va.is_sending_message = False
            glo_va.has_response_server = False
            glo_va.button = -1
            glo_va.STATE = glo_va.STATE_WAITING_SUB_EXAM

            glo_va.timer.Start_Timer(glo_va.OPT_TIMER_SUBMIT_EXAMINATION)
            glo_va.is_sending_message = True
            glo_va.server.Submit_Examination()

            LogMesssage('[State_3]: Patient submit examination and go state waiting for response')
            return
            
        else:
            data = {}
            data['opt'] = 2
            request = {'type': glo_va.REQUEST_NOTIFY_MESSAGE, 'data': data}
            glo_va.gui.queue_request_states_thread.put(request)
            LogMesssage('[State_3]: Patient do not have selected exam room and sensor. Notify for patient')

        # Clear button
        glo_va.button = -1
    elif glo_va.button == glo_va.BUTTON_EXIST:
        LogMesssage('[State_3]: Patient with id: {id} exist program'.format(id=glo_va.patient_ID))
        Init_State()
        return
    elif glo_va.button == glo_va.BUTTON_OKAY:
        glo_va.button = -1
    
    # do not press any thing
    else:
        if glo_va.measuring_sensor == True and glo_va.done_measuring_sensor == True:
            glo_va.measuring_sensor = False
            glo_va.done_measuring_sensor = False
            LogMesssage('[State_3]: Done measure sensor. Init measuring_sensor and done_measuring_sensor flag')

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
            LogMesssage('[State_3]: Has messsage get list examination room')
        
        if glo_va.has_examination_room == False and glo_va.is_sending_message == False:
            LogMesssage('[State_3]: No list examination room. Resend message')
            glo_va.timer.Start_Timer(glo_va.OPT_TIMER_GET_EXAMINATION_ROOM)
            glo_va.is_sending_message = True
            glo_va.server.Get_Examination_Room()
    

def State_4():
    if glo_va.button == glo_va.BUTTON_CONFIRM_DEP:
        glo_va.STATE = glo_va.STATE_MEASURE_SENSOR
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

        LogMesssage('[State_4]: Patient confirm exam room')
        glo_va.button = -1

    elif glo_va.button == glo_va.BUTTON_EXIST:
        LogMesssage('[State_3]: Patient with id: {id} exist program'.format(id=glo_va.patient_ID))
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
        # print(glo_va.list_shape_face[glo_va.current_shape])

        # send request change ui
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)
    
        glo_va.button = -1
        return

    if glo_va.button == glo_va.BUTTON_EXIST:
        # If user reject, Clear user_infor, Ui and go to first state
        LogMesssage('[State_3]: Patient with id: {id} exist program'.format(id=glo_va.patient_ID))
        Init_State()
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
        LogMesssage("Error Face locations", opt=0)
        glo_va.STATE = -1
        return
    elif ret == 0:
        # Face Identifying
        glo_va.face_recognition.Encoding_Face()

        if glo_va.num_user_pose >= 10:
            max_pose = -1
            for i in glo_va.dict_user_pose:
                if glo_va.dict_user_pose[i] > 7 and glo_va.dict_user_pose[i] > max_pose:
                    max_pose = i

            # print("max_pose: {}, current_pose: {}".format(max_pose, glo_va.current_shape))
            # print(glo_va.dict_user_pose)
            
            if max_pose == glo_va.current_shape:
                if glo_va.check_current_shape == False:
                    glo_va.check_current_shape = True
                elif glo_va.check_current_shape == True:
                    glo_va.check_current_shape = False
                    # Activate image in the UI
                    request = {'type': glo_va.REQUEST_ACTIVATE_NEW_FACE, 'data': glo_va.current_shape}
                    glo_va.gui.queue_request_states_thread.put(request)
                    
                    # calculate the mean of all images in one pose
                    mean_embedded_image = np.mean(glo_va.list_embedded_face_origin_new_patient ,axis=0)
                    # save the current embedded face
                    # temp_embedded_face = Compose_Embedded_Face(glo_va.embedded_face)
                    temp_embedded_face = Compose_Embedded_Face(mean_embedded_image)
                    glo_va.list_embedded_face_new_user += temp_embedded_face + ' '

                    # Change to take next pose of user
                    glo_va.current_shape += 1

                    if glo_va.current_shape == glo_va.num_face_new_user:
                        LogMesssage('Done get face new user')
                        glo_va.STATE = glo_va.STATE_MEASURE_SENSOR
                        # send request change ui
                        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
                        glo_va.gui.queue_request_states_thread.put(request)
            else:
                glo_va.check_current_shape = False
        
            
            glo_va.num_user_pose = 0
            glo_va.dict_user_pose = {}
            glo_va.list_embedded_face_origin_new_patient = []
            
    glo_va.gui.image_display = glo_va.img

    return

def State_7():
    if glo_va.button_ok_pressed == True:
        data = {}
        if glo_va.has_response_server == True:
            if glo_va.return_stt is None:
                data['opt'] = 1
                glo_va.valid_stt = -1
            elif glo_va.return_stt is not None:
                dep_name, building, room = exam.Get_Exam_Room_Infor()
                data['opt'] = 0
                data['stt'] = glo_va.return_stt
                data['room'] = '{}-{}'.format(building, room)
                glo_va.valid_stt = 0

            request = {'type': glo_va.REQUEST_NOTIFY_MESSAGE, 'data': data}
            glo_va.gui.queue_request_states_thread.put(request)

            glo_va.button_ok_pressed = False

            glo_va.is_sending_message = False
            glo_va.has_response_server = False

        elif glo_va.has_response_server == False and glo_va.is_sending_message == False:
            data['opt'] = 1
            request = {'type': glo_va.REQUEST_NOTIFY_MESSAGE, 'data': data}
            glo_va.gui.queue_request_states_thread.put(request)

            glo_va.button_ok_pressed = False
    
    elif glo_va.button_ok_pressed == False:
        if glo_va.button == glo_va.BUTTON_OKAY:
            if glo_va.valid_stt == -1:
                glo_va.STATE = glo_va.STATE_MEASURE_SENSOR
                glo_va.button_ok_pressed = True
            elif glo_va.valid_stt == 0:
                Init_State()
                return
                        
            glo_va.valid_stt = None
        else:
            pass
    
    if glo_va.button == glo_va.BUTTON_EXIST:
        # If user reject, Clear user_infor, Ui and go to first state
        Init_State()
        return

    glo_va.button = -1

def Init_State():
    # Lock the response message from server when restart program
    LogMesssage('[Init_State]: Acquire lock init state')
    glo_va.lock_init_state.acquire(True)

    LogMesssage('Reset at STATE: {}'.format(glo_va.STATE))
    # test when state is restarted server accept message or not
    # Clear button
    glo_va.button = -1

    # Clear gui add new user
    request = {'type': glo_va.REQUEST_DEACTIVATE_NEW_FACE, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

    # USER PARAMETERS-----------------------------------------------
    user_infor.Clear()
    # send request clear patient inof
    request = {'type': glo_va.REQUEST_CLEAR_PATIENT_INFO, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

    # Clear list embedded face, embedded face and num images
    glo_va.patient_ID = -1
    glo_va.list_embedded_face_new_user = ""

    glo_va.current_shape = 0
    glo_va.check_current_shape = False

    glo_va.num_user_pose = 0
    glo_va.dict_user_pose = {}
    glo_va.list_embedded_face_origin_new_patient = []

    # EXAMINATION PARAMETERS-----------------------------------------------
    exam.Clear()
    # send request clear exam room, selected room, and dep lsit
    request = {'type': glo_va.REQUEST_CLEAR_EXAM_ROOM, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

    request = {'type': glo_va.REQUEST_CLEAR_SELECTED_EXAM_ROOM, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

    request = {'type': glo_va.REQUEST_CLEAR_DEPARTMENT_LIST, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)
    
    # Clear STT
    glo_va.valid_stt = None
    glo_va.return_stt = None
    glo_va.button_ok_pressed = True
    # Clear patient_Id and list of examination room
    glo_va.hospital_ID = None
    glo_va.list_examination_room = []
    glo_va.has_examination_room = False

    # SENSOR PARAMETERS-----------------------------------------------
    sensor.Clear()
    request = {'type': glo_va.REQUEST_CLEAR_SENSOR, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)

    glo_va.measuring_sensor = False
    glo_va.done_measuring_sensor = False

    # SERVER PARAMETERS-----------------------------------------------
    # Clear timer preveting timeout getting examination room
    glo_va.turn = -1 
    glo_va.timer.Clear_Timer()
    # for server communiation
    glo_va.is_sending_message = False
    glo_va.has_response_server = False

    # STATE 1
    glo_va.STATE = glo_va.STATE_RECOGNIZE_PATIENT
    # send request change ui
    request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)
        
    glo_va.lock_init_state.release()
    LogMesssage('[Init_State]: Release lock init state')