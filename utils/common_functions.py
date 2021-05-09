import os
import cv2
import time
import numpy as np
from threading import Lock, Timer
from PyQt5.QtGui import QImage, QPixmap

from utils.parameters import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def LogMesssage(msg, opt = 1):
    if opt == 0:
        # Header
        print(bcolors.HEADER + "[{time}]: {msg}".format(time=time.strftime("%H:%M:%S",time.localtime()), msg=msg))
    elif opt == 1:
        # message
        print(bcolors.OKCYAN + "[{time}]: {msg}".format(time=time.strftime("%H:%M:%S",time.localtime()), msg=msg))
    else:
        print(bcolors.FAIL + "[{time}]: {msg}".format(time=time.strftime("%H:%M:%S",time.localtime()), msg=msg))


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
    # RGB_resized_adjusted_bright_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
    return RGB_resized_adjusted_bright_img

############################################################################
# GUI MODULE                                                            #
############################################################################
def Convert_To_Display(img):
    # Get ndarray and return QImage
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    image = QImage(img, img.shape[1], img.shape[0], img.shape[1]*3, QImage.Format_RGB888)
    qp_image = QPixmap(image)

    return qp_image