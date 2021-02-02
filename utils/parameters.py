#######################################################################################
# Define parameters                                                                   #
#######################################################################################
# model_engine
PATH_USER_IMG_ENCODED = "/home/thesis/Documents/E-Healthcare-System/model_engine/Encoded_Face"
PATH_USER_ID = "/home/thesis/Documents/E-Healthcare-System/model_engine/ID_Face"
KNN_MODEL_PATH = "/home/thesis/Documents/E-Healthcare-System/model_engine/knn_clf_model.clf"
CENTER_FACE_TRT_PATH = '/home/thesis/Documents/E-Healthcare-System/model_engine/face_detector_320_192.trt'
PREDICTOR_5_POINT_MODEL = '/home/thesis/Documents/E-Healthcare-System/model_engine/shape_predictor_5_face_landmarks.dat'
RESNET_MODEL = '/home/thesis/Documents/E-Healthcare-System/model_engine/dlib_face_recognition_resnet_model_v1.dat'

# Data
FACE_TEST_PATH = "/home/thesis/Documents/E-Healthcare-System/Data/test"
FACE_TRAIN_PATH = "/home/thesis/Documents/E-Healthcare-System/Data/train"
DATA_PATH = "/home/thesis/Documents/E-Healthcare-System/Face/"

SAVING_IMG_PATH = "/home/thesis/Documents/E-Healthcare-System/TEST_FACE/Test"
SAVING_IMGDetec_PATH = "/home/thesis/Documents/E-Healthcare-System/TEST_FACE/Detect"


PATIENT_FILE = 'Patients.json'

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
MIN_FACE_AREA = 60000

# image for center face
SCALE_WIDTH=320
SCALE_HEIGHT=192

# 1920x1080, 30 fps
SENSOR_MODE_1080=2
# 1280x720, 60 fps
SENSOR_MODE_720=3

time_detecting = 0
time_identifying = 0
time_read_frame = 0

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
        self.face_identifier = None
        self.face_detector = None

        self.img = None
        self.face_location = None
        self.embedded_face = None

        # flag init
        self.flg_init_count_face = False
        self.flg_init_GUI = False
        self.flg_init_camera = False
        self.flg_init_face_detector = False

glo_va = GlobalVariable()