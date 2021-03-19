import os
import cv2
import time
import numpy as np
import PySimpleGUI as sg
from PIL import Image, ImageTk
from threading import Lock, Timer

from utils.parameters import *

def SaveFace(opt,dir_name,img_name, img,locations):
    count = 0
    if opt==0:
        os.chdir(SAVING_IMG_PATH) 
        for (top, right, bottom, left) in locations:
            img_name_1 = dir_name+'-'+str(count)+'-'+img_name
            cv2.imwrite(img_name_1, img[top:bottom,left:right]) 
            count += 1

def AdjustBright(img):
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) #convert it to hsv
        v = hsv_img[:, :, 2]
        mean_v = np.mean(v)
        diff = glo_va.BASE_BRIGHTNESS - mean_v
                    
        if diff < 0:
            v = np.where(v < abs(diff), v, v + diff)
        else:
            v = np.where( v + diff > 255, v, v + diff)

        hsv_img[:, :, 2] = v
        ret_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
        # return RGB image
        return ret_img

def Compose_Embedded_Face(encoded_img):
    ret_string = ""
    for i in encoded_img:
        precision_i = '%.20f'%np.float64(i)
        ret_string += str(precision_i) + '/'
    
    return ret_string
        
def Preprocessing_Img(img):
    resized_img = cv2.resize(img, (glo_va.IMAGE_SIZE,glo_va.IMAGE_SIZE))
    RGB_resized_adjusted_bright_img = AdjustBright(resized_img)
    return RGB_resized_adjusted_bright_img

def ConvertToDisplay(image):
    display_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # to RGB
    display_image = Image.fromarray(display_image)  # to PIL format
    display_image = ImageTk.PhotoImage(display_image)  # to ImageTk format
    return display_image

def Capture_New_Patient():
    # Get embedded face of new user
    glo_va.embedded_face_new_user = glo_va.embedded_face
    # Resize image and display for user reviewing
    review_image = cv2.resize(glo_va.detected_face, (300,300))
    display_review_image = ConvertToDisplay(review_image)
    glo_va.window_GUI['review_photo'].update(data=display_review_image)