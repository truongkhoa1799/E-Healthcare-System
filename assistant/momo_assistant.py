from logging import error
import sys
from threading import Timer, Thread, Lock

sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')

import os
# from gtts import gTTS
# import speech_recognition

from utils.parameters import *
from utils.assis_parameters import *

from assistant.states_assistant import *
from utils.common_functions import LogMesssage
from assistant.classify_department import ClassifyDepartment

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class MomoAssistant:
    def __init__(self):
        # self.__momo_ear = speech_recognition.Recognizer()
        # self.__momo_ear.energy_threshold = 400
        self.__dt_clf = ClassifyDepartment()

        # glo_va.thread_assis = Thread(target=MomoCore, args=())
        # glo_va.thread_assis.daemon = True
        # glo_va.thread_assis.start()
    
    def Listen(self):
        with speech_recognition.Microphone() as mic:
            self.__momo_ear.adjust_for_ambient_noise(mic)
            audio = self.__momo_ear.listen(mic)
            if glo_va.STATE != glo_va.STATE_VIEW_DEPARTMENTS:
                return -1

        try:
            script = self.__momo_ear.recognize_google(audio, language='vi-VN')
            print(script)
            return script
        except:
            return -1
    
    def Say(self, text):
        # try:
        #     tts = gTTS(text =text,lang='vi')
        #     tts.save(glo_va.VOICE_PATH_FILE)
        #     # Change here to play music
        #     os.system("afplay {}".format(glo_va.VOICE_PATH_FILE))
        # except Exception as e:
        #     LogMesssage('\tHas error at module Say in momo_assistant: {error}'.format(error=e))
        print(text)

    def __Submit_Examination(self, dep_ID):
        for i in glo_va.list_examination_room:
            if i['dep_ID'] == dep_ID:
                dep_name = i['dep_name']
                building_code = i['building_code']
                room_code = i['room_code']

                data = {}
                data['dep_name'] = dep_name
                data['building_code'] = building_code
                data['room_code'] = room_code

                # Acquire lock first predicted by MOMO
                if glo_va.lock_update_exam_room.locked() == False:
                    glo_va.lock_update_exam_room.acquire()

                    # send request to update selected exam room
                    request = {'type': glo_va.REQUEST_UPDATE_SELECTED_EXAM_ROOM, 'data': data}
                    glo_va.gui.queue_request_states_thread.put(request)
                    
                    glo_va.lock_update_exam_room.release()
                    
                    msg = res_msg[2].format(dep_name=dep_name ,room='{}-{}'.format(building_code, room_code))
                    return msg
                else:
                    return -2
        
        return -1

    def Analyze_Sympton(self, ret_data):
        try:
            list_problems = ret_data['list_problem']
            list_part_of_body = ret_data['list_part_of_body']

            # print("Momo: {}".format(res_msg[5]))
            self.Say(res_msg[5])

            # Normalize part_of_body and problem
            normalized_list_problems = []
            normalized_list_part_bodies = []
            # print(list_problems)
            # print(list_part_of_body)
            for i in list_problems:
                try:
                    normalized_list_problems.append(dict_synonym_problem[i])
                    # print(dict_synonym_problem[i])
                except:
                    normalized_list_problems.append(i)

            for i in list_part_of_body:
                try:
                    normalized_list_part_bodies.append(dict_synonym_part_body[i])
                    # print(dict_synonym_part_body[i])
                except:
                    normalized_list_part_bodies.append(i)

            # print(normalized_list_problems)
            # print(normalized_list_part_bodies)

            # INT
            predict_department_id = self.__dt_clf.Get_Department(normalized_list_problems, normalized_list_part_bodies)

            # map the predicted dep id with curent active dep
            if glo_va.hospital_ID in list(glo_va.map_department_table[predict_department_id].keys()):
                mapped_dep_ID = glo_va.map_department_table[predict_department_id][glo_va.hospital_ID]
                msg = self.__Submit_Examination(mapped_dep_ID)
                print(msg)
                
                if msg == -1:
                    return res_msg[14].format(dep_name=department[predict_department_id])
                # when patient click the submit first, momo say nothing
                elif msg == -2:
                    return -1
                else:
                    return msg
            else:
                return res_msg[13].format(dep_name=department[predict_department_id])

        except Exception as e:
            LogMesssage('Has error at Analyze_Sympton in momo_assistant: {e}'.format(e=e))
            return res_msg[15]

    def Analyze_Department(self, deparment_name):
        try:
            # print("Momo: {}".format(res_msg[5]))
            self.Say(res_msg[5])

            for predict_department_id in list_department:
                if deparment_name in list_department[predict_department_id]:
                    # map the predicted dep id with curent active dep
                    if glo_va.hospital_ID in list(glo_va.map_department_table[predict_department_id].keys()):
                        mapped_dep_ID = glo_va.map_department_table[predict_department_id][glo_va.hospital_ID]
                        msg = self.__Submit_Examination(mapped_dep_ID)

                        if msg == -1:
                            return res_msg[14].format(dep_name=department[predict_department_id])
                        # when patient click the submit first, momo say nothing
                        elif msg == -2:
                            return -1
                        else:
                            return msg
                    else:
                        return res_msg[13].format(dep_name=department[predict_department_id])
            
            # ERROR: HIEỆN TẠI department VÀ list_department CÙNG CÁC PARA TRONG ASSIS_PARA KO THỂ CẬP NHẬP
            # CẦN CẬP NHẬP CHUNG
            LogMesssage('Cannot find department name: {dep_name}'.format(dep_name = deparment_name))
            return res_msg[15]

        except Exception as e:
            LogMesssage('Has error at Analyze_Department in momo_assistant: {e}'.format(e=e))
            return res_msg[15]

# glo_va.lock_update_exam_room = Lock()
# glo_va.momo_assis = MomoAssistant()
# glo_va.STATE = glo_va.STATE_VIEW_DEPARTMENTS
# MomoCore()