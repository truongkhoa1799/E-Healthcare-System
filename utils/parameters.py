import os
import yaml
import pathlib

show_fps = False
PROJECT_PATH = pathlib.Path().absolute()

class GlobalVariable:
    def __init__(self):
        self.main_thread = None

        # parameters for services
        self.gui = None
        self.timer = None
        self.camera = None
        self.server = None
        self.count_face = None
        self.face_recognition = None

        # flag init
        self.flg_init_GUI = False
        self.flg_init_timer = False
        self.flg_init_camera = False
        self.flg_init_count_face = False
        self.flg_server_connected = False
        self.flg_init_momo_assistant = False
        self.flg_init_face_recognition = False
        
        # Server para and timer parameters
        self.is_sending_message = False
        self.has_response_server = False
        self.lock_response_server = None
        self.has_examination_room = False
        # Timer
        # -1: none, 1 server
        self.turn = -1 

        # Parameters for face recognition
        self.img = None
        self.detected_face = None
        self.face_location = None
        self.embedded_face = None
        self.list_embedded_face = ""
        self.times_missing_face = 0

        # Parameter for connection of iot hub
        self.device_ID = None
        self.eventhub_name = None
        self.eventhub_connection = None
        self.device_iothub_connection = None

        # Parameters for new user
        self.list_embedded_face_new_user = ""
        # up : 0, down : 1, left : 2, right : 3, forward : 4
        self.num_face_new_user = 5
        self.current_shape = 0
        self.check_current_shape = False
        self.list_shape_face = ['Looking foward', 'Looking up', 'Looking down', 'Looking left', 'Looking right']
        self.dict_user_pose = {}
        self.num_user_pose = 0
        self.list_embedded_face_origin_new_patient = []

        self.list_examination_room = [
        {'dep_ID': 1, 'dep_name': 'Khoa noi', 'building_code': 'A1', 'room_code': '101'},
        {'dep_ID': 2, 'dep_name': 'Khoa ngoai', 'building_code': 'A1', 'room_code': '102'}, 
        {'dep_ID': 3, 'dep_name': 'Khoa tai mui hong', 'building_code': 'A1', 'room_code': '201'},
        {'dep_ID': 4, 'dep_name': 'Khoa Mat', 'building_code': 'B1', 'room_code': '101'}, 
        {'dep_ID': 5, 'dep_name': 'Khoa Than Kinh', 'building_code': 'B1', 'room_code': '201'},  
        {'dep_ID': 6, 'dep_name': 'Khoa Tim Mach', 'building_code': 'C1', 'room_code': '101'}, 
        {'dep_ID': 7, 'dep_name': 'Khoa San', 'building_code': 'C1', 'room_code': '201'}
        ]
        self.patient_ID = -1
        self.hospital_ID = None
        self.dep_ID_chosen = None
        # self.list_examination_room = []
        self.map_num_departments = {3: 17, 6: 8, 9: 5, 12: 4, 15:3, 18:2}
        self.return_stt = None
        self.valid_stt = None

        # Sensor
        self.measuring_sensor = False
        self.done_measuring_sensor = False

        ##############
        # assistant  #
        ##############
        # MOMO STATE
        self.ASSIS_FIRST_STATE = 1
        self.ASSIS_CHOOSE_DEP_STATE = 2
        self.ASSIS_DISPLAY_SYMPTON_STATE = 3
        self.ASSIS_CONFIRM_STATE = -1

        # used to map predicted department with current running dep in database
        self.momo_assis = None
        self.thread_assis = None
        self.lock_update_exam_room = None
        self.map_department_table = None

        self.assis_state = self.ASSIS_FIRST_STATE
        self.assis_pre_state = self.ASSIS_CONFIRM_STATE

        ############################
        # STATE of the program     #
        ############################
        self.STATE = 1
        self.ENABLE_PROGRAM_RUN = True
        self.START_RUN = False
        
        # STATES
        self.STATE_RECOGNIZE_PATIENT = 1
        self.STATE_CONFIRM_PATIENT = 2
        self.STATE_MEASURE_SENSOR = 3
        self.STATE_VIEW_DEPARTMENTS = 4
        self.STATE_CONFIRM_NEW_PATIENT = 5
        self.STATE_NEW_PATIENT = 6
        self.STATE_WAITING_SUB_EXAM = 7
        
        # Button
        self.button = -1
        # Button used to check when return message of submitting examination
        self.button_ok_pressed = True

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

        # request
        self.REQUEST_CONFIRM_NEW_PATIENT = 0
        self.REQUEST_CHANGE_GUI = 1
        self.REQUEST_UPDATE_PATIENT_INFO = 2
        self.REQUEST_CLEAR_PATIENT_INFO = 3
        self.REQUEST_ACTIVATE_NEW_FACE = 4
        self.REQUEST_UPDATE_EXAM_ROOM = 5
        self.REQUEST_CLEAR_EXAM_ROOM = 6
        self.REQUEST_UPDATE_DEPARTMENT_LIST = 9
        self.REQUEST_CLEAR_DEPARTMENT_LIST = 10
        self.REQUEST_UPDATE_SENSOR = 7
        self.REQUEST_CLEAR_SENSOR = 8
        self.REQUEST_MEASURE_SENSOR = 11
        self.REQUEST_NOTIFY_MESSAGE = 12
        self.REQUEST_DEACTIVATE_NEW_FACE = 13
        self.REQUEST_CLEAR_SELECTED_EXAM_ROOM = 14
        self.REQUEST_UPDATE_SELECTED_EXAM_ROOM = 15

        # Dialog
        self.EXIST_DIALOG = 0
        self.CONFIRM_PATIENT_DIALOG = 1
        self.CONFIRM_NEW_PATIENT_DIALOG = 2

        # PATH_PARA
        config_para_path = os.path.join(PROJECT_PATH, 'config_para.yaml')
        with open(config_para_path, 'r') as file:
            documents = yaml.load(file, Loader=yaml.FullLoader)

            # Momo assistant
            self.VOICE_PATH_FILE = os.path.join(PROJECT_PATH, str(documents['path']['voice_assis_path']))
            self.MAP_DEP_TABLE_PATH = os.path.join(PROJECT_PATH, str(documents['path']['map_dep_table_path']))
            self.DT_MODEL_PREDICT_DEP_PATH = os.path.join(PROJECT_PATH, str(documents['path']['decision_tree_model_predict_dep_path']))
            self.DICT_PART_BOD_PROBLEMS_PREDICT_DEP_PATH = os.path.join(PROJECT_PATH, str(documents['path']['dict_part_body_problems_predict_dep_path']))

            # Connection server
            self.CONNECTION_AZURE_PATH = os.path.join(PROJECT_PATH, str(documents['path']['azure_connection_path']))
            
            # Parameters for image processing, and KNN model
            self.IMAGE_SIZE = int(documents['preprocessing']['image_size'])
            self.BASE_BRIGHTNESS = int(documents['preprocessing']['base_brightness'])
            
            # identifying_face
            self.CYCLE_COUNT_FACE_PERIOD = int(documents['identifying_face']['cycle_count_face_period'])
            self.NUMBER_DETECTED_FACE_TRANSMITED = int(documents['identifying_face']['number_deteced_face_allowed'])
            # MAX length for HOG face Detector
            self.MAX_LENGTH_IMG = int(documents['identifying_face']['max_length_img'])
            self.MAX_EDGE = int(documents['identifying_face']['max_edge'])


            self.FACE_DETECTOR_MODEL = documents['identifying_face']['face_detector_model']
            self.SHAPE_PREDICTOR_MODEL = str(documents['identifying_face']['shape_predictor_model'])

            # FACE RECOGNITION MODEL
            self.PREDICTOR_5_POINT_MODEL = os.path.join(PROJECT_PATH, str(documents['path']['predictor_5_point_model']))
            self.PREDICTOR_68_POINT_MODEL = os.path.join(PROJECT_PATH, str(documents['path']['predictor_68_point_model']))
            self.CNN_FACE_DETECTOR = os.path.join(PROJECT_PATH, str(documents['path']['cnn_face_detector_model']))
            self.RESNET_MODEL = os.path.join(PROJECT_PATH, str(documents['path']['resnet_path']))

            # Display image
            self.CAMERA_DISPLAY_WIDTH = int(documents['camera']['camera_display_width'])
            self.CAMERA_DISPLAY_HEIGHT = int(documents['camera']['camera_display_height'])
            # 1920x1080, 30 fps
            self.SENSOR_MODE_1080 = int(documents['camera']['camera_mode_1080'])
            # 1280x720, 60 fps
            self.SENSOR_MODE_720 = int(documents['camera']['camera_mode_720'])

            # size for display patient
            self.LOCATION_RECOGNIZE_FACE_WIDTH = int(documents['gui']['location_recognize_face_width'])
            self.LOCATION_RECOGNIZE_FACE_HEIGHT = int(documents['gui']['location_recognize_face_height'])
            # size for displaying new patient
            self.LOCATION_ADD_FACE_WIDTH = int(documents['gui']['location_add_face_width'])
            self.LOCATION_ADD_FACE_HEIGHT = int(documents['gui']['location_add_face_height'])

            # Parameters for GUI
            self.WIDTH_GUI = int(documents['gui']['width_gui'])
            self.HEIGHT_GUI = int(documents['gui']['height_gui'])
            self.CAM_EXAM_LAYOUT_WIDTH = int(documents['gui']['cam_exam_layout_width'])
            self.CAM_EXAM_LAYOUT_HEIGHT = int(documents['gui']['cam_exam_layout_height'])
            self.INFOR_SENSOR_LAYOUT_WIDTH = int(documents['gui']['sensor_exam_layout_width'])
            self.INFOR_SENSOR_LAYOUT_HEIGHT = int(documents['gui']['sensor_exam_layout_height'])

            # Parameters for timer
            self.TIMES_MISSING_FACE = int(documents['timer']['times_missing_face'])
            self.TIMEOUT_MISSING_FACE = int(documents['timer']['timeout_missing_face'])

            self.TIMEOUT_VALIDATE = int(documents['timer']['timeout_validate'])
            self.OPT_TIMER_VALIDATE = int(documents['timer']['opt_timer_validate'])

            self.TIMEOUT_GET_EXAMINATION_ROOM = int(documents['timer']['timeout_get_examination_room'])
            self.OPT_TIMER_GET_EXAMINATION_ROOM = int(documents['timer']['opt_timer_get_examination_room'])

            self.TIMEOUT_SUBMIT_EXAMINATION = int(documents['timer']['timeout_submit_examination'])
            self.OPT_TIMER_SUBMIT_EXAMINATION = int(documents['timer']['opt_timer_submit_examination'])


        # load parameters for assistant
        with open(self.MAP_DEP_TABLE_PATH, 'r') as file:
            self.map_department_table = yaml.load(file, Loader=yaml.FullLoader)
        


    def ClearAssisPara(self):
        self.assis_state = self.ASSIS_FIRST_STATE
        self.assis_pre_state = self.ASSIS_CONFIRM_STATE

class User_Infor:
    def __init__(self):
        self.status = -1
        self.patient_ID = None
        self.user_info = None
        self.Clear()

    def Clear(self):
        self.status = -1
        self.user_info = None
        self.patient_ID = None
    
    def Update_Info(self, user_info):
        self.status = 0
        self.user_info = user_info
        self.patient_ID = user_info['user_ID']
    
class Sensor:
    def __init__(self):
        self.status = -1
        self.sensor_infor = None
        self.Clear()
    
    def Clear(self):
        self.status = -1
        self.sensor_infor = None
    
    def Update_Sensor(self, sensor):
        self.status = 0
        self.sensor_infor = sensor

class Examination:
    def __init__(self):
        self.status = -1
        self.__department = None
        self.__room = None
        self.__building = None
        self.Clear()
    
    def Clear(self):
        self.status = -1
        self.__department = ""
        self.__room = ""
        self.__building = ''
    
    def Update_Examination(self, dep, room):
        self.status = 0
        temp = room.split('-')
        
        self.__department = dep
        self.__building = temp[0]
        self.__room = temp[1]
    
    def Get_Exam_Room_Infor(self):
        return self.__department, self.__building, self.__room

glo_va = GlobalVariable()
user_infor = User_Infor()
sensor = Sensor()
exam = Examination()