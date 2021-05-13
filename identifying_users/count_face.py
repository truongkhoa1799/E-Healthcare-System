from threading import Timer
import numpy as np
from utils.parameters import *
from utils.common_functions import Compose_Embedded_Face
from utils.common_functions import LogMesssage

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class CountFace:
    def __init__(self):
        self.__list_faces = ""
        self.__num_imgs = 0
        self.__counter=RepeatTimer(glo_va.CYCLE_COUNT_FACE_PERIOD, self.Count_Second)
        self.__counter.daemon = True
        self.__counter.start()

    def Count_Second(self):
        try:
            # print("State: {}, is_sending_message: {}, has_response_server: {}, num_images: {}".format(glo_va.STATE, glo_va.is_sending_message, glo_va.has_response_server, self.__num_imgs))
            if glo_va.STATE == 1 and self.__num_imgs > glo_va.NUMBER_DETECTED_FACE_TRANSMITED and glo_va.is_sending_message == False:
                glo_va.timer.Start_Timer(glo_va.OPT_TIMER_VALIDATE)
                glo_va.is_sending_message = True
                glo_va.server.Validate_User(self.__list_faces)

            self.__list_faces = ""
            self.__num_imgs = 0
        
        except Exception as e:
            LogMesssage('[Count_Second]: Has error in module count_face: {e}'.format(e=e))

    def Stop(self):
        self.__counter.cancel()
        self.__counter.join()
    
    def Count_Face(self, embedded_face):
        encoded_embedded_face = Compose_Embedded_Face(embedded_face)
        self.__list_faces += encoded_embedded_face + ' '
        self.__num_imgs += 1
    
    def Clear(self):
        self.__num_imgs = 0
        self.__list_faces = ""
