from threading import Timer
import numpy as np
from utils.parameters import *

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class CountFace:
    def __init__(self):
        self.__list_faces = ""
        self.__num_imgs = 0

    def Count_Second(self):
        # print("Hello")
        if self.__num_imgs > NUMBER_DETECTED_FACE_TRANSMITED and glo_va.STATE == 1 and glo_va.is_sending_message == False:
            # print("\tHello")
            glo_va.is_sending_message = True
            glo_va.list_embedded_face = self.__list_faces
            glo_va.server.Validate_User()

        self.__list_faces = ""
        self.__num_imgs = 0

    def Start_Counting_Face(self):
        self.__counter=RepeatTimer(CYCLE_COUNT_FACE_PERIOD, self.Count_Second)
        self.__counter.start()

    def Stop(self):
        try:
            self.__counter.cancel()
            self.__counter.join()
        except:
            print("Not yet start")
            print()
    
    def __Compose_String(self, encoded_img):
        ret_string = ""
        for i in encoded_img:
            precision_i = '%.20f'%np.float64(i)
            ret_string += str(precision_i) + '/'
        
        return ret_string
    
    def Count_Face(self):
        encoded_img_string = self.__Compose_String(glo_va.embedded_face)
        self.__list_faces += encoded_img_string + ' '
        self.__num_imgs += 1
