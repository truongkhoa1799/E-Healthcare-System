from azure.eventhub import EventData, EventHubProducerClient
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

import sys
import time
import pickle
import threading

PROJECT_PATH = '/home/thesis/Documents/thesis/E-Healthcare-System/'
sys.path.append(PROJECT_PATH)
from utils.parameters import *
from utils.common_functions import LogMesssage

class Server:
    def __init__(self):
        # IOT hub, event hub connection
        self.__device_ID = None
        self.__device_iothub_connection = None
        self.__eventhub_connection = None
        self.__eventhub_name = None

        self.__LoadConnection()

        self.__establishConnectionServer()
        

        # Start a thread to listen 
        self.__listening_server_thread = threading.Thread(target=self.__Listen_Reponse_Server, args=())
        self.__listening_server_thread.daemon = True
        self.__listening_server_thread.start()

    def __LoadConnection(self):
        with open (glo_va.CONNECTION_AZURE_PATH, 'rb') as fp_1:
            ret = pickle.load(fp_1)
            self.__device_ID = ret['device_ID']
            self.__device_iothub_connection = ret['device_iothub_connection']
            self.__eventhub_connection = ret['eventhub_connection']
            self.__eventhub_name = ret['eventhub_name']
            # print(self.__device_iothub_connection)
            # print(self.__eventhub_connection)
            # print(self.__eventhub_name)
    
    def __establishConnectionServer(self):
        self.__connection = IoTHubDeviceClient.create_from_connection_string(self.__device_iothub_connection)
        self.__producer = EventHubProducerClient.from_connection_string(
            conn_str=self.__eventhub_connection,
            eventhub_name=self.__eventhub_name
        )
            
    # When server receive response:
    #   1: Clear Timer, so that timer is not trigged
    def __Listen_Reponse_Server(self):
        while True:
            try:
                method_request = self.__connection.receive_method_request()
                if method_request.name == "Update_List_Exam_Rooms":
                    init_parameters.list_examination_room = method_request.payload['list_exam_rooms']
                    LogMesssage('[__Listen_Reponse_Server]: Receive update request udpating list exam rooms')
                
                else:
                    timer_id = method_request.payload['request_id']

                    # Default response
                    response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                    response_status = 200

                    # Was not acquired
                    if not glo_va.lock_init_state.acquire(False):
                        LogMesssage('[__Listen_Reponse_Server]: Lock init state was already acquired, do not accept new message')
                        method_response = MethodResponse(method_request.request_id, response_status, payload=response_payload)
                        self.__connection.send_method_response(method_response)
                        continue
                    
                    if not glo_va.lock_response_server.acquire(False):
                        glo_va.lock_init_state.release()

                        LogMesssage('[__Listen_Reponse_Server]: Lock response server was already acquired, do not accept new message')
                        method_response = MethodResponse(method_request.request_id, response_status, payload=response_payload)
                        self.__connection.send_method_response(method_response)
                        continue

                    LogMesssage('[__Listen_Reponse_Server]: Acquire lock init state')
                    LogMesssage('[__Listen_Reponse_Server]: Acquire lock response server')

                    # time.sleep(20)

                    # if timer did not time out, receive timer and clear timer
                    # Check whether the state is init or not, if yes continue
                    if glo_va.is_sending_message == True:
                        # Notify the timer that server is in lock
                        glo_va.turn = 1

                        # Clear timer
                        glo_va.timer.Clear_Timer()
                        LogMesssage('[__Listen_Reponse_Server]: Clear Timer')

                        # Release lock
                        glo_va.lock_response_server.release()
                        LogMesssage('[__Listen_Reponse_Server]: Release lock response server')
                        LogMesssage("[__Listen_Reponse_Server]: Received response for request: {request_name} of timer_id: {timer_id} for {name}.".format(request_name=method_request.name,timer_id=timer_id, name=method_request.name))
                        
                        # Validation response
                        # TESTED
                        if method_request.name == "Validate_User" and glo_va.timer.timer_id == timer_id:
                            ret_msg = int(method_request.payload['return'])
                            if glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT and ret_msg == 0:
                                # print(method_request.payload)
                                user_infor.Update_Info(method_request.payload)
                                LogMesssage('[__Listen_Reponse_Server]: Update patient information')

                            elif glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT and ret_msg == -2:
                                # Patient is wearing mask
                                LogMesssage('[__Listen_Reponse_Server]: Patient is wearing mask. Please push your mask off')

                            elif glo_va.STATE == glo_va.STATE_RECOGNIZE_PATIENT and ret_msg == -1:
                                user_infor.NoFace()
                                glo_va.times_missing_face += 1
                                LogMesssage('[__Listen_Reponse_Server]: Missing face times: {time}'.format(time=glo_va.times_missing_face))
                            
                            glo_va.has_response_server = True

                        # # Get examination room response
                        # # TESTED
                        # elif method_request.name == "Get_Examination_Room" and glo_va.timer.timer_id == timer_id:
                        #     ret_msg = int(method_request.payload['return'])
                        #     if ret_msg == 0:
                        #         init_parameters.updateListExamRooms(method_request.payload)
                        #         LogMesssage('[__Listen_Reponse_Server]: Get examination room and hospital_ID: {id}'.format(id=init_parameters.hospital_ID))
                        #     else:
                        #         LogMesssage('[__Listen_Reponse_Server]: False get examination room and hospital_ID: {id}'.format(id=init_parameters.hospital_ID))

                        #     glo_va.has_response_server = True

                        # Submit examination request response
                        elif method_request.name == "Submit_Examination" and glo_va.timer.timer_id == timer_id:
                            ret_msg = int(method_request.payload['return'])
                            if ret_msg == 0:
                                glo_va.return_stt = method_request.payload['stt']
                                LogMesssage('[__Listen_Reponse_Server]: Receive STT: {stt} of patient: {id}'.format(stt=glo_va.return_stt, id=user_infor.patient_ID))
                            else:
                                glo_va.return_stt = -1
                                LogMesssage('[__Listen_Reponse_Server]: False receive STT: {stt} of patient: {id}'.format(stt=glo_va.return_stt, id=user_infor.patient_ID))

                            glo_va.has_response_server = True

                        # Get_Sympton request response
                        elif method_request.name == "Get_Sympton" and glo_va.timer.timer_id == timer_id:
                            ret_msg = int(method_request.payload['return'])
                            if glo_va.STATE == glo_va.STATE_VIEW_DEPARTMENTS and ret_msg == 0:
                                glo_va.patient_symptons =  method_request.payload['symptons']
                                LogMesssage('[__Listen_Reponse_Server]: Receive analyzed symptons of patient: {id}'.format(id=user_infor.patient_ID))
                            elif glo_va.STATE == glo_va.STATE_VIEW_DEPARTMENTS and ret_msg == -1:
                                glo_va.patient_symptons = None
                                LogMesssage('[__Listen_Reponse_Server]: False analyzed symptons of patient: {id}'.format(id=user_infor.patient_ID))

                            glo_va.has_response_server = True

                        # Get init parameters request response
                        elif method_request.name == "Get_Init_Parameters" and glo_va.timer.timer_id == timer_id:
                            ret_msg = int(method_request.payload['return'])
                            if ret_msg == 0:
                                parameters = method_request.payload['parameters']
                                init_parameters.updateInitParameters(parameters)
                                LogMesssage('[__Listen_Reponse_Server]: Success to get init parameters')
                            else:
                                LogMesssage('[__Listen_Reponse_Server]: False to get init parameters')

                            glo_va.has_response_server = True

                        else:
                            response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
                            response_status = 404
                    else:
                        # if timer did timeout first, discard this response and wait for next response
                        glo_va.lock_response_server.release()
                        LogMesssage('[__Listen_Reponse_Server]: Release lock response server')

                    glo_va.lock_init_state.release()
                    LogMesssage('[__Listen_Reponse_Server]: Release lock init state')
                

            except Exception as e:
                if method_request.name == "Update_List_Exam_Rooms":
                    LogMesssage('[__Listen_Reponse_Server]: Has error when updating list exam rooms')
                
                else:
                    LogMesssage("Has error at module __Listen_Reponse_Server in server.py: {}".format(e), opt=2)

                    if glo_va.lock_init_state.locked() == True:
                        glo_va.lock_init_state.release()
                        LogMesssage('[__Listen_Reponse_Server]: Has error: {e}. Release lock init state'.format(e=e))

                    if glo_va.lock_response_server.locked() == True:
                        glo_va.lock_response_server.release()
                        LogMesssage('[__Listen_Reponse_Server]: Has error: {e}. Release lock response server'.format(e=e))

                    if method_request.name == "Validate_User":
                        user_infor.Clear()

                    # elif method_request.name == "Get_Examination_Room":
                    #     init_parameters.Clear()

                    elif method_request.name == "Get_Sympton":
                        glo_va.patient_symptons = None

                    elif method_request.name == "Get_Init_Parameters":
                        init_parameters.Clear()

                    glo_va.has_response_server = True
                    # self.__establishConnectionServer()
                    # LogMesssage('Re-establish connection with Server')

            method_response = MethodResponse(method_request.request_id, response_status, payload=response_payload)
            self.__connection.send_method_response(method_response)

    def Validate_User(self):
        try:
            event_data_batch = self.__producer.create_batch()
            try:
                LogMesssage("[Validate_User]: Send validating message to server with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))
                data = EventData(glo_va.list_embedded_face)
                data.properties = {
                    'request_id':glo_va.timer.timer_id,
                    'type_request': "0", 
                    'device_ID': str(self.__device_ID)
                }
                event_data_batch.add(data)
            except Exception as e:
                LogMesssage(e, opt=2)
                glo_va.STATE = -1
            self.__producer.send_batch(event_data_batch)
        except Exception as e:
            LogMesssage("Has error at module Validate_User in server.py: {}".format(e), opt=2)
            
            self.__establishConnectionServer()
            LogMesssage('Re-establish connection with Server')
    
    # def Get_Examination_Room(self):
    #     try:
    #         event_data_batch = self.__producer.create_batch()
    #         try:
    #             LogMesssage("[Get_Examination_Room]: Get Examination Room with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))
    #             data = EventData("")
    #             data.properties = {'request_id':glo_va.timer.timer_id,'type_request':"4", 'device_ID': str(self.__device_ID)}
    #             event_data_batch.add(data)
    #         except Exception as e:
    #             LogMesssage(e, opt=2)
    #             glo_va.STATE = -1
    #         self.__producer.send_batch(event_data_batch)
    #     except Exception as e:
    #         LogMesssage("Has error at module Get_Examination_Room in server.py: {}".format(e), opt=2)
            
    #         self.__establishConnectionServer()
    #         LogMesssage('Re-establish connection with Server')
    
    def Submit_Examination(self):
        try:
            event_data_batch = self.__producer.create_batch()
            try:
                LogMesssage("[Submit_Examination]: Submit Examination with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))
                
                dep_name, building_code, room_code = exam.Get_Exam_Room_Infor()
                sensor_infor = sensor.sensor_infor
                msg = {
                    'request_id':glo_va.timer.timer_id,
                    'type_request': "5",
                    'device_ID': str(self.__device_ID),
                    'hospital_ID': str(init_parameters.hospital_ID),
                    'building_code': building_code,
                    'room_code': room_code,
                    'bmi': str(sensor_infor['bmi']),
                    'pulse': str(sensor_infor['heart_pulse']),
                    'thermal': str(sensor_infor['temperature']),
                    'spo2': str(sensor_infor['spo2']),
                    'height': str(sensor_infor['height']),
                    'weight': str(sensor_infor['weight']),
                    'patient_ID': str(user_infor.patient_ID)
                }
                
                # Check is new user
                if user_infor.patient_ID == -1:
                    data = EventData(glo_va.list_embedded_face_new_user)
                elif user_infor.patient_ID != -1:
                    data = EventData("")

                data.properties = msg
                event_data_batch.add(data)
            except Exception as e:
                LogMesssage(e, opt=2)
                glo_va.STATE = -1
            self.__producer.send_batch(event_data_batch)
        except Exception as e:
            LogMesssage("Has error at module Submit_Examination in server.py: {}".format(e), opt=2)
            
            self.__establishConnectionServer()
            LogMesssage('Re-establish connection with Server')

    def getSymptonPatient(self, voice):
        try:
            event_data_batch = self.__producer.create_batch()
            try:
                LogMesssage("[getSymptonPatient]: Get sympton patient with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))
                data = EventData(voice)
                data.properties = {
                    'request_id': glo_va.timer.timer_id,
                    'type_request': "7", 
                    'device_ID': str(self.__device_ID)
                }
                event_data_batch.add(data)
            except Exception as e:
                LogMesssage(e, opt=2)
                glo_va.STATE = -1
            self.__producer.send_batch(event_data_batch)
        except Exception as e:
            LogMesssage("Has error at module getSymptonPatient in server.py: {}".format(e), opt=2)
            
            self.__establishConnectionServer()
            LogMesssage('Re-establish connection with Server')
    
    def getInitParameters(self):
        try:
            event_data_batch = self.__producer.create_batch()
            try:
                LogMesssage("[getInitParameters]: Get init parameters with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))
                data = EventData('')
                data.properties = {
                    'request_id': glo_va.timer.timer_id,
                    'type_request': "8", 
                    'device_ID': str(self.__device_ID)
                }
                event_data_batch.add(data)
            except Exception as e:
                LogMesssage(e, opt=2)
                glo_va.STATE = -1
            self.__producer.send_batch(event_data_batch)
        except Exception as e:
            LogMesssage("Has error at module getInitParameters in server.py: {}".format(e), opt=2)
            
            self.__establishConnectionServer()
            LogMesssage('Re-establish connection with Server')

    def Close(self):
        # self.__listening_server_thread.join()
        self.__producer.close()
        self.__connection.disconnect()

# server = Server()
# server.Validate_User()
# server.Close()