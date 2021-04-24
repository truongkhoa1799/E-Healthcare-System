import time
from utils.parameters import *
from utils.common_functions import LogMesssage
# from assistant.extract_sympton.get_sympton import Get_Sympton

def MomoCore():
    LogMesssage('[MomoCore]: Start thread MOMO ASSISTANT')
    glo_va.momo_assis.stopCurrentConversation()
    time.sleep(0.1)
    glo_va.momo_assis.Say(assis_para.msg_for_states[glo_va.assis_state], opt=1)

    while glo_va.enable_momo_run:
        # if glo_va.STATE != glo_va.STATE_VIEW_DEPARTMENTS:
        #     continue
        try:
            # NEED TO FIX BUG
            # print("Momo is listening")
            # user_voice = glo_va.momo_assis.Listen()
            if glo_va.has_response_server == False:
                if glo_va.is_sending_message == True:
                    continue

                user_voice = glo_va.momo_assis.Listen()
                LogMesssage('[MomoCore]: Patient say {}'.format(user_voice))
                if glo_va.enable_momo_run == False or user_voice == -1:
                    continue

                glo_va.timer.Start_Timer(glo_va.OPT_TIMER_SEND_MESSAGE_VOICE)
                glo_va.is_sending_message = True
                glo_va.server.getSymptonPatient(user_voice)
                LogMesssage('[State_4]: Patient display symptons')

            elif glo_va.has_response_server == True:
                glo_va.is_sending_message = False
                glo_va.has_response_server = False

                if glo_va.patient_symptons is None:
                    continue
                
                print(glo_va.patient_symptons)
                glo_va.momo_assis.measureDepartment(glo_va.patient_symptons)

                glo_va.patient_symptons = None
                LogMesssage('[State_4]: Received analyzed symptons')


        except Exception as e:
            print("Has error at MomoCore: {}".format(e))
            glo_va.ClearAssisPara()
            print("Reset program")
        
        time.sleep(0.1) 

    LogMesssage('[MomoCore]: Stop thread MOMO ASSISTANT')