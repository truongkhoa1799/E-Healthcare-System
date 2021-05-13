import cv2
import sys
import numpy as np

# from utils.get_occuluded_angle.drawFace import draw
import utils.get_occuluded_angle.reference_world as world
from utils.parameters import *

focal = 1.0

# forward : 0
# up : 1
# down : 2
# left : 3
# right : 4
def Get_Face_Angle(im, shape):
    face3Dmodel = world.ref3DModel()
    # draw(im, shape)
    refImgPts = world.ref2dImagePoints(shape)

    height, width, channel = im.shape
    focalLength = focal * width
    cameraMatrix = world.cameraMatrix(focalLength, (height / 2, width / 2))

    mdists = np.zeros((4, 1), dtype=np.float64)

    # calculate rotation and translation vector using solvePnP
    success, rotationVector, translationVector = cv2.solvePnP(
        face3Dmodel, refImgPts, cameraMatrix, mdists)

    # noseEndPoints3D = np.array([[0, 0, 1000.0]], dtype=np.float64)
    # noseEndPoint2D, jacobian = cv2.projectPoints(noseEndPoints3D, rotationVector, translationVector, cameraMatrix, mdists)

    # calculating angle
    rmat, jac = cv2.Rodrigues(rotationVector)
    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

    # print("Angle x:{} angle y:{}".format(angles[0], angles[1]))
    sign_vertical = -1 if angles[0] < 0 else 1
    diff_vertical = 180 - abs(angles[0])

    sign_horizontal = -1 if angles[1] < 0 else 1
    diff_horizontal = abs(angles[1])

    # print('sign_v: {}, diff_v: {} '.format(sign_vertical, diff_vertical))
    # print('\tsign_h :{}, diff_h: {}'.format(sign_horizontal, diff_horizontal))

    if glo_va.current_shape == 0:
        if diff_horizontal < glo_va.check_pose[glo_va.current_shape][3] \
            and diff_vertical < glo_va.check_pose[glo_va.current_shape][1]:
            return True
        else:
            return False
    
    elif glo_va.current_shape == 1 or glo_va.current_shape == 2:
        if sign_vertical == glo_va.check_pose[glo_va.current_shape][0] \
            and diff_horizontal < glo_va.check_pose[glo_va.current_shape][3] \
            and diff_vertical >= glo_va.check_pose[glo_va.current_shape][1]:
            return True
        else:
            return False
    
    elif glo_va.current_shape == 3 or glo_va.current_shape == 4:
        if sign_horizontal == glo_va.check_pose[glo_va.current_shape][2] \
            and diff_horizontal >= glo_va.check_pose[glo_va.current_shape][3] \
            and diff_vertical < glo_va.check_pose[glo_va.current_shape][1]:
            return True
        else:
            return False

    # if diff_horizontal < 7 and diff_vertical < 7:
    #     # Looking foward
    #     # print('front')
    #     return 0
    
    # if sign_horizontal == -1:
    #     if diff_horizontal >= 5 and diff_vertical < 7:
    #         # Looking left
    #         # print('left')
    #         return 3

    # elif sign_horizontal == 1:
    #     if diff_horizontal >= 5 and diff_vertical < 7:
    #         # Looking right
    #         # print('right')
    #         return 4

    # if sign_vertical == -1:
    #     if diff_vertical >= 5 and diff_horizontal < 7:
    #         # Looking down
    #         # print('down')
    #         return 2

    # elif sign_vertical == 1:
    #     if diff_vertical > 7 and diff_horizontal < 7:
    #         # Looking up
    #         # print('up')
    #         return 1

    # return -1

