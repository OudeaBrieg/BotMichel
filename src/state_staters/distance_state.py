import numpy as np
import random
from rlgym.utils import StateSetter
from rlgym.utils.state_setters import StateWrapper

from src.state_staters.state_switches import get_difficulty_distance

from rlgym.utils.common_values import BALL_RADIUS

# State Setter for the Distance Environment
class DistanceState(StateSetter):
    def __init__(self,
                 env_type: str = "distance",
                 difficulty: int = 0,
                 fw_bw_chance: float = 0.1,
                 boost_chance: float = 0.1):
        super().__init__()
        self.env_type = env_type
        self.difficulty = difficulty
        self.fw_bw_chance = fw_bw_chance
        self.boost_chance = boost_chance

    def reset(self, state_wrapper: StateWrapper):
        fw_bw = np.pi if random.random() < self.fw_bw_chance else 0
        boost = np.random.uniform(0.12, 1.00) if random.random() < self.boost_chance else 0
        # Ball Initialization at center of the field
        state_wrapper.ball.set_pos(0, 0, 0)
        state_wrapper.ball.set_lin_vel(0, 0, 0)
        state_wrapper.ball.set_ang_vel(0, 0, 0)
        # Cars Initialization
        distance = get_difficulty_distance(self.difficulty)
        car_rot_th = np.arctan(BALL_RADIUS / distance)
        rot_threshold = random.random() - 0.5
        yaw_treshold = (rot_threshold) * (np.pi * car_rot_th) + fw_bw
        for car in state_wrapper.cars:
            # Mirroring the cars according to the respective team
            sign = 1 if car.team_num == 0 else -1
            # Set Car Position
            car.set_pos(0, distance * sign, 0)
            # Set Car Rotation
            car_face_ball = (np.pi / 2) * sign
            car.set_rot(0, car_face_ball + yaw_treshold, 0)
            # Set Car Velocity
            car.set_lin_vel(0, 0, 0)
            car.set_ang_vel(0, 0, 0)
            # Set Car Boost
            car.boost = boost