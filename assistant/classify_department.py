import sys
sys.path.append('/home/thesis/Documents/thesis/E-Healthcare-System')
import numpy as np
import pickle

from utils.parameters import *

class ClassifyDepartment:
    def __init__(self):
        self.__decision_tree = None
        self.__dict_part_of_body = None
        self.__dict_problem = None
        self.__dict_department = None

        with open(glo_va.DT_MODEL_PREDICT_DEP_PATH, 'rb') as f:
            self.__decision_tree = pickle.load(f)

        with open(glo_va.DICT_PART_BOD_PROBLEMS_PREDICT_DEP_PATH, 'rb') as f_1:
            dict_data = pickle.load(f_1)
            self.__dict_problem = dict_data['problem']
            self.__dict_part_of_body = dict_data['part_of_body']
            self.__dict_department = dict_data['dict_department']

    def Get_Department(self, list_problems, list_part_of_body):
        ret_predict_department = None
        max_department_occurence = 0
        list_predict_departments = list()
        dict_predict_departments = dict()

        for i in range(len(list_problems)):
            # print("problem: {}, part_body: {}".format(list_problems[i],list_part_of_body[i]))
            if list_problems[i] not in self.__dict_problem or list_part_of_body[i] not in self.__dict_part_of_body:
                dep = '2'
                list_predict_departments.append(dep)
            else:
                X = np.array([self.__dict_problem[list_problems[i]], self.__dict_part_of_body[list_part_of_body[i]]]).reshape(1, -1)
                y_pred_dt = self.__decision_tree.predict(X)
                for i in self.__dict_department:
                    if self.__dict_department[i] == y_pred_dt:
                        list_predict_departments.append(i)
                        break

        print(list_predict_departments)
        # print()
        for i in list_predict_departments:
            list_departmeents = i.split('-')
            # print(list_departmeents)
            for j in range(len(list_departmeents)):
                if list_departmeents[j] not in dict_predict_departments:
                    dict_predict_departments[list_departmeents[j]] = 9 - j
                else:
                    dict_predict_departments[list_departmeents[j]] = dict_predict_departments[list_departmeents[j]] + 9 - j
                
                if dict_predict_departments[list_departmeents[j]] > max_department_occurence:
                    max_department_occurence = dict_predict_departments[list_departmeents[j]]
                    ret_predict_department = list_departmeents[j]
        
        print(dict_predict_departments)
        print(ret_predict_department)
        # Đảm bảo luôn có part_body
        # return department[int(ret_predict_department)]
        return int(ret_predict_department)