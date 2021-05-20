# MIT License
# Copyright (c) 2019 JetsonHacks
# See license
# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import sys
sys.path.append('/home/thesis/Documents/thesis/E-Healthcare-System')
import cv2
import time
import numpy as np

from identifying_users.face_recognition import Face_Recognition
# from identifying_users.face_detector_centerface import FaceDetector
# import pycuda.driver as cuda

# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Defaults to 1280x720 @ 60fps
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of the window on the screen


def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


if __name__ == "__main__":
    # cuda_ctx = cuda.Device(0).make_context()  # GPU 0
    # detector = FaceDetector()
    cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    face_rec = Face_Recognition()
    count = 0
    list_time = []

    # cap = cv2.VideoCapture(0)
    if cap.isOpened():
        window_handle = cv2.namedWindow("CSI Camera", cv2.WINDOW_AUTOSIZE)
        # Window
        while cv2.getWindowProperty("CSI Camera", 0) >= 0:
            time_start = time.time()
            ret_val, img = cap.read()
            # img = cv2.resize(img, (640,360))

            fra = 80 / max(img.shape[0], img.shape[1])
            resized_img = cv2.resize(img, (int(img.shape[1] * fra), int(img.shape[0] * fra)))
            GRAY_resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
            face_locations = face_rec.Get_Face_Locations(GRAY_resized_img)
            # glo_va.list_time_detection.append(time.time() - start_detec)

            if len(face_locations) == 0:
                continue

            try:
                for face_location in face_locations:
                    top = int(face_location[0] / fra)
                    bottom = int(face_location[2] / fra)
                    left = int(face_location[3] / fra)
                    right = int(face_location[1] / fra)

                    cv2.rectangle(img, (left, top), (right, bottom) , (2, 255, 0), 2)
            except:
                continue
            
            # dets = detector(img, img.shape[0], img.shape[1])
            # # print(dets)
            # for det in dets:
            #     boxes = det[:4]
            #     left = int(boxes[0])
            #     top = int(boxes[1])
            #     right = int(boxes[2])
            #     bottom = int(boxes[3])

            #     diff_vertical = bottom - top
            #     diff_horizontal = right - left
            #     diff = abs(int((diff_vertical - diff_horizontal) / 2))
            #     if diff_horizontal < diff_vertical:
            #         top += diff
            #         bottom -= diff
            #     else:
            #         left += diff
            #         right -= diff

            #     cv2.rectangle(img, (left, top), (right, bottom) , (2, 255, 0), 2)

            cv2.imshow("CSI Camera", img)
            # This also acts as
            keyCode = cv2.waitKey(30) & 0xFF
            # Stop the program on the ESC key
            if keyCode == 27 or count == 1500:
                print("Mean time: {}".format(np.mean(list_time)))
                print("Max time: {}".format(np.max(list_time)))
                print("Min time: {}".format(np.min(list_time)))
                print("Std time: {}".format(np.std(list_time)))
                break
            
            diff_time = time.time() - time_start
            if diff_time < 0.1:
                list_time.append(diff_time)
                count += 1
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Unable to open camera")
    # cuda_ctx.pop()
    # del cuda_ctx
