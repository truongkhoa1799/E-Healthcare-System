import os
import yaml
import pathlib
import queue
from PyQt5 import uic
from utils.assis_parameters import AssistantParameter
from threading import Event

show_fps = True
PROJECT_PATH = pathlib.Path().absolute()

class GlobalVariable:
    def __init__(self):
        self.main_thread = None
        
        # CENTER_FACE
        self.centerface_detector = None
        self.stop_program = Event()
        self.start_program = Event()

        # VERIFYING PATIENT
        self.check_ssn = "-1"
        
        # # test
        # self.times_measure = 0
        # self.list_time_detection = []
        # self.list_time_recognition = []
        # self.times_send = 0
        # self.start_time = None
        # self.list_time_send_server = []

        ########################################################
        # SERVICES PARAMETERS                                  #
        ########################################################
        self.gui = None
        self.momo_gui = None
        self.timer = None
        self.camera = None
        self.server = None
        self.count_face = None
        self.face_recognition = None

        ########################################################
        # FLAG                                                 #
        ########################################################
        self.flg_init_GUI = False
        self.flg_init_timer = False
        self.flg_init_camera = False
        self.flg_init_count_face = False
        self.flg_server_connected = False
        self.flg_init_momo_assistant = False
        self.flg_init_face_recognition = False
        
        ########################################################
        # SERVER PARAMETERS                                    #
        ########################################################
        self.lock_init_state = None
        self.is_sending_message = False
        self.has_response_server = False
        self.lock_response_server = None
        # -1: none, 1 server
        self.TIMER_GOT_BY_NO_ONE = -1
        self.TIMER_GOT_BY_SERVER = 0

        self.turn = -1 

        ########################################################
        # FACE RECOGNITION PARAMETERS                          #
        ########################################################
        self.img = None
        self.times_missing_face = 0

        ########################################################
        # IOT HUB PARAMETERS                                   #
        ########################################################
        self.device_ID = None
        self.eventhub_name = None
        self.eventhub_connection = None
        self.device_iothub_connection = None

        ########################################################
        # NEW USER PARAMETERS                                  #
        ########################################################
        # store embedded face of new user
        self.list_embedded_face_new_user = ""
        self.num_face_new_user = 5
        # all pose of new user
        self.current_shape = 0 # up : 0, down : 1, left : 2, right : 3, forward : 4
        self.num_user_pose = 0
        # parameters for get the max user pose for new patient
        self.check_current_shape = False
        self.num_correct_user_pose = 0
        self.list_embedded_face_origin_new_patient = []

        self.check_pose = [
            # sign_v, diff_v, sign_h, diff_h 
            [-1, 5, -1, 5],  # front
            [1, 7, -1, 5],   # up
            [-1, 5, -1, 5],  # down
            [-1, 5, -1, 7],  # left
            [-1, 5, 1, 7]    # right
        ]

        ########################################################
        # PREDICT DEPARMENT PARAMETERS                         #
        ########################################################
        self.patient_symptons = None

        ########################################################
        # SUBMIT PARAMETERS                                    #
        ########################################################
        # self.patient_ID = -1
        self.return_stt = -1
        self.valid_stt = -1

        ########################################################
        # SENSOR                                               #
        ########################################################
        self.measuring_sensor = None
        self.connected_sensor_device = False

        # PARAMETERS for user_info
        self.USER_INFOR_HAS_FACE = 0
        self.USER_INFOR_NO_FACE = -1
        self.USER_INFOR_DEFAULT = -2
        self.USER_INFOR_WEARING_MASK = -3

        self.HAS_INIT_PARAMETERS = 0
        self.NOT_HAS_INIT_PARAMETERS = -1
        self.INVALID_DEVICE_ID = -2

        self.SENSOR_HAS_VALUE = 0
        self.SENSOR_DEFAULT = -1

        self.EXAM_HAS_VALUE = 0
        self.EXAM_DEFAULT = -1

        ########################################################
        # ASSISTANT                                            #
        ########################################################
        # MOMO STATE
        self.ASSIS_FIRST_STATE = 1
        self.ASSIS_CHOOSE_DEP_STATE = 2
        self.ASSIS_DISPLAY_SYMPTON_STATE = 3
        self.ASSIS_CONFIRM_STATE = -1

        self.MOMO_SAY_BLOCKING = 0
        self.MOMO_SAY_WITHOUT_BLOCKING = 1

        # used to map predicted department with current running dep in database
        self.momo_assis = None
        self.thread_assis = None
        self.enable_momo_run = False
        self.map_department_table = None

        self.assis_state = self.ASSIS_FIRST_STATE
        self.assis_pre_state = self.ASSIS_CONFIRM_STATE

        ########################################################
        # STATE of the program                                 #
        ########################################################
        # STATES
        self.STATE_RECOGNIZE_PATIENT = 1
        self.STATE_CONFIRM_PATIENT = 2
        self.STATE_MEASURE_SENSOR = 3
        self.STATE_VIEW_DEPARTMENTS = 4
        self.STATE_CONFIRM_NEW_PATIENT = 5
        self.STATE_NEW_PATIENT = 6
        self.STATE_WAITING_SUB_EXAM = 7
        self.STATE_MEASURING_SENSOR = 8

        self.STATE = self.STATE_RECOGNIZE_PATIENT
        
        ########################################################
        # BUTTON                                               #
        ########################################################
        self.button = -1
        # Button used to check when return message of submitting examination
        self.button_ok_pressed = True

        self.DEFAULT_BUTTON = -1
        self.BUTTON_EXIST = 0
        self.BUTTON_CANCEL_CONFIRM_PATIENT = 1
        self.BUTTON_ACCEPT_CONFIRM_PATIENT = 2
        self.BUTTON_VIEW_LIST_DEP = 3
        self.BUTTON_CAPTURE_SENSOR = 4
        self.BUTTON_DENY_NEW_PATIENT = 5
        self.BUTTON_ACCEPT_NEW_PATIENT = 6
        self.BUTTON_CONFIRM_PATIENT = 7
        self.BUTTON_SUBMIT_EXAM = 8
        self.BUTTON_CONFIRM_DEP = 9
        self.BUTTON_OKAY = 10
        self.BUTTON_SELECT_DEP = 11
        self.BUTTON_CONFIRM_SENSOR = 12
        self.BUTTON_GUILDE_SENSOR = 13
        self.BUTTON_QUIT_GUILDE_SENSOR = 14
        self.BUTTON_NEXT_GUILDE_SENSOR = 15
        self.BUTTON_BACK_GUILDE_SENSOR = 16
        self.BUTTON_CONNECT_DEVICE_SENSOR = 17
        self.BUTTON_DIAGNOSE_SYMPTOMS = 18
        self.BUTTON_CLOSE_MOMO_GUI = 19
        self.BUTTON_VERIFY_PATIENT = 20

        ########################################################
        # REQUEST MAIN GUI                                     #
        ########################################################
        self.REQUEST_CONFIRM_NEW_PATIENT = 0
        self.REQUEST_CHANGE_GUI = 1
        self.REQUEST_UPDATE_PATIENT_INFO = 2
        # self.REQUEST_CLEAR_PATIENT_INFO = 3
        self.REQUEST_ACTIVATE_NEW_FACE = 4
        self.REQUEST_UPDATE_EXAM_ROOM = 5
        self.REQUEST_CLEAR_EXAM_ROOM = 6
        self.REQUEST_UPDATE_DEPARTMENT_LIST = 9
        self.REQUEST_CLEAR_DEPARTMENT_LIST = 10
        self.REQUEST_UPDATE_SENSOR = 7
        self.REQUEST_CLEAR_SENSOR = 8
        # self.REQUEST_MEASURE_SENSOR = 11
        self.REQUEST_NOTIFY_MESSAGE = 12
        # self.REQUEST_DEACTIVATE_NEW_FACE = 13
        self.REQUEST_CLEAR_SELECTED_EXAM_ROOM = 14
        self.REQUEST_UPDATE_SELECTED_EXAM_ROOM = 15
        self.REQUEST_OPEN_MOMO_GUI = 18
        self.REQUEST_UPDATE_DEP_MOMO_GUI = 19
        self.REQUEST_UPDATE_CONVERSATION_MOMO_GUI = 20
        ########################################################
        # REQUEST MEASURE SENSOR GUI                           #
        ########################################################
        self.REQUEST_UPDATE_OSO2 = 16
        self.REQUEST_UPDATE_ESP = 17

        ########################################################
        # DIALOG                                               #
        ########################################################
        self.EXIST_DIALOG = 0
        self.CONFIRM_PATIENT_DIALOG = 1
        self.CONFIRM_NEW_PATIENT_DIALOG = 2
        self.CONFIRM_SENSOR_INFORMATION = 3

        # PATH_PARA
        config_para_path = os.path.join(PROJECT_PATH, 'config_para.yaml')
        with open(config_para_path, 'r') as file:
            documents = yaml.load(file, Loader=yaml.FullLoader)

            # Momo assistant
            self.VOICE_PATH_FILE = os.path.join(PROJECT_PATH, str(documents['path']['voice_assis_path']))
            self.MAP_DEP_TABLE_PATH = os.path.join(PROJECT_PATH, str(documents['path']['map_dep_table_path']))
            self.DT_MODEL_PREDICT_DEP_PATH = os.path.join(PROJECT_PATH, str(documents['path']['decision_tree_model_predict_dep_path']))
            self.DICT_PART_BOD_PROBLEMS_PREDICT_DEP_PATH = os.path.join(PROJECT_PATH, str(documents['path']['dict_part_body_problems_predict_dep_path']))
            self.CENTER_FACE_MODEL_PATH = os.path.join(PROJECT_PATH, str(documents['path']['center_face_model']))

            # Connection server
            self.PARTITION_ID = str(documents['azure']['partition_id'])
            self.CONNECTION_AZURE_PATH = os.path.join(PROJECT_PATH, str(documents['path']['azure_connection_path']))
            
            # Parameters for image processing, and KNN model
            self.IMAGE_SIZE = int(documents['preprocessing']['image_size'])
            self.BASE_BRIGHTNESS = int(documents['preprocessing']['base_brightness'])
            
            # identifying_face
            self.CYCLE_COUNT_FACE_PERIOD = int(documents['identifying_face']['cycle_count_face_period'])
            self.NUMBER_DETECTED_FACE_TRANSMITED = int(documents['identifying_face']['number_deteced_face_allowed'])
            # MAX length for HOG face Detector
            self.MAX_LENGTH_IMG = int(documents['identifying_face']['max_length_img'])
            self.MAX_LENGTH_IMG_NEW_USER = int(documents['identifying_face']['max_length_img_new_user'])
            self.MAX_EDGE = int(documents['identifying_face']['max_edge'])

            self.FACE_DETECTOR_MODEL = documents['identifying_face']['face_detector_model']
            self.SHAPE_PREDICTOR_MODEL = str(documents['identifying_face']['shape_predictor_model'])

            # FACE RECOGNITION MODEL
            self.PREDICTOR_5_POINT_MODEL = os.path.join(PROJECT_PATH, str(documents['path']['predictor_5_point_model']))
            self.PREDICTOR_68_POINT_MODEL = os.path.join(PROJECT_PATH, str(documents['path']['predictor_68_point_model']))
            self.CNN_FACE_DETECTOR = os.path.join(PROJECT_PATH, str(documents['path']['cnn_face_detector_model']))
            self.RESNET_MODEL = os.path.join(PROJECT_PATH, str(documents['path']['resnet_path']))

            # CENTER FACE MODEL
            self.WIDTH_IMG_CENTER_FACE = int(documents['identifying_face']['width_img_center_face'])
            self.HEIGHT_IMG_CENTER_FACE = int(documents['identifying_face']['height_img_center_face'])

            # Display image
            self.CAMERA_CAPTURE_WIDTH = int(documents['camera']['camera_capture_width'])
            self.CAMERA_CAPTURE_HEIGHT = int(documents['camera']['camera_capture_height'])
            self.FLIP_METHOD_CAM = int(documents['camera']['flip_method'])

            # size for display patient
            self.LOCATION_RECOGNIZE_FACE_WIDTH = int(documents['gui']['location_recognize_face_width'])
            self.LOCATION_RECOGNIZE_FACE_HEIGHT = int(documents['gui']['location_recognize_face_height'])
            # size for displaying new patient
            self.LOCATION_ADD_FACE_WIDTH = int(documents['gui']['location_add_face_width'])
            self.LOCATION_ADD_FACE_HEIGHT = int(documents['gui']['location_add_face_height'])

            # MARGIN FACE LOCATION
            self.MARGIN_FACE_LOCATION = int(documents['gui']['margin_face_location'])

            # # Parameters for GUI
            # self.WIDTH_GUI = int(documents['gui']['width_gui'])
            # self.HEIGHT_GUI = int(documents['gui']['height_gui'])
            # self.CAM_EXAM_LAYOUT_WIDTH = int(documents['gui']['cam_exam_layout_width'])
            # self.CAM_EXAM_LAYOUT_HEIGHT = int(documents['gui']['cam_exam_layout_height'])
            # self.INFOR_SENSOR_LAYOUT_WIDTH = int(documents['gui']['sensor_exam_layout_width'])
            # self.INFOR_SENSOR_LAYOUT_HEIGHT = int(documents['gui']['sensor_exam_layout_height'])
            
            self.MAIN_GUI_PATH = str(documents['path']['main_gui_path'])
            self.MEASURE_SENSOR_GUI_PATH = str(documents['path']['measure_sensor_gui_path'])
            self.OKAY_DIALOG_PATH = str(documents['path']['okdialog_path'])
            self.YES_NO_DIALOG_PATH = str(documents['path']['yes_no_dialog'])
            self.MOMO_GUI_DIALOG_PATH = str(documents['path']['momo_gui_dialog'])

            # Parameters for timer
            self.NUM_MISSING_FACE = int(documents['timer']['num_missing_face'])
            self.TIMEOUT_MISSING_FACE = int(documents['timer']['timeout_missing_face'])

            self.TIMEOUT_VALIDATE = int(documents['timer']['timeout_validate'])
            self.OPT_TIMER_VALIDATE = int(documents['timer']['opt_timer_validate'])

            self.TIMEOUT_GET_EXAMINATION_ROOM = int(documents['timer']['timeout_get_examination_room'])
            self.OPT_TIMER_GET_EXAMINATION_ROOM = int(documents['timer']['opt_timer_get_examination_room'])

            self.TIMEOUT_SUBMIT_EXAMINATION = int(documents['timer']['timeout_submit_examination'])
            self.OPT_TIMER_SUBMIT_EXAMINATION = int(documents['timer']['opt_timer_submit_examination'])

            self.TIMEOUT_SEND_MESSAGE_VOICE = int(documents['timer']['timeout_send_voice_message'])
            self.OPT_TIMER_SEND_MESSAGE_VOICE = int(documents['timer']['opt_timer_send_voice_message'])

            self.TIMEOUT_GET_INIT_PARAMETERS = int(documents['timer']['timeout_get_init_parameters'])
            self.OPT_TIMER_GET_INIT_PARAMETERS = int(documents['timer']['opt_timer_get_init_parameters'])

            # MOMO MESSAGES
            self.momo_messages = {
                'ask_confirm': '123',
                'ask_new_patient': '123',
                'say_bye': '123',
                'inform_state_3': '123',
                'inform_oso2': '123',
                'measure_sensor_inform_0': '123',
                'measure_sensor_inform_1': '123',
                'measure_sensor_inform_2': '123',
                'capture_img': '123',
                'ask_take_of_mask': '123'
            }
            self.momo_messages['ask_confirm'] = str(documents['momo_message']['ask_confirm'])
            self.momo_messages['ask_new_patient'] = str(documents['momo_message']['ask_new_patient'])
            self.momo_messages['say_bye'] = str(documents['momo_message']['say_bye'])
            self.momo_messages['inform_state_3'] = str(documents['momo_message']['inform_state_3'])
            self.momo_messages['inform_oso2'] = str(documents['momo_message']['inform_oso2'])
            self.momo_messages['measure_sensor_inform_0'] = str(documents['momo_message']['measure_sensor_inform_0'])
            self.momo_messages['measure_sensor_inform_1'] = str(documents['momo_message']['measure_sensor_inform_1'])
            self.momo_messages['measure_sensor_inform_2'] = str(documents['momo_message']['measure_sensor_inform_2'])
            self.momo_messages['ask_take_of_mask'] = str(documents['momo_message']['ask_take_of_mask'])

            self.momo_messages['capture_img'] = documents['momo_message']['capture_img']

        ########################################################
        # GUI PARAMETERS                                       #
        ########################################################
        self.yes_no_dialog = uic.loadUiType(self.YES_NO_DIALOG_PATH)[0]
        self.ok_dialog = uic.loadUiType(self.OKAY_DIALOG_PATH)[0]
        self.momo_gui_dialog = uic.loadUiType(self.MOMO_GUI_DIALOG_PATH)[0]
        

        # load parameters for assistant
        with open(self.MAP_DEP_TABLE_PATH, 'r') as file:
            self.map_department_table = yaml.load(file, Loader=yaml.FullLoader)
        


    def ClearAssisPara(self):
        self.assis_state = self.ASSIS_FIRST_STATE
        self.assis_pre_state = self.ASSIS_CONFIRM_STATE

class User_Infor:
    def __init__(self):
        # 0: has infro
        # -1: no face
        # -2: default
        self.status = glo_va.USER_INFOR_DEFAULT
        self.patient_ID = -1
        self.user_info = None
        self.Clear()

    def Clear(self):
        self.status = glo_va.USER_INFOR_DEFAULT
        self.user_info = None
        self.patient_ID = -1
    
    def Update_Info(self, user_info):
        self.status = glo_va.USER_INFOR_HAS_FACE
        self.user_info = user_info
        self.patient_ID = user_info['patient_ID']
    
    def wearingMask(self):
        self.status = glo_va.USER_INFOR_WEARING_MASK

    def NoFace(self):
        self.status = glo_va.USER_INFOR_NO_FACE

class InitParameters:
    def __init__(self):
        self.status = glo_va.NOT_HAS_INIT_PARAMETERS
        self.hospital_ID = None
        self.list_examination_room = []

        # self.list_examination_room = [
        # {'dep_ID': 1, 'dep_name': 'Khoa noi', 'building_code': 'A1', 'room_code': '101'},
        # {'dep_ID': 2, 'dep_name': 'Khoa ngoai', 'building_code': 'A1', 'room_code': '102'}, 
        # {'dep_ID': 3, 'dep_name': 'Khoa tai mui hong', 'building_code': 'A1', 'room_code': '201'},
        # {'dep_ID': 4, 'dep_name': 'Khoa Mat', 'building_code': 'B1', 'room_code': '101'}, 
        # {'dep_ID': 5, 'dep_name': 'Khoa Than Kinh', 'building_code': 'B1', 'room_code': '201'},  
        # {'dep_ID': 6, 'dep_name': 'Khoa Tim Mach', 'building_code': 'C1', 'room_code': '101'}, 
        # {'dep_ID': 7, 'dep_name': 'Khoa San', 'building_code': 'C1', 'room_code': '201'}
        # ]

    def Clear(self):
        self.status = glo_va.NOT_HAS_INIT_PARAMETERS
        self.hospital_ID = None
        self.list_examination_room = []
    
    def updateInitParameters(self, parameters):
        self.status = glo_va.HAS_INIT_PARAMETERS
        self.hospital_ID = parameters['hospital_ID']
        self.list_examination_room = parameters['list_exam_rooms']
    
class Sensor:
    def __init__(self):
        self.sensor_infor = None
        self.Clear()
    
    def Clear(self):
        self.sensor_infor = None
    
    def Update_Sensor(self, sensor):
        self.sensor_infor = sensor
    
    def getStatus(self):
        if self.sensor_infor is None \
            or self.sensor_infor['height'] == '' or self.sensor_infor['weight'] == '' \
            or self.sensor_infor['spo2'] == '' or self.sensor_infor['temperature'] == '' \
            or self.sensor_infor['heart_pulse'] == '' or self.sensor_infor['bmi'] == '':
            glo_va.SENSOR_DEFAULT
            
        return glo_va.SENSOR_HAS_VALUE

class Examination:
    def __init__(self):
        self.status = glo_va.EXAM_DEFAULT
        self.__department = None
        self.__room = None
        self.__building = None
        self.Clear()
    
    def Clear(self):
        self.status = glo_va.EXAM_DEFAULT
        self.__department = None
        self.__room = None
        self.__building = None
    
    def Update_Examination(self, dep, room):
        self.status = glo_va.EXAM_HAS_VALUE
        temp = room.split('-')
        
        self.__department = dep
        self.__building = temp[0]
        self.__room = temp[1]
    
    def Get_Exam_Room_Infor(self):
        return self.__department, self.__building, self.__room

glo_va = GlobalVariable()
assis_para = AssistantParameter()
user_infor = User_Infor()
sensor = Sensor()
exam = Examination()
init_parameters = InitParameters()