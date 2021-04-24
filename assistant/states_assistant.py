from utils.parameters import *
# STATE -1: confirm message
# STATE 1: ask want diagnosis
# STATE 2: listen for department name
# STATE 3: listen for display sympton

# ask want diagnosis
def State_1(symptons):
    msg = assis_para.res_msg[-1]

    # If intent does not in vocabulaty say do not understant
    if symptons == -1:
        glo_va.momo_assis.Say(msg, opt=1)
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
    glo_va.momo_assis.Say(msg, opt=1)
    # print()

# listen for department name
def State_2(symptons):
    msg = assis_para.res_msg[-1]

    # If intent does not in vocabulaty say do not understant
    if symptons == -1:
        glo_va.momo_assis.Say(msg, opt=1)
        return

    if symptons['intent'] == 'affirm':
        msg = res_msg[8]
    else:
        msg = Common_State(symptons)

    # print("Momo: {}".format(msg))
    glo_va.momo_assis.Say(msg, opt=1)
    # print()

# listen for display sympton
def State_3(symptons):
    msg = assis_para.res_msg[-1]

    # If intent does not in vocabulaty say do not understant
    if symptons == -1:
        glo_va.momo_assis.Say(msg, opt=1)
        return

    if symptons['intent'] == 'affirm':
        msg = assis_para.res_msg[8]
    else:
        msg = Common_State(symptons)

    # print("Momo: {}".format(msg))
    glo_va.momo_assis.Say(msg, opt=1)
    # print()

# confirm message : -1
def Confirm_Message(symptons):
    msg = assis_para.res_msg[-1]

    # If intent does not in vocabulaty say do not understant
    if symptons == -1:
        glo_va.momo_assis.Say(msg, opt=1)
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
    glo_va.momo_assis.Say(msg, opt=1)
    # print()

def Common_State(symptons):
    msg = assis_para.res_msg[-1]
    if symptons['intent'] == 'greet':
        msg = assis_para.res_msg[6]
    elif symptons['intent'] == 'goodbye':
        msg = assis_para.res_msg[4]
        glo_va.ClearAssisPara()
    elif symptons['intent'] == 'want_exam' and symptons['deparment_name'] != -1:
        msg = glo_va.momo_assis.Analyze_Department(symptons['deparment_name'])
        glo_va.ClearAssisPara()
    elif symptons['intent'] == 'display_symptom' and symptons['list_problem'] != -1:
        msg = glo_va.momo_assis.Analyze_Sympton(symptons)
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