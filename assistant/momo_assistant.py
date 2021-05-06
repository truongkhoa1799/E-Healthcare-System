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

from utils.common_functions import LogMesssage
from assistant.classify_department import ClassifyDepartment

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class MomoAssistant:
    momo_ear = Recognizer()
    momo_mounth = None
    dt_clf = ClassifyDepartment()
    
    @staticmethod
    def momoListen():
        # terminate voice of momo
        LogMesssage('[momo_assistant_momoListen]: Momo is listening')
        try:
            with Microphone() as mic:
                MomoAssistant.momo_ear.adjust_for_ambient_noise(mic)
                audio = MomoAssistant.momo_ear.listen(mic, timeout=4)
                if audio == -1:
                    return -1

            script = MomoAssistant.momo_ear.recognize_google(audio, language='vi-VN')
            return script
        except Exception as e:
            LogMesssage('Has error in [momo_assistant_momoListen]: {}'.format(e))
            return -1
    
    @staticmethod
    def stopCurrentConversation():
        # try:
        #     MomoAssistant.momo_mounth.terminate()
        # except Exception as e:
        #     pass

        print('Stop conversation')

    @staticmethod
    def momoSay(text, opt=0):
        # say without blocking
        # if opt == 0:
        #     try:
        #         tts = gTTS(text = text,lang='vi')
        #         tts.save(glo_va.VOICE_PATH_FILE)
        #         MomoAssistant.momo_mounth = subprocess.Popen(["afplay", glo_va.VOICE_PATH_FILE])
        #     except Exception as e:
        #         LogMesssage('Has error in [momo_assistant_momoSay]: {}'.format(e))
        # else:
        #     try:
        #         # send request to update conversation
        #         data = {}
        #         data['opt'] = 1
        #         data['text'] = text
        #         request = {'type': glo_va.REQUEST_UPDATE_CONVERSATION_MOMO_GUI, 'data': data}
        #         glo_va.momo_gui.queue_request_states_thread.put(request)

        #         tts = gTTS(text =text,lang='vi')
        #         tts.save(glo_va.VOICE_PATH_FILE)
        #         # Change here to play music
        #         os.system("afplay {}".format(glo_va.VOICE_PATH_FILE))
        #     except Exception as e:
        #         LogMesssage('\tHas error in [momo_assistant_momoSay]: {error}'.format(error=e))

        print(text)

    @staticmethod
    def Submit_Examination(dep_ID):
        for i in init_parameters.list_examination_room:
            if i['dep_ID'] == dep_ID:
                dep_name = i['dep_name']
                
                # # send request to update selected exam room
                # request = {'type': glo_va.REQUEST_UPDATE_SELECTED_EXAM_ROOM, 'data': dep_name}
                # glo_va.gui.queue_request_states_thread.put(request)
                # send request to update selected exam room
                request = {'type': glo_va.REQUEST_UPDATE_DEP_MOMO_GUI, 'data': dep_name}
                glo_va.momo_gui.queue_request_states_thread.put(request)
                    
                msg = assis_para.res_msg[2].format(dep_name=dep_name)
                return msg
        
        return -1

    @staticmethod
    def analyzeSympton(ret_data):
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
            predict_department_id = MomoAssistant.dt_clf.Get_Department(normalized_list_problems, normalized_list_part_bodies)

            # map the predicted dep id with curent active dep
            if init_parameters.hospital_ID in list(glo_va.map_department_table[predict_department_id].keys()):
                mapped_dep_ID = glo_va.map_department_table[predict_department_id][init_parameters.hospital_ID]
                msg = MomoAssistant.Submit_Examination(mapped_dep_ID)
                # print(msg)
                
                if msg == -1:
                    return assis_para.res_msg[14].format(dep_name=assis_para.department[predict_department_id])

                else:
                    return msg
            else:
                return assis_para.res_msg[13].format(dep_name=assis_para.department[predict_department_id])

        except Exception as e:
            LogMesssage('Has error at analyzeSympton in momo_assistant: {e}'.format(e=e))
            return assis_para.res_msg[15]

    @staticmethod
    def analyzeDepartment(deparment_name):
        try:
            deparment_name = deparment_name.strip().lower()
            for predict_department_id in assis_para.list_department:
                if deparment_name in assis_para.list_department[predict_department_id]:
                    # map the predicted dep id with curent active dep
                    if init_parameters.hospital_ID in list(glo_va.map_department_table[predict_department_id].keys()):
                        mapped_dep_ID = glo_va.map_department_table[predict_department_id][init_parameters.hospital_ID]
                        msg = MomoAssistant.Submit_Examination(mapped_dep_ID)

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

    @staticmethod
    def momoCore():
        LogMesssage('[momo_assistant_momoCore]: Start thread MOMO ASSISTANT')
        MomoAssistant.stopCurrentConversation()
        time.sleep(0.1)
        MomoAssistant.momoSay(assis_para.msg_for_states[glo_va.assis_state], opt=1)

        while glo_va.enable_momo_run:
            try:
                # NEED TO FIX BUG
                # print("Momo is listening")
                # user_voice = glo_va.momo_assis.momoListen()
                if glo_va.has_response_server == False:
                    if glo_va.is_sending_message == True:
                        continue

                    user_voice = MomoAssistant.momoListen()
                    LogMesssage('[momo_assistant_momoCore]: Patient say {}'.format(user_voice))
                    if glo_va.enable_momo_run == False or user_voice == -1:
                        MomoAssistant.stopCurrentConversation()
                        continue

                    data = {}
                    data['opt'] = 0
                    data['text'] = user_voice
                    request = {'type': glo_va.REQUEST_UPDATE_CONVERSATION_MOMO_GUI, 'data': data}
                    glo_va.momo_gui.queue_request_states_thread.put(request)

                    glo_va.timer.Start_Timer(glo_va.OPT_TIMER_SEND_MESSAGE_VOICE)
                    glo_va.is_sending_message = True
                    glo_va.server.getSymptonPatient(user_voice)
                    LogMesssage('[momo_assistant_momoCore]: Patient display symptons')

                elif glo_va.has_response_server == True:
                    glo_va.is_sending_message = False
                    glo_va.has_response_server = False

                    if glo_va.patient_symptons is None:
                        LogMesssage('[momo_assistant_momoCore]: Cannot get symptoms of patient')
                        continue
                    
                    # print(glo_va.patient_symptons)
                    MomoAssistant.measureDepartment(glo_va.patient_symptons)

                    glo_va.patient_symptons = None
                    LogMesssage('[momo_assistant_momoCore]: Received analyzed symptons')


            except Exception as e:
                print("Has error at momo_assistant_momoCore: {}".format(e))
                glo_va.ClearAssisPara()
                print("Reset program")
            
            time.sleep(0.1) 

        LogMesssage('[momo_assistant_momoCore]: Stop thread MOMO ASSISTANT')

    @staticmethod
    def measureDepartment(symptons):
        if glo_va.assis_state == glo_va.ASSIS_FIRST_STATE:
            State_1(symptons)
        elif glo_va.assis_state == glo_va.ASSIS_CHOOSE_DEP_STATE:
            State_2(symptons)
        elif glo_va.assis_state == glo_va.ASSIS_DISPLAY_SYMPTON_STATE:
            State_3(symptons)
        elif glo_va.assis_state == glo_va.ASSIS_CONFIRM_STATE:
            Confirm_Message(symptons)

# STATE -1: confirm message
# STATE 1: ask want diagnosis
# STATE 2: listen for department name
# STATE 3: listen for display sympton

# ask want diagnosis
def State_1(symptons):
    msg = assis_para.res_msg[-1]

    # If intent does not in vocabulaty say do not understant
    if symptons == -1:
        glo_va.momo_assis.momoSay(msg, opt=1)
        return

    if symptons['intent'] == 'affirm':
        glo_va.assis_state = glo_va.ASSIS_CHOOSE_DEP_STATE
        msg = assis_para.msg_for_states[glo_va.assis_state]
    elif symptons['intent'] == 'deny':
        glo_va.assis_state = glo_va.ASSIS_DISPLAY_SYMPTON_STATE
        msg = assis_para.msg_for_states[glo_va.assis_state]
    else:
        msg = Common_State(symptons)

    # print("Momo: {}".format(msg))
    glo_va.momo_assis.momoSay(msg, opt=1)
    # print()

# listen for department name
def State_2(symptons):
    msg = assis_para.res_msg[-1]

    # If intent does not in vocabulaty say do not understant
    if symptons == -1:
        glo_va.momo_assis.momoSay(msg, opt=1)
        return

    if symptons['intent'] == 'affirm':
        msg = res_msg[8]
    else:
        msg = Common_State(symptons)

    # print("Momo: {}".format(msg))
    glo_va.momo_assis.momoSay(msg, opt=1)
    # print()

# listen for display sympton
def State_3(symptons):
    msg = assis_para.res_msg[-1]

    # If intent does not in vocabulaty say do not understant
    if symptons == -1:
        glo_va.momo_assis.momoSay(msg, opt=1)
        return

    if symptons['intent'] == 'affirm':
        msg = assis_para.res_msg[8]
    else:
        msg = Common_State(symptons)

    # print("Momo: {}".format(msg))
    glo_va.momo_assis.momoSay(msg, opt=1)
    # print()

# confirm message : -1
def Confirm_Message(symptons):
    msg = assis_para.res_msg[-1]

    # If intent does not in vocabulaty say do not understant
    if symptons == -1:
        glo_va.momo_assis.momoSay(msg, opt=1)
        return

    if symptons['intent'] == 'affirm':
        msg = assis_para.res_msg[9]
        glo_va.assis_state = glo_va.assis_pre_state
        glo_va.assis_pre_state = glo_va.ASSIS_CONFIRM_STATE
        msg = assis_para.msg_for_states[glo_va.assis_state]
    elif symptons['intent'] == 'deny':
        msg = assis_para.res_msg[7]
        glo_va.ClearAssisPara()
    else:
        msg = Common_State(symptons)

    # print("Momo: {}".format(msg))
    glo_va.momo_assis.momoSay(msg, opt=1)
    # print()

def Common_State(symptons):
    msg = assis_para.res_msg[-1]
    if symptons['intent'] == 'greet':
        msg = assis_para.res_msg[6]
    elif symptons['intent'] == 'goodbye':
        msg = assis_para.res_msg[4]
        glo_va.ClearAssisPara()
    elif symptons['intent'] == 'want_exam' and symptons['deparment_name'] != -1:
        msg = glo_va.momo_assis.analyzeDepartment(symptons['deparment_name'])
        glo_va.ClearAssisPara()
    elif symptons['intent'] == 'display_symptom' and symptons['list_problem'] != -1:
        msg = glo_va.momo_assis.analyzeSympton(symptons)
        glo_va.ClearAssisPara()
    else:
        # check if previous state is confirm state or not
        # if not, save this state into pre_state
        # else keep
        if glo_va.assis_state != glo_va.ASSIS_CONFIRM_STATE:
            glo_va.assis_pre_state = glo_va.assis_state
        
        # Specify the next state is confirm state
        glo_va.assis_state = glo_va.ASSIS_CONFIRM_STATE
    
    return msg

# glo_va.momo_assis = MomoAssistant()
# glo_va.STATE = glo_va.STATE_VIEW_DEPARTMENTS

# glo_va.momo_thread_say = subprocess.call([MomoCore, ])
# glo_va.enable_momo_run = True
# momo = MomoAssistant()
# print(momo.momoListen())

# momo.momoSay('Hello')
# time.sleep(2)
# momo.momoSay('Hello Khoa')

# time.sleep(5)
# momo.momoSay('Hello Khoa')

# time.sleep(5)