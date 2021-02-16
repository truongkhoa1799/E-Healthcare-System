import time
import pickle
import numpy as np

# import face_recognition
import dlib
from utils.parameters import *
from utils.common_functions import Preprocessing_Img

class Face_Recognition:
    def __init__(self):
        self.__pose_predictor_5_point = dlib.shape_predictor(PREDICTOR_5_POINT_MODEL)
        self.__face_encoder = dlib.face_recognition_model_v1(RESNET_MODEL)
        self.__face_detector = dlib.get_frontal_face_detector()

        test_img = None
        with open ('/home/thesis/Documents/E-Healthcare-System/model_engine/test_encoding_img', mode='rb') as f1:
            test_img = pickle.load(f1)

        test_encoded = self.__face_encodings(test_img, [(1, 149, 1, 149)])
        time.sleep(1)
        print("\tDone load dlib model")
    
    def __face_encodings(self, face_image, known_face_locations):
        raw_landmarks = self.__raw_face_landmarks(face_image, known_face_locations)
        return [np.array(self.__face_encoder.compute_face_descriptor(face_image, raw_landmark_set, 1)) for raw_landmark_set in raw_landmarks]

    ###############################################################################################
    # _css_to_rect                                                                                #
    # Input:                                                                                      #
    #   list_ndarray    css(left, top, right, bottm)            :   bounding box                  #
    # Output:                                                                                     #
    #   None            dlib.rectangle(bottom, left, top, right):   encoding vector               #
    ###############################################################################################
    def __css_to_rect(self, css):
        return dlib.rectangle(css[3], css[0], css[1], css[2])

    def __rect_to_css(self, rect):
        """
        Convert a dlib 'rect' object to a plain tuple in (top, right, bottom, left) order
        :param rect: a dlib 'rect' object
        :return: a plain tuple representation of the rect in (top, right, bottom, left) order
        """
        return rect.top(), rect.right(), rect.bottom(), rect.left()

    def __trim_css_to_bounds(self, css, image_shape):
        """
        Make sure a tuple in (top, right, bottom, left) order is within the bounds of the image.
        :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
        :param image_shape: numpy shape of the image array
        :return: a trimmed plain tuple representation of the rect in (top, right, bottom, left) order
        """
        return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)

    def __raw_face_locations(self, img, number_of_times_to_upsample):
        """
        Returns an array of bounding boxes of human faces in a image
        :param img: An image (as a numpy array)
        :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
        :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
                    deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
        :return: A list of dlib 'rect' objects of found face locations
        """
        return self.__face_detector(img, number_of_times_to_upsample)


    def __raw_face_landmarks(self, face_image, face_locations):
        if face_locations is None:
            face_locations = self.__raw_face_locations(face_image)
        else:
            face_locations = [self.__css_to_rect(face_location) for face_location in face_locations]

        return [self.__pose_predictor_5_point(face_image, face_location) for face_location in face_locations]

    def Get_Face_Locations(self, img):
        """
        Returns an array of bounding boxes of human faces in a image
        :param img: An image (as a numpy array)
        :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
        :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
                    deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
        :return: A list of tuples of found face locations in css (top, right, bottom, left) order
        """
        return [self.__trim_css_to_bounds(self.__rect_to_css(face), img.shape) for face in self.__raw_face_locations(img, 1)]

    def Encoding_Face(self):
        # Pre-processing
        RGB_resized_adjusted_bright_img = Preprocessing_Img(glo_va.img_located)

        glo_va.embedded_face = self.__face_encodings(RGB_resized_adjusted_bright_img, [(0, IMAGE_SIZE, IMAGE_SIZE,0)])[0]
        # glo_va.embedded_face = np.array(glo_va.embedded_face).reshape(1,-1)