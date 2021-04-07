from utils.parameters import *
from assistant.states_assistant import *
from utils.common_functions import LogMesssage

def MomoCore():
    LogMesssage('[MomoCore]: Start thread MOMO ASSISTANT')
    glo_va.momo_assis.Say(msg_for_states[glo_va.assis_state])
    # while glo_va.ENABLE_PROGRAM_RUN:
    # while True:
    while glo_va.STATE == glo_va.STATE_VIEW_DEPARTMENTS:
        # if glo_va.STATE != glo_va.STATE_VIEW_DEPARTMENTS:
        #     continue
        try:
            # NEED TO FIX BUG
            # print("Momo is listening")
            # user_voice = glo_va.momo_assis.Listen()
            user_voice = input('Momo is listening\n')

            # If has a noise, continue
            if user_voice != -1:
                if glo_va.assis_state == glo_va.ASSIS_FIRST_STATE:
                    State_1(user_voice)
                elif glo_va.assis_state == glo_va.ASSIS_CHOOSE_DEP_STATE:
                    State_2(user_voice)
                elif glo_va.assis_state == glo_va.ASSIS_DISPLAY_SYMPTON_STATE:
                    State_3(user_voice)
                elif glo_va.assis_state == glo_va.ASSIS_CONFIRM_STATE:
                    Confirm_Message(user_voice)
                
                print("State: {}, pre-State: {}".format(glo_va.assis_state, glo_va.assis_pre_state))


        except Exception as e:
            print("Has error at main: {}".format(e))
            glo_va.ClearAssisPara()
            print("Reset program")

    LogMesssage('[MomoCore]: Stop thread MOMO ASSISTANT')