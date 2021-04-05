from assistant.extract_sympton.analyze_list_part_body import *

def Case_1(new_sentence):
    ret_list_problem = []
    ret_list_part_bodies = []

    list_verbs = []
    list_nouns_extracted = []

    list_part_body_of_current_verb = []

    all_nouns = ""
    state = 0

    for word in new_sentence:
        if word.type == 'part_of_body':
            if state == 1:
                for i in list_nouns_extracted:
                    for j in list_verbs:
                        ret_list_problem.append(j)
                        ret_list_part_bodies.append(i)
                all_nouns = ""
                list_verbs = []
                list_nouns_extracted = []

            all_nouns += word.value + ' '
            list_part_body_of_current_verb.append(word)
            state = 0
        else:
            if state == 0:
                list_nouns_extracted = Analyze_List_Part_Body(all_nouns, list_part_body_of_current_verb)
                state = 1
            
            list_verbs.append(word.value)
        
    for i in list_nouns_extracted:
        for j in list_verbs:
            ret_list_problem.append(j)
            ret_list_part_bodies.append(i)

    return ret_list_problem, ret_list_part_bodies