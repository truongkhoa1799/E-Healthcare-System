import time
from common_functions import *
from threading import Thread, Timer, Lock

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class CountFace:
    def __init__(self):
        print("Starting CountFace")
        self.__list_faces = []
        self.StartCountingFace()
    
    def CountSecond(self):
        freq = {}
        percent = {}
        max_percent = 0
        return_face_id = None
        for face_id in self.__list_faces: 
            if (face_id in freq): 
                freq[face_id] += 1
            else: 
                freq[face_id] = 1
            
            percent[face_id] = freq[face_id]/len(self.__list_faces)
            if percent[face_id] > max_percent:
                max_percent = percent[face_id]
                return_face_id = face_id
                
        print("Total faces: {}".format(len(self.__list_faces)))
        print(percent)
        if max_fre >= 25:
            print("User {} with percent {}".format(return_face_id,max_percent))
            # current_patient.UpdatePatientName(max_face_id)
        else:
            print("There is no user")
            # current_patient.UpdatePatientName("Unknown")
        
        self.__list_faces = []


    def StartCountingFace(self):
        self.__counter=RepeatTimer(CYCLE_COUNT_FACE_PERIOD, self.CountSecond)
        self.__counter.start()

    def stop(self):
        self.__counter.cancel()
        self.__counter.join()
    
    def CountFace(self, face_id):
        self.__list_faces.append(face_id)
        
