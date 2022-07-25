import cv2 as cv
import sys
import cv2
import math
import time
import numpy as np
import Board
import yaml_handle
import ActionGroups as AGC
import threading
from math import *
import Camera
import start_door
import time

debug = False
stage = []
stage_num = 0
stage_type = 0
stage_name = ""
size = (640, 480)


def initMove():  # 初始化机器人位置
    Board.setPWMServoPulse(1, servo_data['servo1'], 500)
    Board.setPWMServoPulse(2, servo_data['servo2'], 500)


def load_config():
    global lab_data, servo_data
    lab_data = yaml_handle.get_yaml_data(yaml_handle.lab_file_path)
    servo_data = yaml_handle.get_yaml_data(yaml_handle.servo_file_path)


def init():
    print("Ready to go")
    load_config()
    initMove()


__isRunning = False


# 变量重置
def reset():
    global stage
    global stage_num
    global stage_type
    stage_num = 0
    stage_type = 1  # 设置赛道顺序
    stage = [start_door, 'hole', 'landmine', 'baffle', 'mid_door', 'bridge', 'kick_ball', 'stair', 'end_door'], \
            ['start_door', 'bridge', 'landmine', 'baffle', 'mid_door', 'hole', 'kick_ball', 'stair', 'end_door']  # 关卡顺序


# 启动机器人
def start():
    global __isRunning
    reset()
    __isRunning = True
    print("Robot go")


# 机器人停止
def stop():
    global __isRunning
    __isRunning = False
    print("Robot Stop")


# 退出
def exit():
    global __isRunning
    __isRunning = False
    AGC.runActionGroup('stand_slow')
    print("Exit")


if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

if __name__ == '__main__':
    from CalibrationConfig import *

    # 加载参数
    param_data = np.load(calibration_param_path + '.npz')

    # 获取参数
    mtx = param_data['mtx_array']
    dist = param_data['dist_array']
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (640, 480), 0, (640, 480))
    mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (640, 480), 5)

    # 相机标定
    debug = False
    if debug:
        print('Debug Mode')

    # 启动
    init()
    start()
    my_camera = Camera.Camera()
    my_camera.camera_open()
    AGC.runActionGroup('stand')

    # 循环每一帧
while stage_num < 9:
    while True:
        img = my_camera.frame
        if img is not None:

            # 矫正及缩放
            frame = img.copy()
            frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)  # 畸变矫正
            border = cv.copyMakeBorder(frame, 12, 12, 16, 16, borderType=cv.BORDER_CONSTANT,
                                       value=(255, 255, 255))  # 扩展白边，防止边界无法识别
            read_img = cv.resize(border, (size[1], size[0]), interpolation=cv.INTER_CUBIC)  # 图片缩放 320，240

            print('Stage ', stage[stage_type][stage_num], " start")

            # 运行关卡函数
            rdy = stage[stage_type][stage_num].run(read_img)

            # 返回值为1时说明该关卡已完成
            if rdy:
                print('Stage ', stage[stage_type][stage_num], ' done in ', 'second')
                stage_num = stage_num + 1

            time.sleep(0.01)
        else:
            print('image is empty')
            time.sleep(0.5)

        my_camera.camera_close()
        cv2.destroyAllWindows()
print('Win!')
