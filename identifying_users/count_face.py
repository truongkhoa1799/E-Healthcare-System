from threading import Timer
from utils.parameters import *

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class CountFace:
    def __init__(self):
        self.__list_faces = []
    
    def CountSecond(self):
        freq = {}
        max_people = 0
        return_face_id = None
        for face_id in self.__list_faces: 
            if (face_id in freq): 
                freq[face_id] += 1
            else: 
                freq[face_id] = 1
            
            if freq[face_id] > max_people:
                max_people = freq[face_id]
                return_face_id = face_id
                
        if max_people >= THRESHOLD_PATIENT_REC:
            glo_va.patient_id = return_face_id
        
        self.__list_faces = []

    def Error(self):
        self.__list_faces = []

    def StartCountingFace(self):
        self.__counter=RepeatTimer(CYCLE_COUNT_FACE_PERIOD, self.CountSecond)
        self.__counter.start()

    def stop(self):
        try:
            self.__counter.cancel()
            self.__counter.join()
        except:
            print("Not yet start")

    def CountFace(self, face_id):
        self.__list_faces.append(face_id)
        
