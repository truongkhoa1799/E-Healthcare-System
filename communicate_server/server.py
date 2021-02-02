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
        device_method_thread = threading.Thread(target=self.__Listen_Reponse_Server, args=(self.__connection,))
        device_method_thread.daemon = True
        device_method_thread.start()

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
            print (
                "\nMethod callback called with:\nmethodName = {method_name}\npayload = {payload}".format(
                    method_name=method_request.name,
                    payload=method_request.payload
                )
            )
            if method_request.name == "Validate_User":
                print(method_request.payload)
                response_payload = {"Response": "Executed direct method {}".format(method_request.name)}
                response_status = 200
            else:
                response_payload = {"Response": "Direct method {} not defined".format(method_request.name)}
                response_status = 404

            method_response = MethodResponse(method_request.request_id, response_status, payload=response_payload)
            connection.send_method_response(method_response)

            glo_va.patient_id = method_request.payload['answer']
    
    def Validate_User(self):
        try:
            event_data_batch = self.__producer.create_batch()
            try:
                data = EventData(glo_va.list_encoded_img)
                # data = EventData("Hello")
                data.properties = {'type_request':"0", 'device_ID': str(self.__device_ID)}
                event_data_batch.add(data)
            except Exception as e:
                print(e)
                glo_va.STATE = -1
            self.__producer.send_batch(event_data_batch)
        except Exception as e:
            print(e)
            glo_va.STATE = -1

    def Close(self):
        self.__producer.close()
        self.__connection.disconnect()

# server = Server()
# server.Validate_User()
# server.Close()