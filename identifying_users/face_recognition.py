import os
import time
import pickle
import numpy as np

# import face_recognition
import dlib
from utils.parameters import *
from utils.get_occuluded_angle.get_face_pose import Get_Face_Angle
from utils.common_functions import Preprocessing_Img
from utils.common_functions import LogMesssage


# from tensorflow import keras
# import tensorflow as tf

class Face_Recognition:
    def __init__(self):
        if glo_va.SHAPE_PREDICTOR_MODEL == '68':
            LogMesssage("\tLoad predictor 68 points model")
            self.__pose_predictor = dlib.shape_predictor(glo_va.PREDICTOR_68_POINT_MODEL)
        else:
            LogMesssage("\tLoad predictor 5 points model")
            self.__pose_predictor = dlib.shape_predictor(glo_va.PREDICTOR_5_POINT_MODEL)

        self.__face_encoder = dlib.face_recognition_model_v1(glo_va.RESNET_MODEL)

        # Move from DLIB to CenterFace
        # if glo_va.FACE_DETECTOR_MODEL == 'hog':
        #     LogMesssage("\tLoad face detector HOG model")
        #     self.__face_detector = dlib.get_frontal_face_detector()
        # else:
        #     LogMesssage("\tLoad face detector CNN model")
        #     self.__face_detector_cnn = dlib.cnn_face_detection_model_v1(glo_va.CNN_FACE_DETECTOR)

        # Test first image
        test_img = None
        test_img_path = os.path.join(PROJECT_PATH, 'model_engine/test_encoding_img')
        with open (test_img_path, mode='rb') as f1:
            test_img = pickle.load(f1)

        raw_landmarks = self.__raw_face_landmarks(test_img, [(1, 149, 1, 149)])
        test_encoded = [np.array(self.__face_encoder.compute_face_descriptor(test_img, raw_landmark_set, 1)) for raw_landmark_set in raw_landmarks][0]
        time.sleep(0.1)

        LogMesssage("\tDone load dlib model")

    ###############################################################################################
    # _css_to_rect                                                                                #
    # Input:                                                                                      #
    #   list_ndarray    css(left, top, right, bottm)            :   bounding box                  #
    # Output:                                                                                     #
    #   None            dlib.rectangle(bottom, left, top, right):   encoding vector               #
    ###############################################################################################
    def __css_to_rect(self, css):
        return dlib.rectangle(css[3], css[0], css[1], css[2])

    # def __rect_to_css(self, rect):
    #     """
    #     Convert a dlib 'rect' object to a plain tuple in (top, right, bottom, left) order
    #     :param rect: a dlib 'rect' object
    #     :return: a plain tuple representation of the rect in (top, right, bottom, left) order
    #     """
    #     return rect.top(), rect.right(), rect.bottom(), rect.left()

    # def __trim_css_to_bounds(self, css, image_shape):
    #     """
    #     Make sure a tuple in (top, right, bottom, left) order is within the bounds of the image.
    #     :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
    #     :param image_shape: numpy shape of the image array
    #     :return: a trimmed plain tuple representation of the rect in (top, right, bottom, left) order
    #     """
    #     return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)

    # def __raw_face_locations(self, img, number_of_times_to_upsample):
    #     """
    #     Returns an array of bounding boxes of human faces in a image
    #     :param img: An image (as a numpy array)
    #     :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
    #     :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
    #                 deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
    #     :return: A list of dlib 'rect' objects of found face locations
    #     """
    #     if glo_va.FACE_DETECTOR_MODEL == "cnn":
    #         return self.__face_detector_cnn(img, number_of_times_to_upsample)
    #     else:
    #         return self.__face_detector(img, number_of_times_to_upsample)


    def __raw_face_landmarks(self, face_image, face_locations):
        if face_locations is None:
            face_locations = self.__raw_face_locations(face_image)
        else:
            face_locations = [self.__css_to_rect(face_location) for face_location in face_locations]

        return [self.__pose_predictor(face_image, face_location) for face_location in face_locations]

    # def Get_Face_Locations(self, img):
    #     """
    #     Returns an array of bounding boxes of human faces in a image
    #     :param img: An image (as a numpy array)
    #     :param number_of_times_to_upsample: How many times to upsample the image looking for faces. Higher numbers find smaller faces.
    #     :param model: Which face detection model to use. "hog" is less accurate but faster on CPUs. "cnn" is a more accurate
    #                 deep-learning model which is GPU/CUDA accelerated (if available). The default is "hog".
    #     :return: A list of tuples of found face locations in css (top, right, bottom, left) order
    #     """
    #     if glo_va.FACE_DETECTOR_MODEL == "cnn":
    #         return [self.__trim_css_to_bounds(self.__rect_to_css(face.rect), img.shape) for face in self.__raw_face_locations(img, 1)]
    #     else:
    #         return [self.__trim_css_to_bounds(self.__rect_to_css(face), img.shape) for face in self.__raw_face_locations(img, 1)]

    # def Get_Face(self):
    def Get_Location_Face(self, face_locations):
        max_edge = 0
        max_face_location = ()
        try:
            boxes = face_locations[0][:4]

            left = int(boxes[0])
            top = int(boxes[1])
            right = int(boxes[2])
            bottom = int(boxes[3])
            
            # print("top: {}, left: {}, bottom: {}, right: {}".format(top, left, bottom, right))
            if left >= glo_va.MARGIN_FACE_LOCATION and top >= glo_va.MARGIN_FACE_LOCATION \
                and glo_va.img.shape[1] - right >= glo_va.MARGIN_FACE_LOCATION and glo_va.img.shape[0] - bottom >= glo_va.MARGIN_FACE_LOCATION:

                left -= glo_va.MARGIN_FACE_LOCATION
                top -= glo_va.MARGIN_FACE_LOCATION
                right += glo_va.MARGIN_FACE_LOCATION
                bottom += glo_va.MARGIN_FACE_LOCATION

            diff_vertical = bottom - top
            diff_horizontal = right - left
            diff = abs(int((diff_vertical - diff_horizontal) / 2))
            
            if diff_horizontal < diff_vertical:
                top += diff
                bottom -= diff

            else:
                left += diff
                right -= diff
            
            edge = min((right - left), (bottom - top))

            if edge > max_edge:
                max_face_location = (top, bottom, left, right)
                max_edge = edge

        except:
            return -2, None

        if max_edge > glo_va.MAX_EDGE:
            return 0, max_face_location
        else:
            return -1, None

        # if glo_va.img is not None:
        #     # locate faces in the images
        #     if glo_va.STATE == glo_va.STATE_NEW_PATIENT:
        #         fra = glo_va.MAX_LENGTH_IMG_NEW_USER / max(glo_va.img.shape[0], glo_va.img.shape[1]) 
        #     else:
        #         fra = glo_va.MAX_LENGTH_IMG / max(glo_va.img.shape[0], glo_va.img.shape[1])

        #     resized_img = cv2.resize(glo_va.img, (int(glo_va.img.shape[1] * fra), int(glo_va.img.shape[0] * fra)))
        #     GRAY_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
            
        #     # start_detec = time.time()
        #     face_locations = self.Get_Face_Locations(GRAY_resized_img)
        #     # glo_va.list_time_detection.append(time.time() - start_detec)

        #     if len(face_locations) == 0:
        #         return -1

        #     try:
        #         for face_location in face_locations:
        #             top = int(face_location[0] / fra)
        #             bottom = int(face_location[2] / fra)
        #             left = int(face_location[3] / fra)
        #             right = int(face_location[1] / fra)

        #             edge = min((right - left), (bottom - top))
        #             if edge > max_edge:
        #                 glo_va.face_location = (top, bottom, left, right)
        #                 max_edge = edge
        #     except:
        #         return -2

        #     if max_edge > glo_va.MAX_EDGE:
        #         # print("height: {}, width: {}".format(glo_va.face_location[1] - glo_va.face_location[0], glo_va.face_location[3] - glo_va.face_location[2]))
        #         # detected_face = img[top: bottom, left: right]
        #         glo_va.detected_face = glo_va.img[glo_va.face_location[0] : glo_va.face_location[1], glo_va.face_location[2] : glo_va.face_location[3]]
        #         cv2.rectangle(glo_va.img, (left, top), (right, bottom) , (2, 255, 0), 2)
        #         return 0
        #     else:
        #         return -1

        # return -1
    
    def encodingFaceNewPatient(self, detected_face):
        RGB_resized_adjusted_bright_img = Preprocessing_Img(detected_face)

        raw_landmarks = self.__raw_face_landmarks(RGB_resized_adjusted_bright_img, [(0, glo_va.IMAGE_SIZE, glo_va.IMAGE_SIZE,0)])

        embedded_face = [np.array(self.__face_encoder.compute_face_descriptor(RGB_resized_adjusted_bright_img, raw_landmark_set, 1)) for raw_landmark_set in raw_landmarks]
        
        user_pose = Get_Face_Angle(RGB_resized_adjusted_bright_img, raw_landmarks[0])

        return user_pose, embedded_face[0]

    def Encoding_Face(self, detected_face):
        # Pre-processing
        RGB_resized_adjusted_bright_img = Preprocessing_Img(detected_face)

        # locations = (top, right, bottom, left)
        raw_landmarks = self.__raw_face_landmarks(RGB_resized_adjusted_bright_img, [(0, glo_va.IMAGE_SIZE, glo_va.IMAGE_SIZE,0)])

        embedded_face = [np.array(self.__face_encoder.compute_face_descriptor(RGB_resized_adjusted_bright_img, raw_landmark_set, 1)) for raw_landmark_set in raw_landmarks]

        return embedded_face[0]

        # print("face identify: ", time.time() - start_iden)
        # glo_va.list_time_recognition.append(time.time() - start_iden)

        # glo_va.times_measure += 1
        # if glo_va.times_measure == 100:
        #     print()
        #     print('Max time detec: {}'.format(np.max(glo_va.list_time_detection)))
        #     print('Min time detec: {}'.format(np.min(glo_va.list_time_detection)))
        #     print('Mean time detec: {}'.format(np.mean(glo_va.list_time_detection)))
        #     print('Std time detec: {}'.format(np.std(glo_va.list_time_detection)))
        #     print('Max time iden: {}'.format(np.max(glo_va.list_time_recognition)))
        #     print('Min time iden: {}'.format(np.min(glo_va.list_time_recognition)))
        #     print('Mean time iden: {}'.format(np.mean(glo_va.list_time_recognition)))
        #     print('Std time iden: {}'.format(np.std(glo_va.list_time_recognition)))
        #     print()

        # glo_va.embedded_face = np.array(glo_va.embedded_face).reshape(1,-1)