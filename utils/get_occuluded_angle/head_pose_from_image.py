#!/usr/bin/env python3

import os
import cv2
import sys
import numpy as np

sys.path.append('/home/thesis/Documents/thesis/E-Healthcare-System')

from utils.get_occuluded_angle.drawFace import draw
import utils.get_occuluded_angle.reference_world as world

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

    noseEndPoints3D = np.array([[0, 0, 1000.0]], dtype=np.float64)
    noseEndPoint2D, jacobian = cv2.projectPoints(noseEndPoints3D, rotationVector, translationVector, cameraMatrix, mdists)

    # draw nose line 
    # p1 = (int(refImgPts[0, 0]), int(refImgPts[0, 1]))
    # p2 = (int(noseEndPoint2D[0, 0, 0]), int(noseEndPoint2D[0, 0, 1]))
    # cv2.line(im, p1, p2, (110, 220, 0), thickness=2, lineType=cv2.LINE_AA)

    # calculating angle
    rmat, jac = cv2.Rodrigues(rotationVector)
    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
    # print(f"Qx:{Qx}\tQy:{Qy}\tQz:{Qz}\t")
    # x = np.arctan2(Qx[2][1], Qx[2][2])
    # y = np.arctan2(-Qy[2][0], np.sqrt((Qy[2][1] * Qy[2][1] ) + (Qy[2][2] * Qy[2][2])))
    # z = np.arctan2(Qz[0][0], Qz[1][0])
    # print("AxisX: ", x)
    # print("AxisY: ", y)
    # print("AxisZ: ", z)


    # print("Angle x:{} angle y:{}".format(angles[0], angles[1]))
    sign_vertical = -1 if angles[0] < 0 else 1
    diff_vertical = 180 - abs(angles[0])

    sign_horizontal = -1 if angles[1] < 0 else 1
    diff_horizontal = abs(angles[1])

    # print('sign_v: {}, diff_v: {}, sign_h :{}, diff_h: {}'.format(sign_vertical, diff_vertical, sign_horizontal, diff_horizontal))


    if diff_horizontal < 5 and diff_vertical < 5:
        # Looking foward
        # print('front')
        return 0
    
    if sign_horizontal == -1:
        if diff_horizontal > 12 and diff_vertical < 5:
            # Looking left
            # print('left')
            return 3

    elif sign_horizontal == 1:
        if diff_horizontal > 12 and diff_vertical < 5:
            # Looking right
            # print('right')
            return 4

    if sign_vertical == -1:
        if diff_vertical > 5 and diff_horizontal < 5:
            # Looking down
            # print('down')
            return 2
    elif sign_vertical == 1:
        if diff_vertical > 15 and diff_horizontal < 5:
            # Looking up
            # print('up')
            return 1

    
    # if angles[0] < 0 and abs(angles[0]) < 177:
    #     if angles[1] <= 15 and angles[1] >= -15:
    #         # Looking Down
    #         return 2
    #     else:
    #         # None
    #         return -1
    # elif angles[0] > 0 and angles[0] < 167:
    #     if angles[1] <= 15 and angles[1] >= -15:
    #         # Looking UP
    #         return 1
    #     else:
    #         # None
    #         return -1
    
    # elif angles[0] <= -175 or angles[0] >= 175:
    #     if angles[1] < -15:
    #         # Looking Left
    #         return 3
    #     elif angles[1] > 15:
    #         # Looking Right
    #         return 4
    #     elif angles[1] <= 5 and angles[1] >= -5:
    #         # Looking Forward
    #         return 0

    return -1
    # print("Angle: ", angles)
    # print(gaze)
    # print('*' * 80)
        # cv2.putText(im, gaze, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 80), 2)
        # cv2.imshow("Head Pose", im)

