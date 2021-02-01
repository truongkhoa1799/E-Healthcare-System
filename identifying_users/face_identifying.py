import os
import json
import pickle
import numpy as np

# import face_recognition
import dlib
from sklearn import neighbors
from utils.parameters import *

class FaceIdentify:
    ###############################################################################################
    # __init__                                                                                    #
    # Input:                                                                                      #
    #   list_ndarray    self.__known_face_encodings :   List of face encoded                      #
    #   list_str        self.__known_face_IDs       :   List of face ID according to face encoded #
    # Output:                                                                                     #
    #   None            None                        :   None                                      #
    ###############################################################################################
    def __init__(self):
        self.__list_patient = {}
        self.__known_face_encodings = []
        self.__known_face_IDs = []
        self.__knn_clf = None

        self.pose_predictor_5_point = dlib.shape_predictor(PREDICTOR_5_POINT_MODEL)
        self.face_encoder = dlib.face_recognition_model_v1(RESNET_MODEL)

        ret, self.__known_face_IDs, self.__known_face_encodings = self.__LoadData()
        if ret == -1:
            print("There is no user id or encoding face face to load")
            exit(-1)

        ret, self.__knn_clf = self.__LoadKNNModel(KNN_MODEL_PATH)
        if ret == -1:
            print("There is KNN model to load")
            exit(-1)

        ret, self.__list_patient = self.__ReadPatientsInfo()
        if ret == -1:
            print("There Patient info to load")
            exit(-1)

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
        return [np.array(self.face_encoder.compute_face_descriptor(face_image, raw_landmark_set, 1)) for raw_landmark_set in raw_landmarks]

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

        return [self.pose_predictor_5_point(face_image, face_location) for face_location in face_locations]

    ###############################################################################################
    # __ReadPatientsInfo                                                                                  #                    
    # Input:                                                                                      #
    #   None            None                        :   None                                      #
    # Output:                                                                                     #
    #   ret             int                         :   -1 No Data Loaded, 0 success              #
    ###############################################################################################
    def __ReadPatientsInfo(self):
        if not os.path.exists(PATIENT_FILE):
            return -1, None

        info = None
        with open(PATIENT_FILE, 'r') as json_file:
            info = json.load(json_file)

        list = info['patients_info']
        for user in list:
            self.__list_patient[user['patient_id']] = user['name']
        
        return 0, self.__list_patient

    ###############################################################################################
    # __LoadData                                                                                  #                    
    # Input:                                                                                      #
    #   None            None                        :   None                                      #
    # Output:                                                                                     #
    #   ret             int                         :   -1 No Data Loaded, 0 success              #
    ###############################################################################################
    def __LoadData(self):
        known_face_IDs = None
        known_face_encodings = None
        if not os.path.exists(PATH_USER_ID):
            return -1, None, None

        with open (PATH_USER_ID, 'rb') as fp_1:
            known_face_IDs = pickle.load(fp_1)

        if not os.path.exists(PATH_USER_IMG_ENCODED):
            return -1, None, None

        with open (PATH_USER_IMG_ENCODED, 'rb') as fp_2:
            known_face_encodings = pickle.load(fp_2)
        
        return 0, known_face_IDs, known_face_encodings
    
    #################################################################################
    # __LoadKNNModel                                                                #                    
    # Input:                                                                        #
    #   model_path      :   path to save model                                      #
    # Output:                                                                       #
    #   ret             :   -1 no path, 0 success                                   #
    #   knn_clf         :   Model                                                   #
    #################################################################################
    def __LoadKNNModel(self,model_path):
        if not os.path.exists(model_path):
            return -1, None

        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)
            return 0, knn_clf
    
    ###############################################################################################
    # GetFaceID                                                                                   #                    
    # Input:                                                                                      #
    #   ndarray         img                         :                                             #
    # Output:                                                                                     #
    #   Str             UserID                      :                                             #
    ###############################################################################################
    def GetFaceID(self):
        closet_distances = self.__knn_clf.kneighbors(glo_va.embedded_face, n_neighbors = NUM_NEIGHBROS)
        face_id = self.__knn_clf.predict(glo_va.embedded_face)

        meet_condition_threshold = [closet_distances[0][0][i] <= THRESHOLD_FACE_REC for i in range(len(closet_distances[0][0]))]
        for i in range(len(meet_condition_threshold)):
            if self.__known_face_IDs[closet_distances[1][0][i]] == face_id[-1] and meet_condition_threshold[i]:
                try:
                    return self.__list_patient[face_id[-1]], closet_distances[0][0][i]
                except:
                    print("There is no face ins database")
                    return "Null", 0
        return "Null", 0

# if __name__ == '__main__':
#     # print('TrtThread: loading the TRT model...')
#     print("Test with RGB converter")
#     test = FaceIdentify()
#     test.Test()