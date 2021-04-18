# import the necessary packages
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import argparse
import imutils
import time
import cv2
import os

from utils.parameters import *
from identifying_users.face_recognition import Face_Recognition
glo_va.face_recognition = Face_Recognition()

mask_model = '/Users/khoa1799/GitHub/mask_detector/mask_detector.model'
# load the face mask detector model from disk
print("[INFO] loading face mask detector model...")
maskNet = load_model(mask_model)

# img_path = '/Users/khoa1799/GitHub/mask_detector/original_img/unmask/1.jpg'
img_path = '/Users/khoa1799/GitHub/mask_detector/original_img/mask/437.jpg'
img = cv2.imread(img_path)

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
    print(preds)

cv2.imshow('test', mask_location)
cv2.waitKey(5000)

# face_location 
# face = cv2.resize(face, (224, 224))
# face = img_to_array(face)
# face = preprocess_input(face)