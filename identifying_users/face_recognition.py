import os
import cv2
import time
import pickle
import numpy as np

# import face_recognition
import dlib
from utils.parameters import *
from utils.get_occuluded_angle.head_pose_from_image import Get_Face_Angle
from utils.common_functions import Preprocessing_Img

CNN_FACE_DETECTOR = '/home/thesis/Documents/thesis/E-Healthcare-System/model_engine/mmod_human_face_detector.dat'

class Face_Recognition:
    def __init__(self):
        if glo_va.SHAPE_PREDICTOR_MODEL == '68':
            print("\tLoad predictor 68 points model")
            self.__pose_predictor = dlib.shape_predictor(glo_va.PREDICTOR_68_POINT_MODEL)
        else:
            print("\tLoad predictor 5 points model")
            self.__pose_predictor = dlib.shape_predictor(glo_va.PREDICTOR_5_POINT_MODEL)

        self.__face_encoder = dlib.face_recognition_model_v1(glo_va.RESNET_MODEL)

        if glo_va.FACE_DETECTOR_MODEL == 'hog':
            print("\tLoad face detector HOG model")
            self.__face_detector = dlib.get_frontal_face_detector()
        else:
            print("\tLoad face detector CNN model")
            self.__face_detector_cnn = dlib.cnn_face_detection_model_v1(CNN_FACE_DETECTOR)

        test_img = None
        test_img_path = os.path.join(PROJECT_PATH, 'model_engine/test_encoding_img')
        with open (test_img_path, mode='rb') as f1:
            test_img = pickle.load(f1)

        test_encoded = self.__face_encodings(test_img, [(1, 149, 1, 149)])
        time.sleep(1)
        print("\tDone load dlib model")
    
    def __face_encodings(self, face_image, known_face_locations):
        # Get landmarks
        raw_landmarks = self.__raw_face_landmarks(face_image, known_face_locations)

        # If STATE = 6 (get face new user) check angle of face
        if glo_va.STATE == glo_va.STATE_NEW_PATIENT:
            # print('Hello')
            glo_va.user_pose = Get_Face_Angle(face_image, raw_landmarks[0])
            # print("{} {}".format(glo_va.STATE, glo_va.user_pose))

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
        if glo_va.FACE_DETECTOR_MODEL == "cnn":
            return self.__face_detector_cnn(img, number_of_times_to_upsample)
        else:
            return self.__face_detector(img, number_of_times_to_upsample)


    def __raw_face_landmarks(self, face_image, face_locations):
        if face_locations is None:
            face_locations = self.__raw_face_locations(face_image)
        else:
            face_locations = [self.__css_to_rect(face_location) for face_location in face_locations]

        return [self.__pose_predictor(face_image, face_location) for face_location in face_locations]

    def __Get_Face_Locations(self, img):
        """
        Returns an array of bounding boxes of human faces in a image
        :param img: An image (as a numpy array)
        :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
        :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
                    deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
        :return: A list of tuples of found face locations in css (top, right, bottom, left) order
        """
        if glo_va.FACE_DETECTOR_MODEL == "cnn":
            return [self.__trim_css_to_bounds(self.__rect_to_css(face.rect), img.shape) for face in self.__raw_face_locations(img, 1)]
        else:
            return [self.__trim_css_to_bounds(self.__rect_to_css(face), img.shape) for face in self.__raw_face_locations(img, 1)]

    def Get_Face(self):
        face_area = 0
        max_edge = 0

        if glo_va.img is not None:
            # print("size display image: {}".format(glo_va.img.shape))
            # locate faces in the images
            fra = glo_va.MAX_LENGTH_IMG / max(glo_va.img.shape[0], glo_va.img.shape[1]) 
            resized_img = cv2.resize(glo_va.img, (int(glo_va.img.shape[1] * fra), int(glo_va.img.shape[0] * fra)))
            GRAY_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
            # print("size resized image: {}".format(GRAY_resized_img.shape))
            
            face_locations = self.__Get_Face_Locations(GRAY_resized_img)
            # face_locations = self.__Get_Face_Locations(GRAY_resized_img)

            if len(face_locations) == 0:
                return -1

            try:
                for face_location in face_locations:
                    top = int(face_location[0] / fra)
                    bottom = int(face_location[2] / fra)
                    left = int(face_location[3] / fra)
                    right = int(face_location[1] / fra)

                    edge = min((right - left), (bottom - top))
                    if edge > max_edge:
                        glo_va.face_location = (top, bottom, left, right)
                        max_edge = edge
            except:
                return -2

            if max_edge > glo_va.MAX_EDGE:
                # print("height: {}, width: {}".format(glo_va.face_location[1] - glo_va.face_location[0], glo_va.face_location[3] - glo_va.face_location[2]))

                # detected_face = img[top: bottom, left: right]
                glo_va.detected_face = glo_va.img[glo_va.face_location[0] : glo_va.face_location[1], glo_va.face_location[2] : glo_va.face_location[3]]
                cv2.rectangle(glo_va.img, (left, top), (right, bottom) , (2, 255, 0), 2)
                return 0
            else:
                return -1

        return -1

    def Encoding_Face(self):
        # Pre-processing
        RGB_resized_adjusted_bright_img = Preprocessing_Img(glo_va.detected_face)
        # print("size RGB_resized_adjusted_bright_img image: {}".format(RGB_resized_adjusted_bright_img.shape))

        # locations = (top, right, bottom, left)
        glo_va.embedded_face = self.__face_encodings(RGB_resized_adjusted_bright_img, [(0, glo_va.IMAGE_SIZE, glo_va.IMAGE_SIZE,0)])[0]
        # glo_va.embedded_face = np.array(glo_va.embedded_face).reshape(1,-1)