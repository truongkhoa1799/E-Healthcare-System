# from utils.parameters import *
# import cv2
# import os, re, uuid
# import numpy as np

# from azure.iot.device import IoTHubDeviceClient
# from azure.core.exceptions import AzureError

# from identifying_users.face_recognition import Face_Recognition
# from communicate_server.server import Server
# from utils.timer import Timer
# from utils.common_functions import Compose_Embedded_Face

# ORIGINAL_DATA = '/home/thesis/Documents/E-Healthcare-System-Server/Manipulate_Data/Original_Face'
# list_name = []
# def __image_files_in_folder(folder):
#     return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

# def test_validate(user_id):
#     list_faces = ""
#     glo_va.timer = Timer()
#     glo_va.server = Server()
#     glo_va.face_recognition = Face_Recognition()

#     for img in __image_files_in_folder(ORIGINAL_DATA + '/test/' + str(user_id)):
#         glo_va.img = cv2.imread(img)

#         ret = glo_va.face_recognition.Get_Face()
#         if ret == -2:
#             print("Error Face locations")
#             return
#         elif ret == 0:
#             # Face Identifying
#             print(img)
#             glo_va.face_recognition.Encoding_Face()
#             encoded_img_string = Compose_Embedded_Face(glo_va.embedded_face)
#             list_faces += encoded_img_string + ' '
        
#     print(len(list_faces))
#     glo_va.list_embedded_face = list_faces
#     glo_va.timer.Start_Timer(glo_va.OPT_TIMER_VALIDATE)
#     glo_va.is_sending_message = True
#     glo_va.server.Validate_User()

# test_validate(3)