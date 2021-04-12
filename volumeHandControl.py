import cv2
import time
import numpy as np
import handTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


##################################
wCam, hCam = 640, 480
cTime, pTime = 0, 0
##################################
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

devices = AudioUtilities.GetSpeakers()
# devices = AudioUtilities.GetAllDevices()

interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(0, None)
volMin = volRange[0]
volMax = volRange[1]
vol = 0
volBar = 400
volPer = 0


detector = htm.handDetector(detectionCon=0.7)

while True:

    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    # print(lmList)
    if len(lmList) != 0:
        # landmark values cna be found on https://google.github.io/mediapipe/solutions/hands
        # print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        length = math.hypot((x2 - x1), (y2 - y1))
        # print(length)

        if(length <= 50):
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

        # hand length 50 -300
        # volume range -63.5 - 0

        vol = np.interp(length, [50, 300], [volMin, volMax])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])

        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

    cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 0, 255), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (50, 430), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)

    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow('Img', img)
    cv2.waitKey(1)

