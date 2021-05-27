from azure.eventhub import EventData, EventHubProducerClient
from azure.iot.device.aio import IoTHubDeviceClient
from threading import Timer
# from uamqp import errors
# import numpy as np
import sys
import json
import time
import asyncio
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
        
        # self.__LoadConnection()
        # self.__establishEventhubSendConnection()
        # self.__establishIoTHubReceiveConnection()

        event_loop_receive = asyncio.new_event_loop()
        self.__listening_server_thread = threading.Thread(target=self.__init_server, args=(event_loop_receive,))
        self.__listening_server_thread.daemon = True
        self.__listening_server_thread.start()

        # set the mesage received handler on the client

    def __LoadConnection(self):
        with open (glo_va.CONNECTION_AZURE_PATH, 'rb') as fp_1:
            ret = pickle.load(fp_1)
            self.__device_ID = ret['device_ID']
            self.__device_iothub_connection = ret['device_iothub_connection']
            self.__eventhub_connection = ret['eventhub_connection']
            self.__eventhub_name = ret['eventhub_name']

    async def __establishIoTHubReceiveConnection(self):
        LogMesssage('[__establishIoTHubReceiveConnection]: Establish iot hub connection')
        self.__connection = IoTHubDeviceClient.create_from_connection_string(self.__device_iothub_connection)
        await self.__connection.connect()

    
    def __establishEventhubSendConnection(self):
        self.__producer = EventHubProducerClient.from_connection_string(
            conn_str=self.__eventhub_connection,
            eventhub_name=self.__eventhub_name
        )
    
    def __init_server(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.message_received_handler())

    async def message_received_handler(self):
        self.__LoadConnection()
        self.__establishEventhubSendConnection()
        await self.__establishIoTHubReceiveConnection()

        while True:
            try:
                payload = None
                message = await self.__connection.receive_message()
                if message is None: continue
                
                for property in vars(message).items():
                    if property[0] == "custom_properties":
                        payload = json.loads(property[1]['response_msg'])
                        break

                if payload is None: continue
            
            except Exception as e:
                LogMesssage('[server___Listen_Reponse_Server]: Fail to receive message: {}'.format(e))
                continue
                
            try:
                type_request = payload['type_request']
                timer_id = payload['request_id']

                if type_request == glo_va.SERVER_REQUEST_UPDATE_EXAM_ROOM:
                    init_parameters.list_examination_room = payload['parameters']
                    LogMesssage('[server___Listen_Reponse_Server]: Receive update request udpating list exam rooms')
                
                else:
                    ########################################################
                    # ACQUIRE LOCK INIT STATE                              #
                    ########################################################
                    if not glo_va.lock_init_state.acquire(False):
                        LogMesssage('[server___Listen_Reponse_Server]: Lock init state was already acquired, do not accept new message')
                        continue
                    
                    ########################################################
                    # ACQUIRE LOCK RESPONSE SERVER                         #
                    ########################################################
                    if not glo_va.lock_response_server.acquire(False):
                        # Release lock just acquire above
                        glo_va.lock_init_state.release()
                        LogMesssage('[server___Listen_Reponse_Server]: Lock response server was already acquired, do not accept new message')
                        continue
                
                    ########################################################
                    # RESPONSE WITH DIFFERENT REQUEST ID                   #
                    ########################################################
                    if glo_va.timer.timer_id != timer_id:
                        glo_va.lock_response_server.release()
                        glo_va.lock_init_state.release()

                        LogMesssage('[server___Listen_Reponse_Server]: Receive response with different current request id')                        
                        LogMesssage('[server___Listen_Reponse_Server]: Acquire lock init state')
                        LogMesssage('[server___Listen_Reponse_Server]: Acquire lock response server')
                        continue

                    LogMesssage('[server___Listen_Reponse_Server]: Acquire lock init state')
                    LogMesssage('[server___Listen_Reponse_Server]: Acquire lock response server')

                    ########################################################
                    # CHECK REPONSE MESSAGES                              #
                    ########################################################
                    if glo_va.is_sending_message == True:
                        # Notify the timer that server is in lock
                        glo_va.turn = glo_va.TIMER_GOT_BY_SERVER
                        
                        # Clear timer
                        glo_va.timer.Clear_Timer()
                        LogMesssage('[server___Listen_Reponse_Server]: Clear Timer')
                        LogMesssage("[server___Listen_Reponse_Server]: Received response for request: {request_name} of timer_id: {timer_id}.".format(request_name=glo_va.list_request_name[type_request],timer_id=timer_id))
                        
                        ########################################################
                        # VALIDATION USERS RESPONSE                            #
                        ########################################################
                        if type_request == glo_va.SERVER_REQUEST_VALIDATION:
                            # glo_va.list_time_send_server.append(time.time()-glo_va.start_time)
                            # glo_va.times_send += 1
                            # if glo_va.times_send == 10:
                            #     print('Max time detec: {}'.format(np.max(glo_va.list_time_send_server)))
                            #     print('Min time detec: {}'.format(np.min(glo_va.list_time_send_server)))
                            #     print('Mean time detec: {}'.format(np.mean(glo_va.list_time_send_server)))
                            #     print('Std time detec: {}'.format(np.std(glo_va.list_time_send_server)))
                            ret_msg = str(payload['return'])
                            if ret_msg == "0":
                                user_infor.Update_Info(payload)
                                LogMesssage('[server___Listen_Reponse_Server]: Update patient information')

                            elif ret_msg == "-2":
                                # Patient is wearing mask
                                user_infor.wearingMask()
                                LogMesssage('[server___Listen_Reponse_Server]: Patient is wearing mask. Please push your mask off')
                            
                            elif ret_msg == "-3":
                                # Invalid SSN
                                LogMesssage('[server___Listen_Reponse_Server]: SSN for verifying patient is invalid')

                            elif ret_msg == "-1":
                                user_infor.NoFace()
                                glo_va.times_missing_face += 1
                                LogMesssage('[server___Listen_Reponse_Server]: Missing face times: {time}'.format(time=glo_va.times_missing_face))
                            
                            glo_va.has_response_server = True

                        ########################################################
                        # EXAMINATION SUBMISSION RESPONSE                     #
                        ########################################################
                        elif type_request == glo_va.SERVER_REQUEST_SUBMIT_EXAMINATION:
                            ret_msg = str(payload['return'])
                            if ret_msg == "0":
                                glo_va.return_stt = payload['stt']
                                LogMesssage('[server___Listen_Reponse_Server]: Receive STT: {stt} of patient: {id}'.format(stt=glo_va.return_stt, id=user_infor.patient_ID))
                            
                            else:
                                glo_va.return_stt = -1
                                LogMesssage('[server___Listen_Reponse_Server]: False receive STT: {stt} of patient: {id}'.format(stt=glo_va.return_stt, id=user_infor.patient_ID))

                            glo_va.has_response_server = True

                        ########################################################
                        # GET SYMPTONS USERS RESPONSE                          #
                        ########################################################
                        elif type_request == glo_va.SERVER_REQUEST_GET_SYMPTOMS:
                            ret_msg = str(payload['return'])
                            if ret_msg == "0":
                                glo_va.patient_symptons =  payload['symptons']
                                LogMesssage('[server___Listen_Reponse_Server]: Receive analyzed symptons of patient: {id}'.format(id=user_infor.patient_ID))
                            
                            elif ret_msg == "-1":
                                glo_va.patient_symptons = None
                                LogMesssage('[server___Listen_Reponse_Server]: False analyzed symptons of patient: {id}'.format(id=user_infor.patient_ID))

                            glo_va.has_response_server = True

                        ########################################################
                        # LOAD INIT PARAMETERS RESPONSE                        #
                        ########################################################
                        elif type_request == glo_va.SERVER_REQUEST_GET_INIT_PARA:
                            ret_msg = str(payload['return'])
                            if ret_msg == "0":
                                parameters = payload['parameters']
                                init_parameters.updateInitParameters(parameters)
                                LogMesssage('[server___Listen_Reponse_Server]: Success to get init parameters')

                            else:
                                init_parameters.status = ret_msg
                                LogMesssage('[server___Listen_Reponse_Server]: False to get init parameters')

                            glo_va.has_response_server = True

                    # Release lock
                    glo_va.lock_response_server.release()
                    LogMesssage('[server___Listen_Reponse_Server]: Release lock response server')

                    glo_va.lock_init_state.release()
                    LogMesssage('[server___Listen_Reponse_Server]: Release lock init state')

            except Exception as e:
                LogMesssage("Has error at module __Listen_Reponse_Server in server.py: {}".format(e), opt=2)

                if glo_va.lock_init_state.locked() == True:
                    glo_va.lock_init_state.release()
                    LogMesssage('[server___Listen_Reponse_Server]: Has error: {e}. Release lock init state'.format(e=e))

                if glo_va.lock_response_server.locked() == True:
                    glo_va.lock_response_server.release()
                    LogMesssage('[server___Listen_Reponse_Server]: Has error: {e}. Release lock response server'.format(e=e))

                if type_request == glo_va.SERVER_REQUEST_VALIDATION:
                    user_infor.Clear()

                elif type_request == glo_va.SERVER_REQUEST_GET_SYMPTOMS:
                    glo_va.patient_symptons = None

                elif type_request == glo_va.SERVER_REQUEST_GET_INIT_PARA:
                    init_parameters.Clear()

                glo_va.has_response_server = True
                
    # # When server receive response:
    # #   1: Clear Timer, so that timer is not trigged
    # ########################################################
    # # Listenning response or message from server           #
    # ########################################################
    # def __Listen_Reponse_Server(self):
    #     while True:
    #         try:
    #             # RECEIVE MESSAGE
    #             # message = self.__connection.receive_message()
    #             message = self.__connection.receive_message()
    #             if message is None: continue

    #             payload = None
    #             for property in vars(message).items():
    #                 if property[0] == "custom_properties":
    #                     payload = json.loads(property[1]['response_msg'])
    #                     break
                
    #             if payload is None:
    #                 continue
            
    #         except Exception as e:
    #             LogMesssage('[server___Listen_Reponse_Server]: Fail to receive message: {}'.format(e))
    #             continue
                
    #         try:
    #             type_request = payload['type_request']
    #             timer_id = payload['request_id']

    #             if type_request == glo_va.SERVER_REQUEST_UPDATE_EXAM_ROOM:
    #                 init_parameters.list_examination_room = payload['parameters']
    #                 LogMesssage('[server___Listen_Reponse_Server]: Receive update request udpating list exam rooms')
                
    #             else:
    #                 ########################################################
    #                 # ACQUIRE LOCK INIT STATE                              #
    #                 ########################################################
    #                 if not glo_va.lock_init_state.acquire(False):
    #                     LogMesssage('[server___Listen_Reponse_Server]: Lock init state was already acquired, do not accept new message')
    #                     continue
                    
    #                 ########################################################
    #                 # ACQUIRE LOCK RESPONSE SERVER                         #
    #                 ########################################################
    #                 if not glo_va.lock_response_server.acquire(False):
    #                     # Release lock just acquire above
    #                     glo_va.lock_init_state.release()
    #                     LogMesssage('[server___Listen_Reponse_Server]: Lock response server was already acquired, do not accept new message')
    #                     continue
                
    #                 ########################################################
    #                 # RESPONSE WITH DIFFERENT REQUEST ID                   #
    #                 ########################################################
    #                 if glo_va.timer.timer_id != timer_id:
    #                     glo_va.lock_response_server.release()
    #                     glo_va.lock_init_state.release()

    #                     LogMesssage('[server___Listen_Reponse_Server]: Receive response with different current request id')                        
    #                     LogMesssage('[server___Listen_Reponse_Server]: Acquire lock init state')
    #                     LogMesssage('[server___Listen_Reponse_Server]: Acquire lock response server')
    #                     continue

    #                 LogMesssage('[server___Listen_Reponse_Server]: Acquire lock init state')
    #                 LogMesssage('[server___Listen_Reponse_Server]: Acquire lock response server')

    #                 ########################################################
    #                 # CHECK REPONSE MESSAGES                              #
    #                 ########################################################
    #                 if glo_va.is_sending_message == True:
    #                     # Notify the timer that server is in lock
    #                     glo_va.turn = glo_va.TIMER_GOT_BY_SERVER
                        
    #                     # Clear timer
    #                     glo_va.timer.Clear_Timer()
    #                     LogMesssage('[server___Listen_Reponse_Server]: Clear Timer')
    #                     LogMesssage("[server___Listen_Reponse_Server]: Received response for request: {request_name} of timer_id: {timer_id}.".format(request_name=glo_va.list_request_name[type_request],timer_id=timer_id))
                        
    #                     ########################################################
    #                     # VALIDATION USERS RESPONSE                            #
    #                     ########################################################
    #                     if type_request == glo_va.SERVER_REQUEST_VALIDATION:
    #                         # glo_va.list_time_send_server.append(time.time()-glo_va.start_time)
    #                         # glo_va.times_send += 1
    #                         # if glo_va.times_send == 10:
    #                         #     print('Max time detec: {}'.format(np.max(glo_va.list_time_send_server)))
    #                         #     print('Min time detec: {}'.format(np.min(glo_va.list_time_send_server)))
    #                         #     print('Mean time detec: {}'.format(np.mean(glo_va.list_time_send_server)))
    #                         #     print('Std time detec: {}'.format(np.std(glo_va.list_time_send_server)))
    #                         ret_msg = str(payload['return'])
    #                         if ret_msg == "0":
    #                             user_infor.Update_Info(payload)
    #                             LogMesssage('[server___Listen_Reponse_Server]: Update patient information')

    #                         elif ret_msg == "-2":
    #                             # Patient is wearing mask
    #                             user_infor.wearingMask()
    #                             LogMesssage('[server___Listen_Reponse_Server]: Patient is wearing mask. Please push your mask off')
                            
    #                         elif ret_msg == "-3":
    #                             # Invalid SSN
    #                             LogMesssage('[server___Listen_Reponse_Server]: SSN for verifying patient is invalid')

    #                         elif ret_msg == "-1":
    #                             user_infor.NoFace()
    #                             glo_va.times_missing_face += 1
    #                             LogMesssage('[server___Listen_Reponse_Server]: Missing face times: {time}'.format(time=glo_va.times_missing_face))
                            
    #                         glo_va.has_response_server = True

    #                     ########################################################
    #                     # EXAMINATION SUBMISSION RESPONSE                     #
    #                     ########################################################
    #                     elif type_request == glo_va.SERVER_REQUEST_SUBMIT_EXAMINATION:
    #                         ret_msg = str(payload['return'])
    #                         if ret_msg == "0":
    #                             glo_va.return_stt = payload['stt']
    #                             LogMesssage('[server___Listen_Reponse_Server]: Receive STT: {stt} of patient: {id}'.format(stt=glo_va.return_stt, id=user_infor.patient_ID))
                            
    #                         else:
    #                             glo_va.return_stt = -1
    #                             LogMesssage('[server___Listen_Reponse_Server]: False receive STT: {stt} of patient: {id}'.format(stt=glo_va.return_stt, id=user_infor.patient_ID))

    #                         glo_va.has_response_server = True

    #                     ########################################################
    #                     # GET SYMPTONS USERS RESPONSE                          #
    #                     ########################################################
    #                     elif type_request == glo_va.SERVER_REQUEST_GET_SYMPTOMS:
    #                         ret_msg = str(payload['return'])
    #                         if ret_msg == "0":
    #                             glo_va.patient_symptons =  payload['symptons']
    #                             LogMesssage('[server___Listen_Reponse_Server]: Receive analyzed symptons of patient: {id}'.format(id=user_infor.patient_ID))
                            
    #                         elif ret_msg == "-1":
    #                             glo_va.patient_symptons = None
    #                             LogMesssage('[server___Listen_Reponse_Server]: False analyzed symptons of patient: {id}'.format(id=user_infor.patient_ID))

    #                         glo_va.has_response_server = True

    #                     ########################################################
    #                     # LOAD INIT PARAMETERS RESPONSE                        #
    #                     ########################################################
    #                     elif type_request == glo_va.SERVER_REQUEST_GET_INIT_PARA:
    #                         ret_msg = str(payload['return'])
    #                         if ret_msg == "0":
    #                             parameters = payload['parameters']
    #                             init_parameters.updateInitParameters(parameters)
    #                             LogMesssage('[server___Listen_Reponse_Server]: Success to get init parameters')

    #                         else:
    #                             init_parameters.status = ret_msg
    #                             LogMesssage('[server___Listen_Reponse_Server]: False to get init parameters')

    #                         glo_va.has_response_server = True

    #                 # Release lock
    #                 glo_va.lock_response_server.release()
    #                 LogMesssage('[server___Listen_Reponse_Server]: Release lock response server')

    #                 glo_va.lock_init_state.release()
    #                 LogMesssage('[server___Listen_Reponse_Server]: Release lock init state')

    #         except Exception as e:
    #             LogMesssage("Has error at module __Listen_Reponse_Server in server.py: {}".format(e), opt=2)

    #             if glo_va.lock_init_state.locked() == True:
    #                 glo_va.lock_init_state.release()
    #                 LogMesssage('[server___Listen_Reponse_Server]: Has error: {e}. Release lock init state'.format(e=e))

    #             if glo_va.lock_response_server.locked() == True:
    #                 glo_va.lock_response_server.release()
    #                 LogMesssage('[server___Listen_Reponse_Server]: Has error: {e}. Release lock response server'.format(e=e))

    #             if type_request == glo_va.SERVER_REQUEST_VALIDATION:
    #                 user_infor.Clear()

    #             elif type_request == glo_va.SERVER_REQUEST_GET_SYMPTOMS:
    #                 glo_va.patient_symptons = None

    #             elif type_request == glo_va.SERVER_REQUEST_GET_INIT_PARA:
    #                 init_parameters.Clear()

    #             glo_va.has_response_server = True

############################################################
# REQUEST                                                  #
############################################################
    ########################################################
    # Validate user                                        #
    ########################################################
    def Validate_User(self, list_embedded_face):
        # glo_va.start_time = time.time()
        try:
            event_data_batch = self.__producer.create_batch(partition_id=glo_va.PARTITION_ID)
            LogMesssage("[Validate_User]: Send validating message to server with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))

            try:
                data = EventData(list_embedded_face)
                data.properties = {
                    'request_id': glo_va.timer.timer_id,
                    'type_request': glo_va.SERVER_REQUEST_VALIDATION,
                    'device_ID': str(self.__device_ID),
                    'ssn': str(glo_va.check_ssn)
                }
                event_data_batch.add(data)

            except Exception as e:
                LogMesssage("[Validate_User]: Fail to send validating message to server with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))
                return
            
            self.__producer.send_batch(event_data_batch)

        except Exception as e:
            LogMesssage("Has error at module Validate_User in server.py: {}".format(e), opt=2)
    
    ########################################################
    # Submit_Examination                                   #
    ########################################################
    def Submit_Examination(self):
        try:
            event_data_batch = self.__producer.create_batch(partition_id=glo_va.PARTITION_ID)
            LogMesssage("[Submit_Examination]: Submit Examination with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))
            
            try:
                dep_name, building_code, room_code = exam.Get_Exam_Room_Infor()
                sensor_infor = sensor.sensor_infor
                msg = {
                    'request_id':glo_va.timer.timer_id,
                    'type_request': glo_va.SERVER_REQUEST_SUBMIT_EXAMINATION,
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
                LogMesssage("[Submit_Examination]: Fail to submit examination with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))
                return

            self.__producer.send_batch(event_data_batch)

        except Exception as e:
            LogMesssage("Has error at module Submit_Examination in server.py: {}".format(e), opt=2)

    ########################################################
    # getSymptonPatient                                    #
    ########################################################
    def getSymptonPatient(self, voice):
        try:
            event_data_batch = self.__producer.create_batch(partition_id=glo_va.PARTITION_ID)
            LogMesssage("[getSymptonPatient]: Get sympton patient with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))

            try:
                data = EventData(voice)
                data.properties = {
                    'request_id': glo_va.timer.timer_id,
                    'type_request': glo_va.SERVER_REQUEST_GET_SYMPTOMS,
                    'device_ID': str(self.__device_ID)
                }
                event_data_batch.add(data)
            
            except Exception as e:
                LogMesssage("[Submit_Examination]: Fail to get sympton patient with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))
                return

            self.__producer.send_batch(event_data_batch)

        except Exception as e:
            LogMesssage("Has error at module getSymptonPatient in server.py: {}".format(e), opt=2)
    
    ########################################################
    # getInitParameters                                    #
    ########################################################
    def getInitParameters(self):
        try:
            event_data_batch = self.__producer.create_batch(partition_id=glo_va.PARTITION_ID)
            LogMesssage("[getInitParameters]: Get init parameters with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))

            try:
                data = EventData('')
                data.properties = {
                    'request_id': glo_va.timer.timer_id,
                    'type_request': glo_va.SERVER_REQUEST_GET_INIT_PARA,
                    'device_ID': str(self.__device_ID)
                }
                event_data_batch.add(data)
            
            except Exception as e:
                LogMesssage("[getInitParameters]: Fail to get init parameters with timer_id: {timer_id}.".format(timer_id=glo_va.timer.timer_id))
                return

            self.__producer.send_batch(event_data_batch)

        except Exception as e:
            LogMesssage("Has error at module getInitParameters in server.py: {}".format(e), opt=2)

    async def closeIoTHubConnection(self):
        await self.__connection.shutdown()
    
    def closeEventHubConnection(self):
        self.__producer.close()

# server = Server()
# server.getInitParameters()
# while True:
#     selection = input("Press Q to quit\n")
#     if selection == "Q" or selection == "q":
#         print("Quitting...")
#         break
# loop = asyncio.get_event_loop()
# loop.run_until_complete(server.Close())
# loop.close()