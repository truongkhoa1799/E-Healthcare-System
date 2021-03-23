import os
import sys
import yaml
import pathlib

show_fps = True
PROJECT_PATH = pathlib.Path().absolute()

class GlobalVariable:
    def __init__(self):
        self.camera = None

        # Parameters for GUI
        self.gui = None
        self.display_image = None
        self.window_GUI = None
        self.examination_GUI = None

        # STATE of the program
        self.STATE = 1

        # self.cuda_ctx = None

        self.count_face = None

        # face recognition
        # self.face_detector = None
        self.face_recognition = None

        # Parameters for face recognition
        self.img = None
        self.detected_face = None
        self.face_location = None
        self.embedded_face = None
        self.list_embedded_face = ""
        self.times_missing_face = 0
        self.validation_id = None

        # flag init
        self.flg_init_count_face = False
        self.flg_init_GUI = False
        self.flg_init_camera = False
        self.flg_init_face_detector = False
        self.flg_server_connected = False
        self.flg_init_face_recognition = False
        self.flg_init_timer = False

        # Server para
        self.has_response_server = False
        self.server = None
        self.is_sending_message = False

        self.device_ID = None
        self.device_iothub_connection = None
        self.eventhub_connection = None
        self.eventhub_name = None


        # Parameters for new user
        self.list_embedded_face_new_user = ""
        self.embedded_face_new_user = None
        self.num_images_new_user = 0
        self.has_capture = False
        # up : 0, down : 1, left : 2, right : 3, forward : 4
        self.num_face_new_user = 5
        self.current_shape = 0
        self.user_pose = None
        self.list_shape_face = ['Looking up', 'Looking down', 'Looking left', 'Looking right', 'Looking foward']

        self.lock_response_server = None
        self.lock_timer_expir = False

        # Timer
        self.timer = None
        self.timer_expir = False
        self.current_timer_id_validation = None
        # -1: none, 1 server
        self.turn = -1 

        # Examination Room
        self.has_examination_room = False
        # self.list_examination_room = [
        # {'dep_ID': 1, 'dep_name': 'Khoa noi', 'building_code': 'A1', 'room_code': '101'},
        # {'dep_ID': 2, 'dep_name': 'Khoa ngoai', 'building_code': 'A1', 'room_code': '102'}, 
        # {'dep_ID': 3, 'dep_name': 'Khoa tai mui hong', 'building_code': 'A1', 'room_code': '201'},
        # {'dep_ID': 4, 'dep_name': 'Khoa Mat', 'building_code': 'B1', 'room_code': '101'}, 
        # {'dep_ID': 5, 'dep_name': 'Khoa Than Kinh', 'building_code': 'B1', 'room_code': '201'},  
        # {'dep_ID': 6, 'dep_name': 'Khoa Tim Mach', 'building_code': 'C1', 'room_code': '101'}, 
        # {'dep_ID': 7, 'dep_name': 'Khoa San', 'building_code': 'C1', 'room_code': '201'}
        # ]
        self.list_examination_room = []
        self.map_num_departments = {3: 17, 6: 8, 9: 5, 12: 4, 15:3, 18:2}
        self.hospital_ID = None
        self.dep_ID_chosen = None
        self.patient_ID = None
        self.return_stt = None

        # Sensor
        self.has_sensor_values = False
        self.measuring_sensor = False

        # PATH_PARA
        config_para_path = os.path.join(PROJECT_PATH, 'config_para.yaml')
        with open(config_para_path, 'r') as file:
            documents = yaml.load(file, Loader=yaml.FullLoader)
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
            self.RESNET_MODEL = os.path.join(PROJECT_PATH, str(documents['path']['resnet_path']))

            # Display image
            self.CAMERA_DISPLAY_WIDTH = int(documents['camera']['camera_display_width'])
            self.CAMERA_DISPLAY_HEIGHT = int(documents['camera']['camera_display_height'])
            # 1920x1080, 30 fps
            self.SENSOR_MODE_1080 = int(documents['camera']['camera_mode_1080'])
            # 1280x720, 60 fps
            self.SENSOR_MODE_720 = int(documents['camera']['camera_mode_720'])

            # size for display
            self.LOCATION_FACE_WIDTH = int(documents['gui']['location_face_width'])
            self.LOCATION_FACE_HEIGHT = int(documents['gui']['location_face_height'])

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
            
            # STATES
            self.STATE_NEW_PATIENT = int(documents['state']['state_new_patient'])
            # print(self.CONNECTION_AZURE_PATH)
            # print(self.IMAGE_SIZE)
            # print(self.BASE_BRIGHTNESS)
            # print(self.CYCLE_COUNT_FACE_PERIOD)
            # print(self.NUMBER_DETECTED_FACE_TRANSMITED)
            # print(self.MAX_LENGTH_IMG)
            # print(self.PREDICTOR_5_POINT_MODEL)
            # print(self.RESNET_MODEL)
            # print(self.CAMERA_DISPLAY_WIDTH)
            # print(self.CAMERA_DISPLAY_HEIGHT)
            # print(self.SENSOR_MODE_1080)
            # print(self.SENSOR_MODE_720)
            # print(self.LOCATION_FACE_WIDTH)
            # print(self.LOCATION_FACE_HEIGHT)
            # print(self.WIDTH_GUI)
            # print(self.HEIGHT_GUI)
            # print(self.CAM_EXAM_LAYOUT_WIDTH)
            # print(self.CAM_EXAM_LAYOUT_HEIGHT)
            # print(self.INFOR_SENSOR_LAYOUT_WIDTH)
            # print(self.INFOR_SENSOR_LAYOUT_HEIGHT)
            # print(self.TIMES_MISSING_FACE)
            # print(self.TIMEOUT_MISSING_FACE)
            # print(self.TIMEOUT_VALIDATE)
            # print(self.OPT_TIMER_VALIDATE)
            # print(self.TIMEOUT_GET_EXAMINATION_ROOM)
            # print(self.OPT_TIMER_GET_EXAMINATION_ROOM)
            # print(self.TIMEOUT_SUBMIT_EXAMINATION)
            # print(self.OPT_TIMER_SUBMIT_EXAMINATION)



class User_Infor:
    def __init__(self):
        self.__status = -1
        self.__name = None
        self.__birthday = None
        self.__phone = None
        self.__address = None
        self.patient_ID = None
        self.Clear()

    def Clear(self):
        self.__status = -1
        self.__name = "None"
        self.__birthday = "None"
        self.__phone = "None"
        self.__address = "None"
        self.patient_ID = None
    
    def Update_Info(self, user_info):
        self.__status = 0
        self.__name = user_info['name']
        self.__birthday = user_info['birthday']
        self.__phone = user_info['phone']
        self.__address = user_info['address']
        self.patient_ID = user_info['user_ID']

    def Update_Screen(self):
        glo_va.window_GUI['-NAME-'].update(str(self.__name))
        glo_va.window_GUI['-BD-'].update(str(self.__birthday))
        glo_va.window_GUI['-PHONE-'].update(str(self.__phone))
        glo_va.window_GUI['-ADDRESS-'].update(str(self.__address))
    
    def Get_Status(self):
        return self.__status
    
class Sensor:
    def __init__(self):
        self.__blood_pressure = None
        self.__pulse = None
        self.__thermal = None
        self.__spo2 = None
        self.Clear()
    
    def Clear(self):
        self.__blood_pressure = "None"
        self.__pulse = "None"
        self.__thermal = "None"
        self.__spo2 = "None"
    
    def Update_Sensor(self, sensor):
        self.__blood_pressure = sensor['blood_pressure']
        self.__pulse = sensor['pulse']
        self.__thermal = sensor['thermal']
        self.__spo2 = sensor['spo2']
    
    def Update_Screen(self):
        glo_va.window_GUI['-BLOOD_PRESSURE-'].update(str(self.__blood_pressure))
        glo_va.window_GUI['-PULSE-'].update(str(self.__pulse))
        glo_va.window_GUI['-THERMAL-'].update(str(self.__thermal))
        glo_va.window_GUI['-SPO2-'].update(str(self.__spo2))
    
    def Get_Data(self):
        return self.__blood_pressure, self.__pulse, self.__thermal, self.__spo2

class Examination:
    def __init__(self):
        self.__department = None
        self.__room = None
        self.Clear()
    
    def Clear(self):
        self.__department = "None"
        self.__room = "None"
    
    def Update_Examination(self, exam):
        self.__department = exam['dep']
        self.__room = exam['room']
    
    def Update_Screen(self):
        glo_va.window_GUI['-DEPARTMENT-'].update(str(self.__department))
        glo_va.window_GUI['-ROOM-'].update(str(self.__room))
    
    def Get_Buidling_Room(self):
        temp = self.__room.split('-')
        return temp[0], temp[1]
    
    def Get_Room(self):
        return self.__room

glo_va = GlobalVariable()
user_infor = User_Infor()
sensor = Sensor()
exam = Examination()