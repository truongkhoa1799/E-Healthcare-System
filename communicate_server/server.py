from azure.eventhub import EventData, EventHubProducerClient
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

import sys
import time
import pickle
import threading

PROJECT_PATH = '/home/thesis/Documents/thesis/E-Healthcare-System/'
sys.path.append(PROJECT_PATH)
from utils.parameters import *

class Server:
    def __init__(self):
        # IOT hub, event hub connection
        self.__device_ID = None
        self.__device_iothub_connection = None
        self.__eventhub_connection = None
        self.__eventhub_name = None

        self.__LoadConnection()

        self.__connection = IoTHubDeviceClient.create_from_connection_string(self.__device_iothub_connection)
        self.__producer = EventHubProducerClient.from_connection_string(
            conn_str=self.__eventhub_connection,
            eventhub_name=self.__eventhub_name
        )

        # Start a thread to listen 
        self.__listening_server_thread = threading.Thread(target=self.__Listen_Reponse_Server, args=(self.__connection,))
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
            
    # When server receive response:
    #   1: Clear Timer, so that timer is not trigged
    def __Listen_Reponse_Server(self, connection):
        while True:
            try:
                method_request = connection.receive_method_request()
                timer_id = method_request.payload['request_id']

                glo_va.lock_response_server.acquire()
                # if timer did not time out, receive timer and clear timer
                if glo_va.is_sending_message == True:
                    # Notify the timer that server is in lock
                    glo_va.turn = 1

                    # Clear timer
                    glo_va.timer.Clear_Timer()

                    # Release lock
                    glo_va.lock_response_server.release()

                    current_time = time.strftime("%H:%M:%S", time.localtime())
                    print("[{time}]: Received response for request: {request_name} of timer_id: {timer_id} for {name}.".format(time=current_time, request_name=method_request.name,timer_id=timer_id, name=method_request.name))
                    
                    # Validation response
                    if method_request.name == "Validate_User" and glo_va.timer.timer_id == timer_id:
                        response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                        response_status = 200

                        ret_msg = int(method_request.payload['return'])
                        if ret_msg == 0:
                            # print(method_request.payload)
                            user_infor.Update_Info(method_request.payload)
                        elif glo_va.STATE == 1 and ret_msg == -1:
                            glo_va.times_missing_face += 1

                        glo_va.has_response_server = True

                    # Get examination room response
                    elif method_request.name == "Get_Examination_Room" and glo_va.timer.timer_id == timer_id:
                        response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                        response_status = 200

                        ret_msg = int(method_request.payload['return'])
                        if ret_msg == 0:
                            glo_va.has_examination_room = True
                            glo_va.list_examination_room = method_request.payload['msg']
                            glo_va.hospital_ID = method_request.payload['hospital_ID']
                        else:
                            glo_va.has_examination_room = False

                        glo_va.has_response_server = True

                        # Submit examination request response
                    elif method_request.name == "Submit_Examination" and glo_va.timer.timer_id == timer_id:
                        response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                        response_status = 200

                        ret_msg = int(method_request.payload['return'])
                        if ret_msg == 0:
                            glo_va.return_stt = method_request.payload['stt']

                        glo_va.has_response_server = True
                    else:
                        response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
                        response_status = 404
                else:
                    # if timer did timeout first, discard this response and wait for next response
                    glo_va.lock_response_server.release()
                    response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                    response_status = 200

                method_response = MethodResponse(method_request.request_id, response_status, payload=response_payload)
                connection.send_method_response(method_response)
            except Exception as e:
                print("Has error at module __Listen_Reponse_Server in server.py: {}".format(e))
                glo_va.STATE = -1
        

    def Validate_User(self):
        try:
            event_data_batch = self.__producer.create_batch()
            try:
                current_time = time.strftime("%H:%M:%S", time.localtime())
                print("[{time}]: Send validating message to server with timer_id: {timer_id}.".format(time=current_time, timer_id=glo_va.timer.timer_id))
                data = EventData(glo_va.list_embedded_face)
                data.properties = {'request_id':glo_va.timer.timer_id,'type_request':"0", 'device_ID': str(self.__device_ID)}
                event_data_batch.add(data)
            except Exception as e:
                print(e)
                glo_va.STATE = -1
            self.__producer.send_batch(event_data_batch)
        except Exception as e:
            print("Has error at module Validate_User in server.py: {}".format(e))
            glo_va.STATE = -1
    
    def Get_Examination_Room(self):
        try:
            event_data_batch = self.__producer.create_batch()
            try:
                current_time = time.strftime("%H:%M:%S", time.localtime())
                print("[{time}]: Get Examination Room with timer_id: {timer_id}.".format(time=current_time, timer_id=glo_va.timer.timer_id))
                data = EventData("")
                data.properties = {'request_id':glo_va.timer.timer_id,'type_request':"4", 'device_ID': str(self.__device_ID)}
                event_data_batch.add(data)
            except Exception as e:
                print(e)
                glo_va.STATE = -1
            self.__producer.send_batch(event_data_batch)
        except Exception as e:
            print("Has error at module Get_Examination_Room in server.py: {}".format(e))
            glo_va.STATE = -1
    
    def Submit_Examination(self):
        try:
            event_data_batch = self.__producer.create_batch()
            try:
                current_time = time.strftime("%H:%M:%S", time.localtime())
                print("[{time}]: Submit Examination with timer_id: {timer_id}.".format(time=current_time, timer_id=glo_va.timer.timer_id))
                
                building_code, room_code = exam.Get_Buidling_Room()
                blood_pressure, pulse, thermal, spo2 = sensor.Get_Data()
                msg = {
                    'request_id':glo_va.timer.timer_id,
                    'type_request': "5",
                    'device_ID': str(self.__device_ID),
                    'hospital_ID': str(glo_va.hospital_ID),
                    'building_code': building_code,
                    'room_code': room_code,
                    'blood_pressure': str(blood_pressure),
                    'pulse': str(pulse),
                    'thermal': str(thermal),
                    'spo2': str(spo2),
                    'height': str(175.5),
                    'weight': str(75.4)
                }
                
                # Check is new user
                if len(glo_va.list_embedded_face_new_user) != 0:
                    data = EventData(glo_va.list_embedded_face_new_user)
                    msg['patient_ID'] = str(-1)
                else:
                    data = EventData("")
                    msg['patient_ID'] = str(glo_va.patient_ID)

                data.properties = msg
                event_data_batch.add(data)
            except Exception as e:
                print(e)
                glo_va.STATE = -1
            self.__producer.send_batch(event_data_batch)
        except Exception as e:
            print("Has error at module Submit_Examination in server.py: {}".format(e))
            glo_va.STATE = -1

    def Close(self):
        # self.__listening_server_thread.join()
        self.__producer.close()
        self.__connection.disconnect()

# server = Server()
# server.Validate_User()
# server.Close()