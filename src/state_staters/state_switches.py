import numpy as np
import random

# Computing Distance from Car to Ball
def difficulty_distance(difficulty,
                        th_arr=[-200, -1024, 1984, -2944]):
    def distance_easy():
        dist_min, dist_max = th_arr[0], th_arr[1]
        return np.random.uniform(dist_min, dist_max)
    def distance_medium():
        dist_min, dist_max = th_arr[1], th_arr[2]
        return np.random.uniform(dist_min, dist_max)
    def distance_hard():
        dist_min, dist_max = th_arr[2], th_arr[3]
        return np.random.uniform(dist_min, dist_max)
    def distance_default():
        dist_min, dist_max = th_arr[0], th_arr[3]
        return np.random.uniform(dist_min, dist_max)
    distance_switch = {
        0: distance_easy,
        1: distance_medium,
        2: distance_hard
    }
    return distance_switch.get(difficulty, distance_default)()

# Computing Yaw angle from Car to Ball
def difficulty_yaw(difficulty,
                   fw_bw,
                   coeff_arr=[0.15, 0.325, 0.5]):
    rot_threshold = random.random() - 0.5
    def yaw_easy():
        return (rot_threshold) * (np.pi * coeff_arr[0]) + fw_bw
    def yaw_medium():
        return (rot_threshold) * (np.pi * coeff_arr[1]) + fw_bw
    def yaw_hard():
        return (rot_threshold) * (np.pi * coeff_arr[2]) + fw_bw
    def yaw_default():
        return (rot_threshold) * (np.pi * coeff_arr[2]) + fw_bw
    yaw_switch = {
        0: yaw_easy,
        1: yaw_medium,
        2: yaw_hard
    }
    return yaw_switch.get(difficulty, yaw_default)()