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
        diff = BASE_BRIGHTNESS - mean_v
                    
        if diff < 0:
            v = np.where(v < abs(diff), v, v + diff)
        else:
            v = np.where( v + diff > 255, v, v + diff)

        hsv_img[:, :, 2] = v
        ret_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
        # return BRG image
        return ret_img
        
def Preprocessing_Img(img):
    resized_img = cv2.resize(img, (IMAGE_SIZE,IMAGE_SIZE))
    resized_adjusted_bright_img = AdjustBright(resized_img)
    RGB_resized_adjusted_bright_img = cv2.cvtColor(resized_adjusted_bright_img, cv2.COLOR_BGR2RGB)
    return RGB_resized_adjusted_bright_img