from threading import Timer
import numpy as np
from utils.parameters import *

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class CountFace:
    def __init__(self):
        # self.__list_faces = []
        self.__list_faces = ""
        self.__num_imgs = 0

    def CountSecond(self):
        if self.__num_imgs > THRESHOLD_PATIENT_REC:
            glo_va.list_encoded_img = self.__list_faces
            glo_va.server.Validate_User()

        self.__list_faces = ""
        self.__num_imgs = 0

    def StartCountingFace(self):
        self.__counter=RepeatTimer(CYCLE_COUNT_FACE_PERIOD, self.CountSecond)
        self.__counter.start()

    def stop(self):
        try:
            self.__counter.cancel()
            self.__counter.join()
        except:
            print("Not yet start")
    
    def __Compose_String(self, encoded_img):
        ret_string = ""
        for i in encoded_img:
            precision_i = '%.20f'%np.float64(i)
            ret_string += str(precision_i) + '/'
        
        return ret_string

    # def CountFace(self, face_id):
    #     self.__list_faces.append(face_id)
    
    def CountFace(self):
        self.__num_imgs += 1
        encoded_img_string = self.__Compose_String(glo_va.embedded_face)
        self.__list_faces += encoded_img_string + ' '
