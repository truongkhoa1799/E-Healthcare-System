import os
import re
import cv2
import pickle
import pycuda.driver as cuda
from models.face_identifier import FaceIdentifier 

LIST_CUT_FACE_PATH = "/home/thesis/Documents/FRCheckInSystem/src/Cut-Face/"
EMBEDDED_FACE = "/home/thesis/Documents/FRCheckInSystem/src/EMBEDDED_FACE/embedded_face"
NAME_FACE = "/home/thesis/Documents/FRCheckInSystem/src/EMBEDDED_FACE/name_face"

global known_face_encodings
global known_face_IDs

def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

def SaveData():
    with open(NAME_FACE, mode='wb') as fp_1:
        pickle.dump(known_face_IDs, fp_1)
    
    with open(EMBEDDED_FACE, 'wb') as fp_2:
        pickle.dump(known_face_encodings, fp_2)

def LoadData():
    global known_face_encodings
    global known_face_IDs
    if not os.path.exists(NAME_FACE):
        print("There is no user id face to load")
        exit(-1)

    with open (NAME_FACE, 'rb') as fp_1:
        known_face_IDs = pickle.load(fp_1)

    if not os.path.exists(EMBEDDED_FACE):
        print("There is no user encoding face to load")
        exit(-1)

    with open (EMBEDDED_FACE, 'rb') as fp_2:
        known_face_encodings = pickle.load(fp_2)

if __name__ == "__main__":
    global known_face_encodings
    global known_face_IDs
    known_face_encodings = []
    known_face_IDs = []

    # print('TrtThread: loading the TRT model...')
    # cuda_ctx = cuda.Device(0).make_context()  # GPU 0
    # iden = FaceIdentifier()
    # print('TrtThread: start running...')

    # for class_dir in os.listdir(LIST_CUT_FACE_PATH):
    #     if not os.path.isdir(os.path.join(LIST_CUT_FACE_PATH, class_dir)):
    #         continue

    #     # Loop through each training image for the current person and past image path for encoing individualy
    #     for img in image_files_in_folder(os.path.join(LIST_CUT_FACE_PATH, class_dir)):
    #         path = img.split('/')
    #         user_ID = path[-2]
    #         img_name = path[-1]

    #         loaded_img = cv2.imread( img )
    #         resized_img = cv2.resize(loaded_img, (224,224))

    #         embedded_face = iden(resized_img)

    #         known_face_encodings.append(embedded_face)
    #         known_face_IDs.append(user_ID)

    #         SaveData()

    # del iden
    # cuda_ctx.pop()
    # del cuda_ctx

    LoadData()
    print(known_face_IDs)