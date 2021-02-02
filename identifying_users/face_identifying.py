import os
import time
import json
import pickle
import numpy as np

import cv2
# import face_recognition
import dlib
from sklearn import neighbors
from utils.parameters import *

class FaceIdentifier:
    ###############################################################################################
    # __init__                                                                                    #
    # Input:                                                                                      #
    #   list_ndarray    self.__known_face_encodings :   List of face encoded                      #
    #   list_str        self.__known_face_IDs       :   List of face ID according to face encoded #
    # Output:                                                                                     #
    #   None            None                        :   None                                      #
    ###############################################################################################
    def __init__(self):
        self.__known_face_encodings = []
        self.__known_face_IDs = []
        self.__knn_clf = None

        self.__pose_predictor_5_point = dlib.shape_predictor(PREDICTOR_5_POINT_MODEL)
        self.__face_encoder = dlib.face_recognition_model_v1(RESNET_MODEL)
        
        test_img = cv2.imread(FACE_TEST_PATH + '/00002/0-khoa_1.jpeg')
        resized_img = cv2.resize(test_img, (IMAGE_SIZE,IMAGE_SIZE))
        test_encoded = self.face_encodings(resized_img, [(1, 149, 1, 149)])
        time.sleep(1)
        print("\tDone load dlib model")

        self.__Load_Data(PATH_USER_ID, PATH_USER_IMG_ENCODED)

        self.__Load_KNN_Model(KNN_MODEL_PATH)

    ###############################################################################################
    # face_encodings                                                                              #
    # Input:                                                                                      #
    #   list_ndarray    face_image :   image to encode                                            #
    #   list_str        known_face_locations       :   bounding box for face                      #
    # Output:                                                                                     #
    #   None            128-vector                        :   encoding vector                     #
    ###############################################################################################
    def face_encodings(self, face_image, known_face_locations):
        raw_landmarks = self._raw_face_landmarks(face_image, known_face_locations)
        return [np.array(self.__face_encoder.compute_face_descriptor(face_image, raw_landmark_set, 1)) for raw_landmark_set in raw_landmarks]

    ###############################################################################################
    # _css_to_rect                                                                                #
    # Input:                                                                                      #
    #   list_ndarray    css(left, top, right, bottm)            :   bounding box                  #
    # Output:                                                                                     #
    #   None            dlib.rectangle(bottom, left, top, right):   encoding vector               #
    ###############################################################################################
    def _css_to_rect(self, css):
        return dlib.rectangle(css[3], css[0], css[1], css[2])

    def _raw_face_landmarks(self, face_image, face_locations):
        if face_locations is None:
            face_locations = self._raw_face_locations(face_image)
        else:
            face_locations = [self._css_to_rect(face_location) for face_location in face_locations]

        return [self.__pose_predictor_5_point(face_image, face_location) for face_location in face_locations]

    ###############################################################################################
    # __Load_Data                                                                                  #                    
    # Input:                                                                                      #
    #   None            None                        :   None                                      #
    # Output:                                                                                     #
    #   ret             int                         :   -1 No Data Loaded, 0 success              #
    ###############################################################################################
    def __Load_Data(self, user_id_path, encoding_img_path):
        with open (user_id_path, 'rb') as fp_1:
            self.__known_face_IDs = pickle.load(fp_1)

        with open (encoding_img_path, 'rb') as fp_2:
            self.__known_face_encodings = pickle.load(fp_2)
    
    #################################################################################
    # __Load_KNN_Model                                                                #                    
    # Input:                                                                        #
    #   model_path      :   path to save model                                      #
    # Output:                                                                       #
    #   ret             :   -1 no path, 0 success                                   #
    #   knn_clf         :   Model                                                   #
    #################################################################################
    def __Load_KNN_Model(self,model_path):
        with open(model_path, 'rb') as f:
            self.__knn_clf = pickle.load(f)
    
    ###############################################################################################
    # GetFaceID                                                                                   #                    
    # Input:                                                                                      #
    #   ndarray         img                         :                                             #
    # Output:                                                                                     #
    #   Str             UserID                      :                                             #
    ###############################################################################################
    def Get_User_ID(self):
        closet_distances = self.__knn_clf.kneighbors(glo_va.embedded_face, n_neighbors = NUM_NEIGHBROS)
        face_id = self.__knn_clf.predict(glo_va.embedded_face)
        meet_condition_threshold = [closet_distances[0][0][i] <= THRESHOLD_FACE_REC for i in range(len(closet_distances[0][0]))]

        for i in range(len(meet_condition_threshold)):
            if self.__known_face_IDs[closet_distances[1][0][i]] == face_id[-1] and meet_condition_threshold[i]:
                return face_id[-1]
        return -1

# # print('TrtThread: loading the TRT model...')
# print("Test with RGB converter")
# test = FaceIdentifier()