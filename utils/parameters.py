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
CYCLE_COUNT_FACE_PERIOD = 2.0
THRESHOLD_PATIENT_REC = 15

# Display image
DISPLAY_WIDTH=640
DISPLAY_HEIGHT=360

# size for display
LOCATION_FACE_WIDTH = 300
LOCATION_FACE_HEIGHT = 360

# Min are to encoding
MIN_FACE_AREA = 60000

# image for center face
SCALE_WIDTH=320
SCALE_HEIGHT=192

# 1920x1080, 30 fps
SENSOR_MODE_1080=2
# 1280x720, 60 fps
SENSOR_MODE_720=3

class GlobalVariable:
    def __init__(self):
        self.camera = None

        self.gui = None
        self.display_image = None
        self.window_GUI = None
        self.patient_id = None

        self.STATE = 0

        self.cuda_ctx = None

        self.count_face = None

        # face recognition
        self.face_detector = None
        self.face_encoder = None

        self.img = None
        self.img_located = None
        self.face_location = None
        self.embedded_face = None

        # flag init
        self.flg_init_count_face = False
        self.flg_init_GUI = False
        self.flg_init_camera = False
        self.flg_init_face_detector = False
        self.flg_server_connected = False

        # Encoded Image
        self.list_encoded_img = ""

        # Server para
        self.has_response_server = False
        self.server = None

        self.device_ID = None
        self.device_iothub_connection = None
        self.eventhub_connection = None
        self.eventhub_name = None

glo_va = GlobalVariable()