from utils.parameters import assis_para

def Analyze_List_Part_Body(all_nouns, list_part_body_of_current_verb):
    list_nouns_extracted = []
    all_nouns = all_nouns.strip()
    i = 0
    while i < len(assis_para.list_composite_words):
        # Check whether this composite noun exist in all_nouns
        # If yes, get the first appearance in all_noun
        start_position = all_nouns.find(assis_para.list_composite_words[i])
        if start_position != -1:
            # Calculate the end of this word.
            end_position = start_position + len(assis_para.list_composite_words[i])
            
            # append composite noun to list_nouns_extracted, dont forget to remove last white space
            noun_extracted = all_nouns[start_position:end_position]
            # Change composite noun to similar part of body
            list_nouns_extracted.append(noun_extracted)

            # remove composite noun just extracted. And remove white space
            all_nouns = all_nouns.replace(all_nouns[start_position:end_position] , '', 1).strip()
        else:
            i += 1
    
    for part_body in list_part_body_of_current_verb:
        if part_body.value == all_nouns[0:len(part_body.value)]:
            noun_extracted = all_nouns[0:len(part_body.value)]
            list_nouns_extracted.append(noun_extracted)

            # remove composite noun just extracted. And remove white space
            all_nouns = all_nouns.replace(all_nouns[0:len(part_body.value)] , '', 1).strip()
    
    return list_nouns_extracted