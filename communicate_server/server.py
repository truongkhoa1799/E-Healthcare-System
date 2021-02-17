from azure.eventhub import EventData, EventHubProducerClient
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

import sys
import pickle
import threading
sys.path.append('/home/thesis/Documents/E-Healthcare-System')
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
        with open (CONNECTION_LIST_PATH, 'rb') as fp_1:
            ret = pickle.load(fp_1)
            self.__device_ID = ret['device_ID']
            self.__device_iothub_connection = ret['device_iothub_connection']
            self.__eventhub_connection = ret['eventhub_connection']
            self.__eventhub_name = ret['eventhub_name']

    def __Listen_Reponse_Server(self, connection):
        while True:
            method_request = connection.receive_method_request()
            if method_request.name == "Validate_User":
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
                ret_msg = int(method_request.payload['return'])
                print("\tReceived response from server: {}".format(ret_msg))
                if ret_msg == 0:
                    user_infor.name = method_request.payload['name']
                    user_infor.birthday = method_request.payload['birthday']
                    user_infor.phone = method_request.payload['phone']
                    user_infor.address = method_request.payload['address']
                    glo_va.has_response_server = True
            else:
                response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
                response_status = 404

            method_response = MethodResponse(method_request.request_id, response_status, payload=response_payload)
            connection.send_method_response(method_response)

    def Validate_User(self):
        try:
            event_data_batch = self.__producer.create_batch()
            try:
                data = EventData(glo_va.list_embedded_face)
                data.properties = {'type_request':"0", 'device_ID': str(self.__device_ID)}
                event_data_batch.add(data)
            except Exception as e:
                print(e)
                glo_va.STATE = -1
            self.__producer.send_batch(event_data_batch)
        except Exception as e:
            print("Has error at module Validate_User in server.py: {}".format(e))
            glo_va.STATE = -1

    def Close(self):
        # self.__listening_server_thread.join()
        self.__producer.close()
        self.__connection.disconnect()

# server = Server()
# server.Validate_User()
# server.Close()