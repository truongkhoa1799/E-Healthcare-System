#######################################################################################
# Define parameters                                                                   #
#######################################################################################
# model_engine
# USER INFORMATION
PATH_USER_IMG_ENCODED = "/Users/khoa1799/GitHub/E-Healthcare-System/model_engine/Encoded_Face"
PATH_USER_ID = "/Users/khoa1799/GitHub/E-Healthcare-System/model_engine/ID_Face"

# KNN MODEL
KNN_MODEL_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System/model_engine/knn_clf_model.clf"

# FACE RECOGNITION MODEL
CENTER_FACE_TRT_PATH = '/Users/khoa1799/GitHub/E-Healthcare-System/model_engine/face_detector_320_192.trt'
PREDICTOR_5_POINT_MODEL = '/Users/khoa1799/GitHub/E-Healthcare-System/model_engine/shape_predictor_5_face_landmarks.dat'
RESNET_MODEL = '/Users/khoa1799/GitHub/E-Healthcare-System/model_engine/dlib_face_recognition_resnet_model_v1.dat'

# Data
FACE_TEST_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System/Data/test"
FACE_TRAIN_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System/Data/train"
DATA_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System/Face/"

SAVING_IMG_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System/TEST_FACE/Test"
SAVING_IMGDetec_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System/TEST_FACE/Detect"

# Connection server
IOT_HUB_CONNECTION = "HostName=E-HealthCare.azure-devices.net;SharedAccessKeyName=ServerRight;SharedAccessKey=coR5OV6uuuBPCxSriI7DibJsw+XiCb6255cONqZ6JWg="
CONNECTION_LIST_PATH = "/Users/khoa1799/GitHub/E-Healthcare-System/communicate_server/connection"
RESPONSE_IOTHUB_CONNECTION = "HostName=E-HealthCare.azure-devices.net;DeviceId={};SharedAccessKey={}"

PATIENT_FILE = 'Patients.json'

# Parameters for image processing, and KNN model
IMAGE_SIZE = 150
BASE_BRIGHTNESS = 180
THRESHOLD_FACE_REC = 0.5
NUM_JITTERS = 1
NUM_NEIGHBROS = 3
KNN_ALGORITHM = 'ball_tree'
KNN_WEIGHTS = 'distance'

CYCLE_COUNT_FACE_PERIOD = 2.0
THRESHOLD_PATIENT_REC = 20
# Good for 1280x720
DISPLAY_WIDTH=640
DISPLAY_HEIGHT=360

LOCATION_FACE_WIDTH = 300
LOCATION_FACE_HEIGHT = 360

# image for center face
SCALE_WIDTH=320
SCALE_HEIGHT=192

# For 1920x1080
# DISPLAY_WIDTH=960
# DISPLAY_HEIGHT=540

# 1920x1080, 30 fps
SENSOR_MODE_1080=2
# 1280x720, 60 fps
SENSOR_MODE_720=3

time_detecting = 0
time_identifying = 0
time_read_frame = 0

class GlobalVariable:
    def __init__(self):
        self.gui = None
        self.camera = None
        self.STATE = 0
        self.img = None
        self.display_image = None
        self.window_GUI = None
        self.face_detector = None
        self.cuda_ctx = None
        self.face_location = None
        self.face_identifying = None
        self.embedded_face = None
        self.patient_id = None
        self.count_face = None

        # flag init
        self.flg_init_count_face = False
        self.flg_init_GUI = False
        self.flg_init_camera = False
        self.flg_init_face_detector = False

        # IOT hub, event hub connection
        self.device_ID = None
        self.device_iothub_connection = None
        self.eventhub_connection = None
        self.eventhub_name = None

        # Encoded Image
        self.list_encoded_img = ""

        # Identifying User flag
        self.has_response_server = False
        self.producer = None

glo_va = GlobalVariable()