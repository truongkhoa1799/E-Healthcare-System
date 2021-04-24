from logging import error
import sys, time, threading
from threading import Timer

sys.path.append('/Users/khoa1799/GitHub/E-Healthcare-System')

import os, time
from threading import Lock
import subprocess
from gtts import gTTS

from utils.speech_recognition.speech_recognition import Recognizer, Microphone
# from speech_recognition import Recognizer, Microphone

from utils.parameters import *

from assistant.momo_core import MomoCore
from assistant.states_assistant import *
from utils.common_functions import LogMesssage
from assistant.classify_department import ClassifyDepartment

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class MomoAssistant:
    def __init__(self):
        self.__momo_ear = Recognizer()
        self.__momo_mounth = None
        self.__dt_clf = ClassifyDepartment()
    
    def Listen(self):
        # terminate voice of momo
        LogMesssage('[Momo_Listen]: Momo is listening')
        with Microphone() as mic:
            self.__momo_ear.adjust_for_ambient_noise(mic)
            audio = self.__momo_ear.listen(mic, timeout=5)
            if audio == -1:
                return -1
        try:
            script = self.__momo_ear.recognize_google(audio, language='vi-VN')
            return script
        except Exception as error:
            print(error)
            return -1
    
    def stopCurrentConversation(self):
        try:
            self.__momo_mounth.terminate()
        except Exception as e:
            pass

    def Say(self, text, opt=0):
        # say without blocking
        if opt == 0:
            try:
                tts = gTTS(text = text,lang='vi')
                tts.save(glo_va.VOICE_PATH_FILE)
                self.__momo_mounth = subprocess.Popen(["afplay", glo_va.VOICE_PATH_FILE])
            except Exception as e:
                LogMesssage('Has error at module [Say] in [momo_assistant]: {}'.format(e))
        else:
            try:
                tts = gTTS(text =text,lang='vi')
                tts.save(glo_va.VOICE_PATH_FILE)
                # Change here to play music
                os.system("afplay {}".format(glo_va.VOICE_PATH_FILE))
            except Exception as e:
                LogMesssage('\tHas error at module Say in momo_assistant: {error}'.format(error=e))

    def __Submit_Examination(self, dep_ID):
        for i in list_exam_rooms.list_examination_room:
            if i['dep_ID'] == dep_ID:
                dep_name = i['dep_name']
                
                # send request to update selected exam room
                request = {'type': glo_va.REQUEST_UPDATE_SELECTED_EXAM_ROOM, 'data': dep_name}
                glo_va.gui.queue_request_states_thread.put(request)
                    
                msg = assis_para.res_msg[2].format(dep_name=dep_name)
                return msg
        
        return -1

    def Analyze_Sympton(self, ret_data):
        try:
            list_problems = ret_data['list_problem']
            list_part_of_body = ret_data['list_part_of_body']

            # Normalize part_of_body and problem
            normalized_list_problems = []
            normalized_list_part_bodies = []

            for i in list_problems:
                try:
                    normalized_list_problems.append(assis_para.dict_synonym_problem[i])
                    # print(dict_synonym_problem[i])
                except:
                    normalized_list_problems.append(i)

            for i in list_part_of_body:
                try:
                    normalized_list_part_bodies.append(assis_para.dict_synonym_part_body[i])
                    # print(dict_synonym_part_body[i])
                except:
                    normalized_list_part_bodies.append(i)

            # INT
            predict_department_id = self.__dt_clf.Get_Department(normalized_list_problems, normalized_list_part_bodies)

            # map the predicted dep id with curent active dep
            if list_exam_rooms.hospital_ID in list(glo_va.map_department_table[predict_department_id].keys()):
                mapped_dep_ID = glo_va.map_department_table[predict_department_id][list_exam_rooms.hospital_ID]
                msg = self.__Submit_Examination(mapped_dep_ID)
                print(msg)
                
                if msg == -1:
                    return assis_para.res_msg[14].format(dep_name=assis_para.department[predict_department_id])

                else:
                    return msg
            else:
                return assis_para.res_msg[13].format(dep_name=assis_para.department[predict_department_id])

        except Exception as e:
            LogMesssage('Has error at Analyze_Sympton in momo_assistant: {e}'.format(e=e))
            return assis_para.res_msg[15]

    def Analyze_Department(self, deparment_name):
        try:
            deparment_name = deparment_name.strip().lower()
            for predict_department_id in assis_para.list_department:
                if deparment_name in assis_para.list_department[predict_department_id]:
                    # map the predicted dep id with curent active dep
                    if list_exam_rooms.hospital_ID in list(glo_va.map_department_table[predict_department_id].keys()):
                        mapped_dep_ID = glo_va.map_department_table[predict_department_id][list_exam_rooms.hospital_ID]
                        msg = self.__Submit_Examination(mapped_dep_ID)

                        if msg == -1:
                            return assis_para.res_msg[14].format(dep_name=assis_para.department[predict_department_id])

                        else:
                            return msg
                    else:
                        return assis_para.res_msg[13].format(dep_name=assis_para.department[predict_department_id])
            
            # ERROR: HIEỆN TẠI department VÀ list_department CÙNG CÁC PARA TRONG ASSIS_PARA KO THỂ CẬP NHẬP
            # CẦN CẬP NHẬP CHUNG
            LogMesssage('Cannot find department name: {dep_name}'.format(dep_name = deparment_name))
            return assis_para.res_msg[15]

        except Exception as e:
            LogMesssage('Has error at Analyze_Department in momo_assistant: {e}'.format(e=e))
            return assis_para.res_msg[15]

    
    def measureDepartment(self, symptons):
        if glo_va.assis_state == glo_va.ASSIS_FIRST_STATE:
            State_1(symptons)
        elif glo_va.assis_state == glo_va.ASSIS_CHOOSE_DEP_STATE:
            State_2(symptons)
        elif glo_va.assis_state == glo_va.ASSIS_DISPLAY_SYMPTON_STATE:
            State_3(symptons)
        elif glo_va.assis_state == glo_va.ASSIS_CONFIRM_STATE:
            Confirm_Message(symptons)

# glo_va.momo_assis = MomoAssistant()
# glo_va.STATE = glo_va.STATE_VIEW_DEPARTMENTS

# glo_va.momo_thread_say = subprocess.call([MomoCore, ])
# glo_va.enable_momo_run = True
# momo = MomoAssistant()
# print(momo.Listen())

# momo.Say('Hello')
# time.sleep(2)
# momo.Say('Hello Khoa')

# time.sleep(5)
# momo.Say('Hello Khoa')

# time.sleep(5)