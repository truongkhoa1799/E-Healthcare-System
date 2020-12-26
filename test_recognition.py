import re
import os
import cv2
import json
import pickle
import time
from sklearn import svm
import numpy as np
import face_recognition
import numpy as numpy

KNN_MODEL_PATH = "/Users/khoa1799/Documents/E-Healthcare-System/Data/knn_clf_model.clf"
PATH_USER_IMG_ENCODED = "/Users/khoa1799/Documents/E-Healthcare-System/Data/Encoded_Face"
PATH_USER_ID = "/Users/khoa1799/Documents/E-Healthcare-System/Data/ID_Face"
FACE_TEST_PATH = "/Users/khoa1799/Documents/E-Healthcare-System/Data/test"
NUM_NEIGHBROS = 5
THRESHOLD_FACE_REC = 0.5
IMAGE_SIZE = 150

from sklearn.model_selection import GridSearchCV
from sklearn import preprocessing
encoder = preprocessing.LabelEncoder()
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()


global known_face_IDs
global known_face_encodings
global knn_clf
global svm_clf

def image_files_in_folder(folder):
        return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

def LoadKNNModel():
    global knn_clf

    if not os.path.exists(KNN_MODEL_PATH):
        print("There is KNN model to load")
        exit(-1)

    with open(KNN_MODEL_PATH, 'rb') as f:
        knn_clf = pickle.load(f)

def TrainKNN(n_neighbors, knn_algorithm, knn_weights, model_save_path):
    print("Starting train KNN Model")
    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(self.__known_face_encodings))))
        print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algorithm, weights=knn_weights)

    # self.__known_face_encodings is list of ndarray
    # self.__known_face_IDs is list of str
    knn_clf.fit(self.__known_face_encodings, self.__known_face_IDs)

    ret = self.__SaveKNNModel(knn_clf, KNN_MODEL_PATH)

    print("Finishing train KNN Model")
    return knn_clf

def LoadData():
    global known_face_IDs
    global known_face_encodings

    known_face_IDs = []
    known_face_encodings = []
    if not os.path.exists(PATH_USER_ID):
        print("There is no user id face to load")
        exit(-1)

    with open (PATH_USER_ID, 'rb') as fp_1:
        known_face_IDs = pickle.load(fp_1)

    if not os.path.exists(PATH_USER_IMG_ENCODED):
        print("There is no user encoding face to load")
        exit(-1)

    with open (PATH_USER_IMG_ENCODED, 'rb') as fp_2:
        known_face_encodings = pickle.load(fp_2)

def GetFaceID(embedded_face):
    global known_face_IDs
    global known_face_encodings
    global knn_clf
    global svm_clf

    # closet_distances = knn_clf.kneighbors(embedded_face, n_neighbors = NUM_NEIGHBROS)
    # face_id = knn_clf.predict(embedded_face)

    # meet_condition_threshold = [closet_distances[0][0][i] <= THRESHOLD_FACE_REC for i in range(len(closet_distances[0][0]))]
    # for i in range(len(meet_condition_threshold)):
    #     if known_face_IDs[closet_distances[1][0][i]] == face_id[-1] and meet_condition_threshold[i]:
    #         return face_id[-1], closet_distances[0][0][i]
            
    # return "Null", 0

    X_test_scaled = scaler.fit_transform(embedded_face)
    face_id = svm_clf.predict(X_test_scaled)
    return face_id, 0

if __name__ == '__main__':
    LoadData()
    LoadKNNModel()
    TrainSVM()

    print("\tStarting test")
    # time_request = time.time()
    # Loop through each person in the training set
    for class_dir in os.listdir(FACE_TEST_PATH):
        print(class_dir)
        if not os.path.isdir(os.path.join(FACE_TEST_PATH, class_dir)):
            continue
    
        # Loop through each training image for the current person and past image path for encoing individualy
        for img in image_files_in_folder(os.path.join(FACE_TEST_PATH, class_dir)):
            path = img.split('/')
            user_ID = class_dir
            img_name = path[-1]
            time_st = time.time()
            loaded_img = cv2.imread( img )
            
            fra = IMAGE_SIZE / max(loaded_img.shape[0], loaded_img.shape[1]) 
            resized_img = cv2.resize(loaded_img, (int(loaded_img.shape[1] * fra), int(loaded_img.shape[0] * fra)))
            RGB_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
            embedded_face = face_recognition.face_encodings(RGB_resized_img, [(0,150,150,0)])[0]
            embedded_face = np.array(embedded_face).reshape(1,-1)

            face_id, distance = GetFaceID(embedded_face)
            
            print("User: {}, distance: {}, time to decode: {}".format(face_id, distance, time.time() - time_st))
        print()

    # print(self.__known_face_IDs)
    