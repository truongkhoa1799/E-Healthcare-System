import cv2
import numpy as np
import threading, time
from utils.parameters import *
from sensor.measure_sensors import MeasureSensor
from utils.common_functions import LogMesssage
from utils.common_functions import Compose_Embedded_Face

########################################################
# IDENTIFYING PATIENT                                  #
########################################################
def State_1():
    # Read camera
    glo_va.camera.RunCamera()

    if glo_va.img is not None: face_locations = glo_va.centerface_detector(glo_va.img, glo_va.img.shape[0], glo_va.img.shape[1])
    else:
        return

    if len(face_locations) == 1:
        ret, location_detected_face = glo_va.face_recognition.Get_Location_Face(face_locations)
        if ret == -2:
            LogMesssage("[states_State_1]: Error Face locations", opt=0)
            Init_State()
            return

        elif ret == 0:
            # Face Identifying
            # detected_face = img[top: bottom, left: right]
            detected_face = glo_va.img[location_detected_face[0] : location_detected_face[1], location_detected_face[2] : location_detected_face[3]]
            
            # cv2.rectangle(glo_va.img, (left, top), (right, bottom) , (2, 255, 0), 2)
            cv2.rectangle(glo_va.img, (location_detected_face[2], location_detected_face[0]), (location_detected_face[3], location_detected_face[1]) , (2, 255, 0), 2)

            embedded_face = glo_va.face_recognition.Encoding_Face(detected_face)
            glo_va.count_face.Count_Face(embedded_face)
        
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
            LogMesssage('[states_State_1]: Patient: {id} has been detected'.format(id=user_infor.patient_ID))
            glo_va.STATE = glo_va.STATE_CONFIRM_PATIENT
            
            request = {'type': glo_va.REQUEST_UPDATE_PATIENT_INFO, 'data': user_infor.user_info}
            glo_va.gui.queue_request_states_thread.put(request)

            glo_va.camera.currentStopCamera()

            # MOMO saying
            glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_confirm'])

        elif user_infor.status == glo_va.USER_INFOR_NO_FACE and glo_va.times_missing_face == glo_va.NUM_MISSING_FACE:
            LogMesssage('[states_State_1]: Patient exceed number of trying identify')
            glo_va.STATE = glo_va.STATE_CONFIRM_NEW_PATIENT

            request = {'type': glo_va.REQUEST_CONFIRM_NEW_PATIENT, 'data': ''}
            glo_va.gui.queue_request_states_thread.put(request)

            glo_va.camera.currentStopCamera()

            # MOMO saying
            glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_new_patient'])
            glo_va.times_missing_face = 0

        elif user_infor.status == glo_va.USER_INFOR_WEARING_MASK:
            glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_take_of_mask'])
            LogMesssage('[states_State_1]: Patient is asked to take of mask')

            glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_take_of_mask'])
            time.sleep(2)
        
        # Clear all previous detected faces  
        glo_va.count_face.Clear()

        # set parameters for receive response to server. Make sure that there will not has dump response
        glo_va.is_sending_message = False
        glo_va.has_response_server = False
    
    if glo_va.button == glo_va.BUTTON_EXIST:
        LogMesssage('[states_State_1]: Patient exist program')
        Init_State()

############################################################
# CONFIRMING PATIENT'S INFORMATION                         #
############################################################
def State_2():
    ########################################################
    # ACCEPT PATIENT'S INFORMATION                         #
    ########################################################
    if glo_va.button == glo_va.BUTTON_ACCEPT_CONFIRM_PATIENT:
        glo_va.button = glo_va.DEFAULT_BUTTON

        LogMesssage('[states_State_2]: Patient accept information of patient with ID: {id}'.format(id=user_infor.patient_ID))

        # After user confrim their information, Clear user_infor, Ui and go to STATE measuring sensor
        glo_va.STATE = glo_va.STATE_MEASURE_SENSOR
        # send request change ui
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)
        
        # MOMO saying
        glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_choose_dep_frame'])

        LogMesssage('[states_State_2]: Clear patient information and screen. Save patient_id detected')
    
    ########################################################
    # CANCEL PATIENT'S INFORMATION                         #
    ########################################################
    elif glo_va.button == glo_va.BUTTON_CANCEL_CONFIRM_PATIENT or glo_va.button == glo_va.BUTTON_EXIST:
        LogMesssage('[states_State_2]: Patient reject information of patient with ID: {id}'.format(id=user_infor.patient_ID))
        Init_State()

############################################################
# IDENTIFYING PATIENT                                      #
############################################################
def State_3():
    ########################################################
    # CAPTURE SENSOR                                       #
    ########################################################
    if glo_va.button == glo_va.BUTTON_CAPTURE_SENSOR:
        glo_va.button = glo_va.DEFAULT_BUTTON
        glo_va.STATE = glo_va.STATE_MEASURING_SENSOR

        # # Clear current sensor information
        # request = {'type': glo_va.REQUEST_CLEAR_SENSOR, 'data': ''}
        # glo_va.gui.queue_request_states_thread.put(request)
        
        # send request to change gui
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

        # MOMO saying
        glo_va.momo_assis.momoSay(glo_va.momo_messages['measure_sensor_inform_0'])
        # Init measure sensor
        glo_va.measuring_sensor = MeasureSensor()
        LogMesssage('[states_State_3]: Patient choose measuring sensor')
    
    ########################################################
    # VIEW LIST DEPARTMENTS                                #
    ########################################################
    elif glo_va.button == glo_va.BUTTON_VIEW_LIST_DEP:
        glo_va.button = glo_va.DEFAULT_BUTTON
        glo_va.STATE = glo_va.STATE_VIEW_DEPARTMENTS

        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

        # MOMO saying
        glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_choose_dep'])
        LogMesssage('[states_State_3]: Patient choose view department')

    ########################################################
    # SUBMIT EXAMINATION                                   #
    ########################################################
    elif glo_va.button == glo_va.BUTTON_SUBMIT_EXAM:
        glo_va.button = glo_va.DEFAULT_BUTTON
        if exam.status == glo_va.EXAM_HAS_VALUE and sensor.getStatus() == glo_va.SENSOR_HAS_VALUE:
            glo_va.is_sending_message = False
            glo_va.has_response_server = False
            glo_va.STATE = glo_va.STATE_WAITING_SUB_EXAM

            glo_va.timer.Start_Timer(glo_va.OPT_TIMER_SUBMIT_EXAMINATION)
            glo_va.is_sending_message = True
            glo_va.server.Submit_Examination()

            LogMesssage('[states_State_3]: Patient submit examination and go state waiting for response')
            
        elif exam.status == glo_va.EXAM_DEFAULT:
            # data = {}
            # data['opt'] = 2
            # request = {'type': glo_va.REQUEST_NOTIFY_MESSAGE, 'data': data}
            # glo_va.gui.queue_request_states_thread.put(request)
            # LogMesssage('[states_State_3]: Patient do not have selected exam room and sensor. Notify for patient')

            # MOMO saying
            glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_choose_dep_frame_again'])
        
        elif sensor.getStatus() == glo_va.SENSOR_DEFAULT:
            # MOMO saying
            glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_measure_sensor_again'])

    ########################################################
    # EXIST PROGRAM                                        #
    ########################################################
    elif glo_va.button == glo_va.BUTTON_EXIST:
        LogMesssage('[states_State_3]: Patient with id: {id} exist program'.format(id=user_infor.patient_ID))
        Init_State()

############################################################
# CHOOSE DEPARTMENTS                                       #
############################################################
def State_4():
    ########################################################
    # CONFIRM DEPARTMENT                                   #
    ########################################################
    if glo_va.button == glo_va.BUTTON_CONFIRM_DEP:
        glo_va.button = glo_va.DEFAULT_BUTTON
        glo_va.STATE = glo_va.STATE_MEASURE_SENSOR
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

        LogMesssage('[states_State_4]: Patient confirm exam room')

        if exam.status == glo_va.EXAM_DEFAULT:
            # MOMO saying
            glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_choose_dep_frame_again'])
            LogMesssage('[states_State_4]: Patient do not select department room')

        elif sensor.getStatus() == glo_va.SENSOR_DEFAULT:
            # MOMO saying
            glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_measure_sensor'])
            LogMesssage('[states_State_4]: Patient do not have sensor information')

        else:
            # MOMO saying
            glo_va.momo_assis.momoSay(glo_va.momo_messages["ask_submit_exam"])
            LogMesssage('[states_State_4]: Patient have enought data')
    
    ########################################################
    # EXIST PROGRAM                                        #
    ########################################################
    elif glo_va.button == glo_va.BUTTON_EXIST:
        LogMesssage('[states_State_4]: Patient with id: {id} exist program'.format(id=user_infor.patient_ID))
        Init_State()

    ########################################################
    # DIAGNOSIS SYMPTOMS WITH MOMO                         #
    ########################################################
    elif glo_va.button == glo_va.BUTTON_DIAGNOSE_SYMPTOMS:
        glo_va.button = glo_va.DEFAULT_BUTTON
        LogMesssage('[states_State_4]: Patient with id: {id} choose diagnosing symptoms'.format(id=user_infor.patient_ID))

        request = {'type': glo_va.REQUEST_OPEN_MOMO_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

        # Start momo assistant
        glo_va.ClearAssisPara()
        glo_va.enable_momo_run = True
        glo_va.patient_symptons is None

        glo_va.is_sending_message = False
        glo_va.has_response_server = False

        # Init MOMO Assistant
        # This thread will end when change to new state which != STATE_VIEW_DEPARTMENTS
        glo_va.thread_assis = threading.Thread(target=glo_va.momo_assis.momoCore, args=())
        glo_va.thread_assis.daemon = True
        glo_va.thread_assis.start()

    ########################################################
    # CLOSE MOMO GUI                                       #
    ########################################################
    elif glo_va.button == glo_va.BUTTON_CLOSE_MOMO_GUI:
        glo_va.button = glo_va.DEFAULT_BUTTON
        LogMesssage('[states_State_4]: Patient with id: {id} close diagnosing symptoms gui'.format(id=user_infor.patient_ID))
        glo_va.enable_momo_run = False
        glo_va.thread_assis.join()

        # Remove a chance to receive dummy response from server
        glo_va.lock_response_server.acquire(True)
        glo_va.is_sending_message = False
        glo_va.has_response_server = False
        glo_va.timer.Clear_Timer()
        glo_va.lock_response_server.release()

############################################################
# CONFIRMING NEW PATIENT                                   #
############################################################
def State_5():
    if glo_va.button == glo_va.BUTTON_DENY_NEW_PATIENT:
        Init_State()

    elif glo_va.button == glo_va.BUTTON_ACCEPT_NEW_PATIENT:
        LogMesssage('[states_State_3]: Unknown Patient choose add new patient')
        glo_va.button = glo_va.DEFAULT_BUTTON
        # Set state for next state
        glo_va.STATE = glo_va.STATE_NEW_PATIENT

        # send request change ui
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

        glo_va.camera.runBackCamera()

        return
    
    elif glo_va.button == glo_va.BUTTON_VERIFY_PATIENT:
        LogMesssage('[states_State_3]: Unknown Patient choose verify patient with SSN: {}'.format(glo_va.check_ssn))
        glo_va.button = glo_va.DEFAULT_BUTTON

        # Back to first state
        glo_va.STATE = glo_va.STATE_RECOGNIZE_PATIENT

        glo_va.camera.runBackCamera()

        return

    if glo_va.button == glo_va.BUTTON_EXIST:
        # If user reject, Clear user_infor, Ui and go to first state
        LogMesssage('[states_State_3]: Unknown Patient exist program')
        Init_State()

############################################################
# GETTING FACE NEW PATIENT                                 #
############################################################
def State_6():
    if glo_va.button == glo_va.BUTTON_EXIST:
        Init_State()
        return

    # Read camera
    glo_va.camera.RunCamera()

    if glo_va.img is not None: face_locations = glo_va.centerface_detector(glo_va.img, glo_va.img.shape[0], glo_va.img.shape[1])
    if len(face_locations) == 1:
        ret, location_detected_face = glo_va.face_recognition.Get_Location_Face(face_locations)
        if ret == -2:
            LogMesssage("[State_1]: Error Face locations", opt=0)
            Init_State()
            return

        elif ret == 0:
            # detected_face = img[top: bottom, left: right]
            detected_face = glo_va.img[location_detected_face[0] : location_detected_face[1], location_detected_face[2] : location_detected_face[3]]

            correct_user_pose, embedded_face = glo_va.face_recognition.encodingFaceNewPatient(detected_face)
            if correct_user_pose:
                glo_va.num_correct_user_pose += 1

                # Draw green box for correct face
                # cv2.rectangle(glo_va.img, (left, top), (right, bottom) , (2, 255, 0), 2)
                cv2.rectangle(glo_va.img, (location_detected_face[2], location_detected_face[0]), (location_detected_face[3], location_detected_face[1]) , (0, 255, 0), 2)
            else:
                # Draw red box for incorrect face
                # cv2.rectangle(glo_va.img, (left, top), (right, bottom) , (2, 255, 0), 2)
                cv2.rectangle(glo_va.img, (location_detected_face[2], location_detected_face[0]), (location_detected_face[3], location_detected_face[1]) , (0, 0, 255), 2)

            glo_va.num_user_pose += 1
            # print("{} {}".format(glo_va.num_user_pose, user_pose))
            # Save this in the list embedded for new user
            glo_va.list_embedded_face_origin_new_patient.append(embedded_face)

            if glo_va.num_user_pose >= 7:
                if glo_va.num_correct_user_pose > 5:
                    if glo_va.check_current_shape == False:
                        glo_va.check_current_shape = True

                    elif glo_va.check_current_shape == True:
                        glo_va.check_current_shape = False
                        
                        # Activate image in the UI
                        request = {'type': glo_va.REQUEST_ACTIVATE_NEW_FACE, 'data': glo_va.current_shape}
                        glo_va.gui.queue_request_states_thread.put(request)

                        # Change to take next pose of user
                        glo_va.current_shape += 1

                        # MOMO saying
                        glo_va.momo_assis.momoSay(glo_va.momo_messages['capture_img'][glo_va.current_shape])
                        
                        # calculate the mean of all images in one pose
                        mean_embedded_image = np.mean(glo_va.list_embedded_face_origin_new_patient ,axis=0)
                        # save the current embedded face
                        # temp_embedded_face = Compose_Embedded_Face(glo_va.embedded_face)
                        temp_embedded_face = Compose_Embedded_Face(mean_embedded_image)
                        glo_va.list_embedded_face_new_user += temp_embedded_face + ' '

                        if glo_va.current_shape == glo_va.num_face_new_user:
                            LogMesssage('Done get face new user')
                            glo_va.STATE = glo_va.STATE_MEASURE_SENSOR

                            # send request change ui
                            request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
                            glo_va.gui.queue_request_states_thread.put(request)

                            time.sleep(1.5)

                            # MOMO saying
                            glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_choose_dep_frame'])
                            glo_va.camera.currentStopCamera()
            
                else:
                    glo_va.check_current_shape = False

                glo_va.num_user_pose = 0
                glo_va.num_correct_user_pose = 0
                glo_va.list_embedded_face_origin_new_patient = []

    glo_va.gui.image_display = glo_va.img

############################################################
# WAITING RESPONSE SUBMI EXAMMINATION                      #
############################################################
def State_7():
    if glo_va.button_ok_pressed == True:
        data = {}
        if glo_va.has_response_server == True:
            if glo_va.return_stt == -1:
                data['opt'] = 1
                glo_va.valid_stt = -1
                
            else:
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
    
    elif glo_va.button_ok_pressed == False and glo_va.button == glo_va.BUTTON_OKAY:
        if glo_va.valid_stt == -1:
            glo_va.STATE = glo_va.STATE_MEASURE_SENSOR
            glo_va.button_ok_pressed = True

        elif glo_va.valid_stt == 0:
            Init_State()
    
    if glo_va.button == glo_va.BUTTON_EXIST:
        # If user reject, Clear user_infor, Ui and go to first state
        Init_State()
        return

############################################################
# MEASURING SENSOR INFORMATION                             #
############################################################
def State_8():
    ########################################################
    # CONFIRM SENSOR                                       #
    ########################################################
    if glo_va.button == glo_va.BUTTON_CONFIRM_SENSOR:
        glo_va.button = glo_va.DEFAULT_BUTTON

        if glo_va.measuring_sensor.has_esp and glo_va.measuring_sensor.has_oso2:
            # Get sensor information from MeasureSensor
            sensor_infor = {
                'height': glo_va.measuring_sensor.final_height, 'weight': glo_va.measuring_sensor.final_weight,
                'spo2': glo_va.measuring_sensor.final_spo2, 'heart_pulse': glo_va.measuring_sensor.final_heart_pulse,
                'temperature': glo_va.measuring_sensor.final_temperature, 'bmi': glo_va.measuring_sensor.final_bmi
            }

            # Change state
            request = {'type': glo_va.REQUEST_UPDATE_SENSOR, 'data': sensor_infor}
            glo_va.gui.queue_request_states_thread.put(request)

            # Update sensor entity
            sensor.Update_Sensor(sensor_infor)
            LogMesssage("[states_State_8]: Has enought sensor data: {}. Has oso2: {}. Has esp32: {}".format(sensor_infor, glo_va.measuring_sensor.has_oso2, glo_va.measuring_sensor.has_esp))

        else:
            if glo_va.measuring_sensor.has_esp: LogMesssage("[states_State_8]: Missing datas of OSO2 sensor")
            else: LogMesssage("[states_State_8]: Missing datas of ESP32 sensor")

        if glo_va.connected_sensor_device:
            glo_va.connected_sensor_device = False
            glo_va.measuring_sensor.closeDevice()

        glo_va.measuring_sensor = None

        # Change state
        glo_va.STATE = glo_va.STATE_MEASURE_SENSOR
        request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
        glo_va.gui.queue_request_states_thread.put(request)

        LogMesssage('[states_State_8]: Patient confirm measuring sensor')

        if sensor.getStatus() == glo_va.SENSOR_DEFAULT:
            # MOMO saying
            glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_measure_sensor_again'])
            LogMesssage('[states_State_8]: Patient do not have sensor information')

        elif exam.status == glo_va.EXAM_DEFAULT:
            # MOMO saying
            LogMesssage('[states_State_8]: Patient do not select deparment')
            
        else:
            # MOMO saying
            glo_va.momo_assis.momoSay(glo_va.momo_messages["ask_submit_exam"])
            LogMesssage('[states_State_8]: Patient have enough data')

    ########################################################
    # CONNECT DEVICE                                       #
    ########################################################
    elif glo_va.button == glo_va.BUTTON_CONNECT_DEVICE_SENSOR:
        glo_va.button = glo_va.DEFAULT_BUTTON
        LogMesssage('[states_State_8]: Patient press connect sensor device')

        # if connection is closed
        if glo_va.connected_sensor_device == False:
            is_opened = glo_va.measuring_sensor.openConnectionSensors()
            # If open connection successfully
            if is_opened == 0:
                glo_va.connected_sensor_device = True
                # MOMO saying
                glo_va.momo_assis.momoSay(glo_va.momo_messages['confirm_connect_device_success'])
                LogMesssage('[states_State_8]: Patient successfully connect sensor device')
            
            # If open connection unsuccessfully
            elif is_opened == -1:
                # MOMO saying
                glo_va.momo_assis.momoSay(glo_va.momo_messages['ask_turn_on_oso2'])
                LogMesssage("[State_8]: Patient unsuccessfully connect sensor device")
        
        # If the connection is already opened
        else:
            glo_va.momo_assis.momoSay(glo_va.momo_messages['confirm_connected_device'])
            LogMesssage("[states_State_8]: Connection with sensors device is already connected")

    ########################################################
    # EXIST PROGRAM                                        #
    ########################################################
    elif glo_va.button == glo_va.BUTTON_EXIST:
        LogMesssage('[states_State_8]: Patient with id: {id} exist program'.format(id=user_infor.patient_ID))
        Init_State()
    
    ########################################################
    # PATIENT DO NOT PRESS ANYTHING                        #
    ########################################################
    else:
        if glo_va.connected_sensor_device:
            # Check read data success for fail or disconnect
            ret = glo_va.measuring_sensor.getSensorsData()
            
            # disconnect
            if ret == -2:
                glo_va.measuring_sensor.closeDevice()
                glo_va.connected_sensor_device = False

                data = {}
                data['opt'] = 5
                request = {'type': glo_va.REQUEST_NOTIFY_MESSAGE, 'data': data}
                glo_va.gui.queue_request_states_thread.put(request)

                LogMesssage("[states_State_8]: Connection with sensors device is disconnected")

            elif ret == 1:
                glo_va.measuring_sensor.closeDevice()
                glo_va.connected_sensor_device = False
                LogMesssage("[states_State_8]: Done getting sensor information")
            
            elif ret == 2: glo_va.momo_assis.momoSay(glo_va.momo_messages["ask_finish_oso2_measurement"])
            
            elif ret == 3: glo_va.momo_assis.momoSay(glo_va.momo_messages["ask_finish_esp_measurement"])

############################################################
# INIT PROGRAM                                             #
############################################################
def Init_State():
    LogMesssage('[states_Init_State]: Reset at STATE: {}'.format(glo_va.STATE))

    glo_va.camera.runBackCamera()

    # Lock the response message from server when restart program
    glo_va.lock_init_state.acquire(True)
    LogMesssage('[states_Init_State]: Acquire lock init state')
    
    ########################################################
    # BUTTON                                               #
    ########################################################
    glo_va.button = glo_va.DEFAULT_BUTTON
    glo_va.button_ok_pressed = True
    LogMesssage('\t[states_Init_State]: Set default button parameters')

    ########################################################
    # SERVER                                               #
    ########################################################
    glo_va.turn = glo_va.TIMER_GOT_BY_NO_ONE
    glo_va.timer.Clear_Timer()
    glo_va.is_sending_message = False
    glo_va.has_response_server = False
    LogMesssage('\t[states_Init_State]: Set default server parameters')

    ########################################################
    # FACE RECOGNITION PARAMETERS                          #
    ########################################################
    # glo_va.patient_ID = -1
    user_infor.Clear()
    glo_va.check_ssn = "-1"
    LogMesssage('\t[states_Init_State]: Clear patient information')

    ########################################################
    # NEW USER PARAMETERS                                  #
    ########################################################
    if glo_va.current_shape != 0:
        glo_va.list_embedded_face_new_user = ""
        glo_va.current_shape = 0
        glo_va.num_user_pose = 0
        glo_va.check_current_shape = False
        glo_va.num_correct_user_pose = 0
        glo_va.list_embedded_face_origin_new_patient = []
        LogMesssage('\t[states_Init_State]: Set default parameters for new patients')
    
    # request = {'type': glo_va.REQUEST_DEACTIVATE_NEW_FACE, 'data': ''}
    # glo_va.gui.queue_request_states_thread.put(request)

    ########################################################
    # EXAM ROOMS                                           #
    ########################################################
    exam.Clear()
    request = {'type': glo_va.REQUEST_CLEAR_EXAM_ROOM, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)
    request = {'type': glo_va.REQUEST_CLEAR_SELECTED_EXAM_ROOM, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)
    request = {'type': glo_va.REQUEST_CLEAR_DEPARTMENT_LIST, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)
    LogMesssage('\t[states_Init_State]: Set default parameters for EXAM ROOMS')

    glo_va.patient_symptons = None
    
    ########################################################
    # SUBMIT PARAMETERS                                    #
    ########################################################
    glo_va.valid_stt = -1
    glo_va.return_stt = -1
    LogMesssage('\t[states_Init_State]: Set default parameters for submit examination')

    ########################################################
    # SENSOR PARAMETERS                                    #
    ########################################################
    try:
        glo_va.measuring_sensor.closeDevice()
        glo_va.measuring_sensor = None
    except:
        glo_va.measuring_sensor = None

    glo_va.connected_sensor_device = False
    sensor.Clear()
    request = {'type': glo_va.REQUEST_CLEAR_SENSOR, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)
    LogMesssage('\t[states_Init_State]: Set default parameters for Sensor')

    ########################################################
    # BACK TO STATE 1                                      #
    ########################################################
    glo_va.STATE = glo_va.STATE_RECOGNIZE_PATIENT
    request = {'type': glo_va.REQUEST_CHANGE_GUI, 'data': ''}
    glo_va.gui.queue_request_states_thread.put(request)
    LogMesssage('\t[states_Init_State]: Back to State 1')

    # MOMO saying
    glo_va.momo_assis.momoSay(glo_va.momo_messages['say_bye'])
    time.sleep(1)

    glo_va.lock_init_state.release()
    LogMesssage('[states_Init_State]: Release lock init state')