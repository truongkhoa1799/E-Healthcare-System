import re
import os
import cv2
import json
import pickle
import numpy as numpy
import sys, glob, time
import pycuda.driver as cuda

import face_recognition
from sklearn import neighbors
from common_functions import *
from face_detector_CenterFace import *

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

        ret = self.__LoadData()
        self.__knn_clf = self.__LoadKNNModel(KNN_MODEL_PATH)

        xml_file = self.__ReadXML()
        self.__list_patient = self.__ReadPatientsInfo(xml_file)
    
    def __ReadXML(self):
        with open(PATIENT_FILE, 'r') as json_file:
            info = json.load(json_file)
            return info

    def __ReadPatientsInfo(self,info):
        list = info['patients_info']
        for user in list:
            self.__list_patient[user['patient_id']] = user['name']
        
        return self.__list_patient

    ###############################################################################################
    # __LoadNewData                                                                               #                    
    # Input:                                                                                      #
    #   None            None                        :   None                                      #
    # Output:                                                                                     #
    #   ret                                         :   -1 No Data Loaded, 0 success              #
    ###############################################################################################
    def __LoadNewData(self):
        time_request = time.time()

        # Creating a list that store each encoding thread
        list_thread_encoding_image = []

        # Loop through each person in the training set
        for class_dir in os.listdir(FACE_TRAIN_PATH):
            print(class_dir)
            if not os.path.isdir(os.path.join(FACE_TRAIN_PATH, class_dir)):
                continue
        
            # Loop through each training image for the current person and past image path for encoing individualy
            for img in self.__image_files_in_folder(os.path.join(FACE_TRAIN_PATH, class_dir)):
                path = img.split('/')
                user_ID = class_dir
                img_name = path[-1]
                loaded_img = cv2.imread( img )
                print("Loaded image {} ".format(img_name))
                
                # embedded_face: type ndarray (256,)
                # embedded_face = self.__face_iden(loaded_img)
                fra = IMAGE_SIZE / max(loaded_img.shape[0], loaded_img.shape[1]) 
                resized_img = cv2.resize(loaded_img, (int(loaded_img.shape[1] * fra), int(loaded_img.shape[0] * fra)))
                RGB_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
                embedded_face = face_recognition.face_encodings(RGB_resized_img, [(0,150,150,0)])[0]
                # embedded_face = np.array(embedded_face).reshape(-1,1)
                # print(type(embedded_face))
                # print(embedded_face.shape)
                # embedded_face = embedded_face.reshape((1,len(embedded_face)))
                # print(type(embedded_face))
                # print(embedded_face.shape)

                self.__known_face_encodings.append(embedded_face)
                self.__known_face_IDs.append(user_ID)

        print("\ttime load data {}".format(time.time() - time_request))
        print("\t{}".format(self.__known_face_IDs))

        if len(self.__known_face_encodings) != len(self.__known_face_IDs) \
           or len(self.__known_face_encodings) == 0 \
           or len(self.__known_face_IDs) == 0:
            return -1

        self.__SaveData()
        return 0

    ###############################################################################################
    # __LoadData                                                                                  #                    
    # Input:                                                                                      #
    #   None            None                        :   None                                      #
    # Output:                                                                                     #
    #   ret             int                         :   -1 No Data Loaded, 0 success              #
    ###############################################################################################
    def __LoadData(self):
        if not os.path.exists(PATH_USER_ID):
            print("There is no user id face to load")
            exit(-1)

        with open (PATH_USER_ID, 'rb') as fp_1:
            self.__known_face_IDs = pickle.load(fp_1)

        if not os.path.exists(PATH_USER_IMG_ENCODED):
            print("There is no user encoding face to load")
            exit(-1)

        with open (PATH_USER_IMG_ENCODED, 'rb') as fp_2:
            self.__known_face_encodings = pickle.load(fp_2)
    
    ###############################################################################################
    # __SaveData                                                                                  #                    
    # Input:                                                                                      #
    #   None            None                        :   None                                      #
    # Output:                                                                                     #
    #   ret             int                         :   -1 No Data Loaded, 0 success              #
    ###############################################################################################
    def __SaveData(self):
        with open(PATH_USER_ID, mode='wb') as fp_1:
            pickle.dump(self.__known_face_IDs, fp_1)
        
        with open(PATH_USER_IMG_ENCODED, 'wb') as fp_2:
            pickle.dump(self.__known_face_encodings, fp_2)
        
    def __image_files_in_folder(self,folder):
        return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]
    
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
            print("There is KNN model to load")
            exit(-1)

        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)
            return knn_clf

    #################################################################################
    # __SaveKNNModel                                                                #                    
    # Input:                                                                        #
    #   knn_clf         :   Model after trained                                     #
    #   model_save_path :   path to save model                                      #
    # Output:                                                                       #
    #   ret             :   -1 no path, 0 success                                   #
    #################################################################################
    def __SaveKNNModel(self, knn_clf,model_save_path):
        if model_save_path is not None:
            with open(model_save_path, 'wb') as f:
                pickle.dump(knn_clf, f)

    ###############################################################################################
    # __TrainKNN                                                                                  #                    
    # Input:                                                                                      #
    #   int             n_neighbors                 :   Bumber of neighbors                       #
    #   str             knn_algorithm               :   algorithm implement KNN                   #
    #   str             knn_weights                 :   weights to calculate diff                 #
    # Output:                                                                                     #
    #   knn_clf         knn_clf                     :   knn classification model                  #
    ###############################################################################################
    def __TrainKNN(self, n_neighbors, knn_algorithm, knn_weights, model_save_path):
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
        # print(closet_distances)
        # print(face_id[-1])
        meet_condition_threshold = [closet_distances[0][0][i] <= THRESHOLD_FACE_REC for i in range(len(closet_distances[0][0]))]
        for i in range(len(meet_condition_threshold)):
            if self.__known_face_IDs[closet_distances[1][0][i]] == face_id[-1] and meet_condition_threshold[i]:
                try:
                    return self.__list_patient[face_id[-1]], closet_distances[0][0][i]
                except:
                    print("There is no face ins database")
                    return "Null", 0
        return "Null", 0
        
    def Test(self):
        print("\tStarting load new image")
        # ret = self.__LoadNewData()
        # ret = self.__LoadData()

        # self.__knn_clf = self.__TrainKNN(NUM_NEIGHBROS, KNN_ALGORITHM, KNN_WEIGHTS, KNN_MODEL_PATH)
        # self.__knn_clf = self.__LoadKNNModel(KNN_MODEL_PATH)

        print("\tStarting test")
        # time_request = time.time()
        # Loop through each person in the training set
        for class_dir in os.listdir(FACE_TEST_PATH):
            print(class_dir)
            if not os.path.isdir(os.path.join(FACE_TEST_PATH, class_dir)):
                continue
        
            # Loop through each training image for the current person and past image path for encoing individualy
            for img in self.__image_files_in_folder(os.path.join(FACE_TEST_PATH, class_dir)):
                path = img.split('/')
                user_ID = class_dir
                img_name = path[-1]
                time_st = time.time()
                loaded_img = cv2.imread( img )
                
                # embedded_face = self.__face_iden(loaded_img)
                # embedded_face = embedded_face.reshape((1,len(embedded_face)))

                # fra = IMAGE_SIZE / max(loaded_img.shape[0], loaded_img.shape[1]) 
                # resized_img = cv2.resize(loaded_img, (int(loaded_img.shape[1] * fra), int(loaded_img.shape[0] * fra)))
                # RGB_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
                # embedded_face = face_recognition.face_encodings(RGB_resized_img, [(0,150,150,0)])[0]
                # embedded_face = np.array(embedded_face).reshape(1,-1)

                # Use the KNN model to find the best matches for the test face
                # closest_distances = knn_clf.kneighbors(embedded_face, n_neighbors=1)
                # print("\t{}".format(closest_distances))
                # print(closest_distances[1][0][0])
                # print(closest_distances[0][0][0])

                face_id = self.GetFaceID(loaded_img)
                
                print("User: {} with time to decode one img {}".format(face_id, time.time() - time_st))
            print()
        print(self.__known_face_IDs)

            # # TEST 1
            # face_locations = face_recognition.face_locations(resized_RGB_img)
            # img_name = img.split('/')
            # # SaveFace(0,ID, img_name[-1],resized_img, face_locations)
            # face_encodings = face_recognition.face_encodings(resized_RGB_img, face_locations)
            # if len(face_encodings) == 0:
            #     print("Cannot detect face in img {}".format(img))
            #     continue

            # # Use the KNN model to find the best matches for the test face
            # closest_distances = knn_clf.kneighbors(face_encodings, n_neighbors=3)
            # indexes = []
            # distances = []
            # for i in range(len(face_locations)):
            #     indexes.append(closest_distances[1][i][0])
            #     distances.append(closest_distances[0][i][0])

            # for user_index, distance in zip(indexes, distances):
            #     print("USer: {}, distance: {}.".format(self.__known_face_IDs[user_index],distance))
            
            
        # print("\tTime Testing {}".format(time.time() - time_request))


if __name__ == '__main__':
    # print('TrtThread: loading the TRT model...')
    print("Test with RGB converter")
    test = FaceIdentify()
    test.Test()