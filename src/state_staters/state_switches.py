import numpy as np
import random
from src.utils.common_values import BALL_RADIUS, OCTANE_LENGTH, SUPERSONIC_THRESHOLD

# Getting Distance from Car to Ball
def get_difficulty_distance(difficulty,
                            th_arr=[1024, 1984, 2944]):
    min_distance = BALL_RADIUS + OCTANE_LENGTH + 42
    max_distance = th_arr[-1]
    def no_distance():
        return min_distance
    def distance_easy():
        return np.random.uniform(min_distance, th_arr[0])
    def distance_medium():
        return np.random.uniform(th_arr[0], th_arr[1])
    def distance_hard():
        return np.random.uniform(th_arr[1], max_distance)
    def distance_default():
        return np.random.uniform(min_distance, max_distance)
    distance_switch = {
        0: no_distance,
        1: distance_easy,
        2: distance_medium,
        3: distance_hard
    }
    return distance_switch.get(difficulty, distance_default)()

# Getting Yaw angle from Car to Ball
def get_difficulty_car_yaw(difficulty,
                           distance,
                           fw_bw,
                           th_arr=[0.15, 0.325, 0.5]):
    min_yaw = np.arctan(BALL_RADIUS / distance)
    max_yaw = th_arr[-1]                   
    side = 1 if random.random() < 0.5 else -1
    def no_yaw():
        return side * (np.pi * np.random.uniform(0, min_yaw)) + fw_bw
    def yaw_easy():
        return side * (np.pi * np.random.uniform(min_yaw, th_arr[0])) + fw_bw
    def yaw_medium():
        return side * (np.pi * np.random.uniform(th_arr[0], th_arr[1])) + fw_bw
    def yaw_hard():
        return side * (np.pi * np.random.uniform(th_arr[1], max_yaw)) + fw_bw
    def yaw_default():
        return side * (np.pi * np.random.uniform(0, max_yaw)) + fw_bw
    yaw_switch = {
        0: no_yaw,
        1: yaw_easy,
        2: yaw_medium,
        3: yaw_hard
    }
    return yaw_switch.get(difficulty, yaw_default)()

# Getting Car Initial Speed
def get_difficulty_car_speed(difficulty,
                             fw_bw,
                             th_arr=[705, 1410]):
    speed_min = 0
    speed_max = SUPERSONIC_THRESHOLD
    side = 1 if fw_bw == 0 else -1
    def no_speed():
        return side * speed_min
    def speed_easy():
        return side * np.random.randint(th_arr[0]) 
    def speed_medium():
        return side * np.random.randint(th_arr[0], th_arr[1])
    def speed_hard():
        return side * np.random.randint(th_arr[1], speed_max)
    def speed_default():
        return side * np.random.randint(speed_max)
    speed_switch = {
        0: no_speed,
        0: speed_easy,
        1: speed_medium,
        2: speed_hard
    }
    return speed_switch.get(difficulty, speed_default)()