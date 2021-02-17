#######################################################################################
# Define parameters                                                                   #
#######################################################################################

# FACE RECOGNITION MODEL
CENTER_FACE_TRT_PATH = '/home/thesis/Documents/E-Healthcare-System/model_engine/face_detector_320_192.trt'
PREDICTOR_5_POINT_MODEL = '/home/thesis/Documents/E-Healthcare-System/model_engine/shape_predictor_5_face_landmarks.dat'
RESNET_MODEL = '/home/thesis/Documents/E-Healthcare-System/model_engine/dlib_face_recognition_resnet_model_v1.dat'

# Connection server
IOT_HUB_CONNECTION = "HostName=E-HealthCare.azure-devices.net;SharedAccessKeyName=ServerRight;SharedAccessKey=coR5OV6uuuBPCxSriI7DibJsw+XiCb6255cONqZ6JWg="
CONNECTION_LIST_PATH = "/home/thesis/Documents/E-Healthcare-System/communicate_server/connection"
RESPONSE_IOTHUB_CONNECTION = "HostName=E-HealthCare.azure-devices.net;DeviceId={};SharedAccessKey={}"

# Parameters for image processing, and KNN model
IMAGE_SIZE = 150
BASE_BRIGHTNESS = 180

# Count Face
CYCLE_COUNT_FACE_PERIOD = 1.5
NUMBER_DETECTED_FACE_TRANSMITED = 20

# Display image
CAMERA_DISPLAY_WIDTH=640
CAMERA_DISPLAY_HEIGHT=360
# DISPLAY_WIDTH=1280
# DISPLAY_HEIGHT=720

# 1920x1080, 30 fps
SENSOR_MODE_1080=2
# 1280x720, 60 fps
SENSOR_MODE_720=3

# size for display
LOCATION_FACE_WIDTH = 300
LOCATION_FACE_HEIGHT = 360

# Min are to encoding
MIN_FACE_AREA = 40000

# MAX length for HOG face Detector
MAX_LENGTH_IMG = 80

# # image for center face
# SCALE_WIDTH=320
# SCALE_HEIGHT=192

show_fps = True

class GlobalVariable:
    def __init__(self):
        self.camera = None

        # Parameters for GUI
        self.gui = None
        self.display_image = None
        self.window_GUI = None
        self.patient_id = None

        # STATE of the program
        self.STATE = 0

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

        # flag init
        self.flg_init_count_face = False
        self.flg_init_GUI = False
        self.flg_init_camera = False
        self.flg_init_face_detector = False
        self.flg_server_connected = False
        self.flg_init_face_recognition = False

        # Server para
        self.has_response_server = False
        self.server = None

        self.device_ID = None
        self.device_iothub_connection = None
        self.eventhub_connection = None
        self.eventhub_name = None

class User_Infor:
    def __init__(self):
        self.name = None
        self.birthday = None
        self.phone = None
        self.address = None
        self.Init()
    
    def Init(self):
        self.name = "None"
        self.birthday = "None"
        self.phone = "None"
        self.address = "None"

glo_va = GlobalVariable()
user_infor = User_Infor()