import os
import re
import cv2
import time
import pickle
import numpy as np
from sklearn import neighbors
import dlib

TRAIN_IMG = '/Users/khoa1799/GitHub/E-Healthcare-System/DATA/train/'

LWF_PATH_USER_ID = '/Users/khoa1799/GitHub/E-Healthcare-System/model_engine/LWF_ID_Face'
LWF_PATH_USER_IMG_ENCODED = '/Users/khoa1799/GitHub/E-Healthcare-System/model_engine/LWF_Encoded_Face'
LWF_KNN_MODEL_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System/model_engine/LWF_knn_clf_model.clf"
LWF_SVM_MODEL_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System/model_engine/LWF_svm_clf_model.clf"

PREDICTOR_5_POINT_MODEL = '/Users/khoa1799/GitHub/E-Healthcare-System/model_engine/shape_predictor_5_face_landmarks.dat'
RESNET_MODEL = '/Users/khoa1799/GitHub/E-Healthcare-System//model_engine/dlib_face_recognition_resnet_model_v1.dat'

IMAGE_SIZE = 150

BASE_BRIGHTNESS = 180
IMAGE_SIZE = 150

pose_predictor_5_point = dlib.shape_predictor(PREDICTOR_5_POINT_MODEL)
face_encoder = dlib.face_recognition_model_v1(RESNET_MODEL)

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

img = cv2.imread(TRAIN_IMG + '00002/0-Khoa3.jpeg')
img = preprocessing(img)

# cv2.imshow('test', img)
# cv2.waitKey(2000)

embedded_face = face_encodings(img, [(0,IMAGE_SIZE,IMAGE_SIZE,0)])[0]
test = ""
num_sign = 0
for i in embedded_face:
    if i<0:
        num_sign+=1
    precision_i = '%.20f'%np.float64(i)
    test += str(precision_i) + '/'

print(len(test) + 128 - num_sign)
print()
print(test)
print()

# => 3072 = (1 + 1 + 1 + 20 + 1)*128 bytes for 1 image
test_2 = test.split('/')
ans = [np.float64(i) for i in test_2 if i != '']
print(ans == embedded_face)
