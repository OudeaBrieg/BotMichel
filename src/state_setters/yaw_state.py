import numpy as np
import random
from rlgym.utils import StateSetter
from rlgym.utils.state_setters import StateWrapper

from src.state_setters.state_switches import get_difficulty_distance, get_difficulty_car_yaw, \
                                             get_difficulty_car_speed
from src.utils.misc import compute_angle
from src.utils.common_values import BALL_RADIUS, OCTANE_MIN_SPAWN_HEIGHT

# State Setter for the Yaw Environment
class YawState(StateSetter):
    def __init__(self,
                 difficulty: int = 0,
                 fw_bw_chance: float = 0.1,
                 boost_chance: float = 0.9):
        super().__init__()
        self.difficulty = difficulty
        self.fw_bw_chance = fw_bw_chance
        self.boost_chance = boost_chance

    def reset(self, state_wrapper: StateWrapper):
        fw_bw = np.pi if random.random() < self.fw_bw_chance else 0
        boost = np.random.uniform(0.12, 1.00) if random.random() < self.boost_chance else 0
        n = len(state_wrapper.cars)
        # Ball Initialization at center of the field
        state_wrapper.ball.set_pos(0, 0, BALL_RADIUS)
        state_wrapper.ball.set_lin_vel(0, 0, 0)
        state_wrapper.ball.set_ang_vel(0, 0, 0)
        # Cars Initialization
        car_distance = get_difficulty_distance(0)
        car_yaw = get_difficulty_car_yaw(self.difficulty, car_distance, fw_bw)
        car_speed = get_difficulty_car_speed(0, fw_bw)
        for k, car in enumerate(state_wrapper.cars):
            y = car_distance * np.sin((k * 2 * np.pi) / n)
            x = car_distance * np.cos((k * 2 * np.pi) / n)
            # Set Car Position
            car.set_pos(x, y, OCTANE_MIN_SPAWN_HEIGHT)
            # Set Car Rotation
            car_face_ball_angle = compute_angle(x, y)
            final_yaw = car_face_ball_angle + car_yaw
            car.set_rot(0, final_yaw, 0)
            # Set Car Velocity
            car_lin_x = car_speed * np.cos(final_yaw)
            car_lin_y = car_speed * np.sin(final_yaw)
            car.set_lin_vel(car_lin_x, car_lin_y, 0)
            car.set_ang_vel(0, 0, 0)
            # Set Car Boost
            car.boost = boost