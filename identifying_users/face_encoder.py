import time
import pickle
import numpy as np

# import face_recognition
import dlib
from utils.parameters import *
from utils.common_functions import Preprocessing_Img

class Face_Encoder:
    def __init__(self):
        self.__pose_predictor_5_point = dlib.shape_predictor(PREDICTOR_5_POINT_MODEL)
        self.__face_encoder = dlib.face_recognition_model_v1(RESNET_MODEL)
        
        test_img = None
        with open ('/home/thesis/Documents/E-Healthcare-System/model_engine/test_encoding_img', mode='rb') as f1:
            test_img = pickle.load(f1)

        test_encoded = self.__face_encodings(test_img, [(1, 149, 1, 149)])
        time.sleep(1)
        print("\tDone load dlib model")
    
    ###############################################################################################
    # face_encodings                                                                              #
    # Input:                                                                                      #
    #   list_ndarray    face_image :   image to encode                                            #
    #   list_str        known_face_locations       :   bounding box for face                      #
    # Output:                                                                                     #
    #   None            128-vector                        :   encoding vector                     #
    ###############################################################################################
    def __face_encodings(self, face_image, known_face_locations):
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

    def Encoding_Face(self):
        # Pre-processing
        RGB_resized_adjusted_bright_img = Preprocessing_Img(glo_va.img_located)

        glo_va.embedded_face = self.__face_encodings(RGB_resized_adjusted_bright_img, [(0, IMAGE_SIZE, IMAGE_SIZE,0)])[0]
        # glo_va.embedded_face = np.array(glo_va.embedded_face).reshape(1,-1)