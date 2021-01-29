import sys
sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')
import asyncio
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

from utils.parameters import *

import os
import re
import cv2
import time
import pickle
import numpy as np
from sklearn import neighbors
import threading
import dlib

pose_predictor_5_point = dlib.shape_predictor(PREDICTOR_5_POINT_MODEL)
face_encoder = dlib.face_recognition_model_v1(RESNET_MODEL)

FLAG = True
global time_st
time_request = []
time_response = []

def face_encodings(face_image, known_face_locations):
    raw_landmarks = _raw_face_landmarks(face_image, known_face_locations)
    return [np.array(face_encoder.compute_face_descriptor(face_image, raw_landmark_set, 1)) for raw_landmark_set in raw_landmarks]

def _css_to_rect(css):
    return dlib.rectangle(css[3], css[0], css[1], css[2])

def _raw_face_landmarks(face_image, face_locations):
    if face_locations is None:
        face_locations = _raw_face_locations(face_image)
    else:
        face_locations = [_css_to_rect(face_location) for face_location in face_locations]

    pose_predictor = pose_predictor_5_point

    return [pose_predictor(face_image, face_location) for face_location in face_locations]

def preprocessing(img):
    # Resize image
    resized_img = cv2.resize(img, (IMAGE_SIZE,IMAGE_SIZE))

    # Adjust bright image
    hsv_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2HSV) #convert it to hsv
    v = hsv_img[:, :, 2]
    mean_v = np.mean(v)
    diff = BASE_BRIGHTNESS - mean_v
                   
    if diff < 0:
        v = np.where(v < abs(diff), v, v + diff)
    else:
        v = np.where( v + diff > 255, v, v + diff)

    hsv_img[:, :, 2] = v
    adjust_bright_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)

    # Change to RGB image
    RGB_resized_img = cv2.cvtColor(adjust_bright_img, cv2.COLOR_BGR2RGB)

    # return RGB image
    return RGB_resized_img

def Compose_String(encoded_img):
    ret_string = ""
    for i in encoded_img:
        precision_i = '%.20f'%np.float64(i)
        ret_string += str(precision_i) + '/'
    
    return ret_string

def Get_Encoded_Img(img):
    processed_img = preprocessing(img)
    encoded_img = face_encodings(processed_img, [(0,IMAGE_SIZE,IMAGE_SIZE,0)])[0]
    encoded_img_string = Compose_String(encoded_img)

    for i in range(10):
        glo_va.list_encoded_img += encoded_img_string + ' '

def LoadConnection():
    if not os.path.exists(CONNECTION_LIST_PATH):
        return -1

    with open (CONNECTION_LIST_PATH, 'rb') as fp_1:
        ret = pickle.load(fp_1)
        glo_va.device_ID = ret['device_ID']
        glo_va.device_iothub_connection = ret['device_iothub_connection']
        glo_va.eventhub_connection = ret['eventhub_connection']
        glo_va.eventhub_name = ret['eventhub_name']
        # print(glo_va.device_iothub_connection)
        # print(glo_va.eventhub_connection)
        # print(glo_va.eventhub_name)

    return 0

def Listen_Reponse_Server(connection):
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

        glo_va.has_response_server = True


async def Validate_User(producer):
    # Create a producer client to send messages to the event hub.
    # Specify a connection string to your event hubs namespace and
    # the event hub name.
    async with producer:
        global time_st
        time_st = time.time()
        test_img = cv2.imread(FACE_TEST_PATH + '/00002/0-Khoa_1.jpeg')
        Get_Encoded_Img(test_img)

        event_data_batch = await producer.create_batch()
        data = EventData(glo_va.list_encoded_img)
        data.properties = {'type_request':"0", 'device_ID': str(glo_va.device_ID)}
        event_data_batch.add(data)
        await producer.send_batch(event_data_batch)

if __name__ == '__main__':
    glo_va.has_response_server = False
    LoadConnection()
    connection = IoTHubDeviceClient.create_from_connection_string(glo_va.device_iothub_connection)
    producer = EventHubProducerClient.from_connection_string(
        conn_str=glo_va.eventhub_connection,
        eventhub_name=glo_va.eventhub_name
    )
    
    # Start a thread to listen 
    device_method_thread = threading.Thread(target=Listen_Reponse_Server, args=(connection,))
    device_method_thread.daemon = True
    device_method_thread.start()

    test_img = cv2.imread(FACE_TRAIN_PATH + '/00002/0-Khoa3.jpeg')
    test_encoded = face_encodings(test_img, [(0,IMAGE_SIZE,IMAGE_SIZE,0)])[0]

    print("Start identifying user")
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Validate_User(producer))

    while glo_va.has_response_server == False:
        continue
    
    print(time.time()-time_st)
    # print("Hello 1")
    # # # => 3072 = (1 + 1 + 1 + 20 + 1)*128 bytes for 1 image
    # # test_2 = test.split('/')
    # # ans = [np.float64(i) for i in test_2 if i != '']
    # # print(ans == embedded_face)