from threading import Timer
import numpy as np
from utils.parameters import *
from utils.common_functions import Compose_Embedded_Face

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class CountFace:
    def __init__(self):
        self.__list_faces = ""
        self.__num_imgs = 0
        self.__counter=RepeatTimer(CYCLE_COUNT_FACE_PERIOD, self.Count_Second)
        self.__counter.start()

    def Count_Second(self):
        if self.__num_imgs > NUMBER_DETECTED_FACE_TRANSMITED and glo_va.STATE == 1 and glo_va.is_sending_message == False:
            glo_va.list_embedded_face = self.__list_faces
            glo_va.timer.Start_Timer(OPT_TIMER_VALIDATE)
            glo_va.server.Validate_User()
            glo_va.is_sending_message = True

        self.__list_faces = ""
        self.__num_imgs = 0

    def Stop(self):
        self.__counter.cancel()
        self.__counter.join()
    
    def Count_Face(self):
        encoded_img_string = Compose_Embedded_Face(glo_va.embedded_face)
        self.__list_faces += encoded_img_string + ' '
        self.__num_imgs += 1
    
    def Clear(self):
        self.__num_imgs = 0
        self.__list_faces = ""
