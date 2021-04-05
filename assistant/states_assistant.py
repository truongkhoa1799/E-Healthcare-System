from utils.assis_parameters import *
from utils.parameters import *
from assistant.extract_sympton.get_sympton import Get_Sympton
# STATE -1: confirm message
# STATE 1: ask want diagnosis
# STATE 2: listen for department name
# STATE 3: listen for display sympton

# ask want diagnosis
def State_1(user_voice):
    msg = res_msg[-1]
    ret_data = Get_Sympton(user_voice)

    # If intent does not in vocabulaty say do not understant
    if ret_data == -1:
        glo_va.momo_assis.Say(msg)
        return

    if ret_data['intent'] == 'affirm':
        glo_va.assis_state = glo_va.ASSIS_CHOOSE_DEP_STATE
        msg = msg_for_states[glo_va.assis_state]
    elif ret_data['intent'] == 'deny':
        glo_va.assis_state = glo_va.ASSIS_DISPLAY_SYMPTON_STATE
        msg = msg_for_states[glo_va.assis_state]
    else:
        msg = Common_State(ret_data)

    # print("Momo: {}".format(msg))
    if msg != -1:
        glo_va.momo_assis.Say(msg)
    # print()

# listen for department name
def State_2(user_voice):
    msg = res_msg[-1]
    ret_data = Get_Sympton(user_voice)

    # If intent does not in vocabulaty say do not understant
    if ret_data == -1:
        glo_va.momo_assis.Say(msg)
        return

    if ret_data['intent'] == 'affirm':
        msg = res_msg[8]
    else:
        msg = Common_State(ret_data)

    # print("Momo: {}".format(msg))
    if msg != -1:
        glo_va.momo_assis.Say(msg)
    # print()

# listen for display sympton
def State_3(user_voice):
    msg = res_msg[-1]
    ret_data = Get_Sympton(user_voice)

    # If intent does not in vocabulaty say do not understant
    if ret_data == -1:
        glo_va.momo_assis.Say(msg)
        return

    if ret_data['intent'] == 'affirm':
        msg = res_msg[8]
    else:
        msg = Common_State(ret_data)

    # print("Momo: {}".format(msg))
    if msg != -1:
        glo_va.momo_assis.Say(msg)
    # print()

# confirm message : -1
def Confirm_Message(user_voice):
    msg = res_msg[-1]
    ret_data = Get_Sympton(user_voice)

    # If intent does not in vocabulaty say do not understant
    if ret_data == -1:
        glo_va.momo_assis.Say(msg)
        return

    if ret_data['intent'] == 'affirm':
        msg = res_msg[9]
        glo_va.assis_state = glo_va.assis_pre_state
        glo_va.assis_pre_state = glo_va.ASSIS_CONFIRM_STATE
        msg = msg_for_states[glo_va.assis_state]
    elif ret_data['intent'] == 'deny':
        msg = res_msg[7]
        glo_va.ClearAssisPara()
    else:
        msg = Common_State(ret_data)

    # print("Momo: {}".format(msg))
    if msg != -1:
        glo_va.momo_assis.Say(msg)
    # print()

def Common_State(ret_data):
    msg = res_msg[-1]
    if ret_data['intent'] == 'greet':
        msg = res_msg[6]
    elif ret_data['intent'] == 'goodbye':
        msg = res_msg[4]
        glo_va.ClearAssisPara()
    elif ret_data['intent'] == 'want_exam' and ret_data['deparment_name'] != -1:
        msg = glo_va.momo_assis.Analyze_Department(ret_data['deparment_name'])
        glo_va.ClearAssisPara()
    elif ret_data['intent'] == 'display_symptom' and ret_data['list_problem'] != -1:
        msg = glo_va.momo_assis.Analyze_Sympton(ret_data)
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