from shutil import register_unpack_format
import numpy as np
import random
from rlgym.utils import StateSetter
from rlgym.utils.state_setters import StateWrapper

from src.state_staters.state_switches import difficulty_yaw

from rlgym.utils.common_values import BALL_RADIUS

# State Setter for the Distance Environment
class YawState(StateSetter):
    def __init__(self,
                 env_type: str = "yaw",
                 difficulty: int = 0,
                 fw_bw_chance: float = 0.1,
                 boost_chance: float = 0.1,
                 distance: float = 1024):
        super().__init__()
        self.env_type = env_type
        self.difficulty = difficulty
        self.fw_bw_chance = fw_bw_chance
        self.boost_chance = boost_chance
        self.distance = distance

    def reset(self, state_wrapper: StateWrapper):
        # Ball Initialization
        state_wrapper.ball.set_pos(0, 0, 0)
        state_wrapper.ball.set_lin_vel(0, 0, 0)
        state_wrapper.ball.set_ang_vel(0, 0, 0)     
        
        # Cars Initialization
        fw_bw = np.pi if random.random() < self.fw_bw_chance else 0
        boost = np.random.uniform(0.12, 1.00) if random.random() < self.boost_chance else 0
        car_yaw = difficulty_yaw(self.difficulty, fw_bw)
        for car in state_wrapper.cars:
            # Mirroring the cars according to the respective team 
            sign = 1 if car.team_num == 0 else -1
            # Set Car Position
            car.set_pos(0, self.distance * sign, 0)
            # Set Car Rotation
            face_ball = (np.pi / 2) * sign
            car.set_rot(0, face_ball + car_yaw, 0)
            # Set Car Velocity
            car.set_lin_vel(0, 0, 0)            
            car.set_ang_vel(0, 0, 0)
            # Set Car Boost
            car.boost = boost    