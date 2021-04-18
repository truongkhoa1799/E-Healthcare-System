# MIT License
# Copyright (c) 2019 JetsonHacks
# See license
# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import cv2
import numpy as np
from utils.parameters import *
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
# import tensorflow as tf
# from tensorflow import keras
from identifying_users.face_recognition import Face_Recognition
glo_va.face_recognition = Face_Recognition()

mask_model = '/Users/khoa1799/GitHub/mask_detector/mask_detector.model'
# load the face mask detector model from disk
print("[INFO] loading face mask detector model...")
maskNet = load_model(mask_model)

# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Defaults to 1280x720 @ 60fps
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of the window on the screen


# def gstreamer_pipeline(
#     capture_width=1024,
#     capture_height=600,
#     display_width=1024,
#     display_height=600,
#     framerate=30,
#     flip_method=0,
# ):
#     return (
#         "nvarguscamerasrc ! "
#         "video/x-raw(memory:NVMM), "
#         "width=(int)%d, height=(int)%d, "
#         "format=(string)NV12, framerate=(fraction)%d/1 ! "
#         "nvvidconv flip-method=%d ! "
#         "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
#         "videoconvert ! "
#         "video/x-raw, format=(string)BGR ! appsink"
#         % (
#             capture_width,
#             capture_height,
#             framerate,
#             flip_method,
#             display_width,
#             display_height,
#         )
#     )




def show_camera():
    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    # print(gstreamer_pipeline(flip_method=0))
    labels = ['mask', 'unmask']
    # cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
        # Window
        while cv2.getWindowProperty("CSI Camera", 0) >= 0:
            ret_val, img = cap.read()
            mask_location = None

            margin_width = int((img.shape[1] - glo_va.LOCATION_RECOGNIZE_FACE_WIDTH) / 2)
            margin_height = int((img.shape[0] - glo_va.LOCATION_RECOGNIZE_FACE_HEIGHT) / 2)

            img = img[margin_height:glo_va.LOCATION_RECOGNIZE_FACE_HEIGHT+margin_height , margin_width:glo_va.LOCATION_RECOGNIZE_FACE_WIDTH+margin_width]

            fra = glo_va.MAX_LENGTH_IMG_NEW_USER / max(img.shape[0], img.shape[1]) 
            resized_img = cv2.resize(img, (int(img.shape[1] * fra), int(img.shape[0] * fra)))
            GRAY_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)

            face_locations = glo_va.face_recognition.Get_Face_Locations(GRAY_resized_img)

            if len(face_locations) != 0:
                face_location = face_locations[0]
                top = int(face_location[0] / fra)
                bottom = int(face_location[2] / fra)
                left = int(face_location[3] / fra)
                right = int(face_location[1] / fra)

                mask_location = img[top:bottom, left:right]
                face = cv2.resize(mask_location, (224, 224))
                face = img_to_array(face)
                face = preprocess_input(face)

                faces = np.array([face], dtype="float32")
                preds = maskNet.predict(faces, batch_size=32)

                print(labels[preds[0].argmax()])

                cv2.rectangle(img, (left, top), (right, bottom) , (2, 255, 0), 2)

            cv2.imshow("CSI Camera", img)
            # This also acts as
            keyCode = cv2.waitKey(30) & 0xFF
            # Stop the program on the ESC key
            if keyCode == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Unable to open camera")


if __name__ == "__main__":
    show_camera()
