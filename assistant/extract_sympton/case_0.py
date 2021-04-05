from assistant.extract_sympton.analyze_list_part_body import *

def Case_0(new_sentence):
    ret_list_problem = []
    ret_list_part_bodies = []

    list_verbs = []
    list_nouns_extracted = []

    list_part_body_of_current_verb = []

    all_nouns = ""
    state = 0

    for word in new_sentence:
        if word.type == 'problem':
            if state == 1:
                list_nouns_extracted = Analyze_List_Part_Body(all_nouns, list_part_body_of_current_verb)
                for i in list_verbs:
                    for j in list_nouns_extracted:
                        ret_list_problem.append(i)
                        ret_list_part_bodies.append(j)

                all_nouns = ""
                list_verbs = []
                list_nouns_extracted = []
                state = 0

            list_verbs.append(word.value)
        else:
            state = 1
            all_nouns += word.value + ' '
            list_part_body_of_current_verb.append(word)
    
    list_nouns_extracted = Analyze_List_Part_Body(all_nouns, list_part_body_of_current_verb)
    # print(list_verbs)
    # print(list_nouns_extracted)
    for i in list_verbs:
        if len(list_nouns_extracted) != 0:
            for j in list_nouns_extracted:
                ret_list_problem.append(i)
                ret_list_part_bodies.append(j)
        else:
            ret_list_problem.append(i)
            ret_list_part_bodies.append('none')

    return ret_list_problem, ret_list_part_bodies