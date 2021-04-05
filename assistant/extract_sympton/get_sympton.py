# import time
import json
import requests

from utils.common_functions import LogMesssage
from utils.assis_parameters import *
from assistant.extract_sympton.case_0 import *
from assistant.extract_sympton.case_1 import *

def Get_Sympton(user_voice):
    try:
        # start_time = time.time()
        url = 'http://localhost:5005/model/parse'
        data = '{"text":"' + user_voice + '"}'
        ret_data = {'intent': -1, 'list_problem': -1, 'list_part_of_body': -1, 'deparment_name': -1}
        response = json.loads(requests.post(url, data=data.encode('utf-8')).text)

        # print('time to request: {}'.format(time.time() - start_time))
        list_problems = list()
        list_part_of_bodies = list()

        # 0: SUB + V + Noun
        # 1: Noun + Ved
        case = None

        if 'intent' in response:
            ret_data['intent'] = response['intent']['name']
        else:
            return -1

        if ret_data['intent'] == 'want_exam':
            if 'entities' in response:
                for i in response['entities']:
                    if i['extractor'] == 'CRFEntityExtractor' and i['entity'] == 'deparment_name':
                        ret_data['deparment_name'] = i['value']
                        print(ret_data)
                        return ret_data
            else:
                return -1
        elif ret_data['intent'] == 'display_symptom':
            if 'entities' in response:
                for i in response['entities']:
                    # with part of body and problem, we use RegexEntityExtractor to look up value
                    if i['extractor'] == 'RegexEntityExtractor':
                        if i['entity'] == 'part_of_body':
                            w = Word(i['value'], i['start'], i['end'], 'part_of_body')
                            list_part_of_bodies.append(w)
                        elif i['entity'] == 'problem':
                            w = Word(i['value'], i['start'], i['end'], 'problem')
                            list_problems.append(w)
            else:
                return -1

        if len(list_problems) == 0:
            return ret_data
        else:
            if len(list_part_of_bodies) == 0:
                case = 0
            else:
                if list_part_of_bodies[0].start > list_problems[0].start:
                    case = 0
                else:
                    case = 1

        new_sentence = Create_New_Sentence(list_problems, list_part_of_bodies)

        if case == 0:
            ret_data['list_problem'], ret_data['list_part_of_body'] = Case_0(new_sentence)
        else:
            ret_data['list_problem'], ret_data['list_part_of_body'] = Case_1(new_sentence)
            
        print(ret_data['list_problem'])
        print(ret_data['list_part_of_body'])
        return ret_data
    except:
        LogMesssage('Has error at Get_Sympton in get_sympton: {e}'.format(e=e))
        # Set default value when this program is crash
        ret_data['list_problem'] = ['rách']
        ret_data['list_part_of_body'] = ['none']
        return ret_data

def Create_New_Sentence(list_problems, list_part_of_bodies):
    new_sentence = list()
    # Loop until both list_problems and list_part_of_bodies is empty
    while len(list_problems) != 0 or len(list_part_of_bodies) != 0:
        # If list_problem is empty, append value in list_part_of_bodies
        if len(list_problems) == 0:
            new_sentence.append(list_part_of_bodies.pop(0))
        # If list_part_of_bodies is empty, append value in list_problems
        elif len(list_part_of_bodies) == 0:
            new_sentence.append(list_problems.pop(0))
        # Else compare which value in 2 list appear first then append it
        else:
            if list_problems[0].start < list_part_of_bodies[0].start:
                new_sentence.append(list_problems.pop(0))
            else:
                new_sentence.append(list_part_of_bodies.pop(0))
    return new_sentence