import numpy as np
import random
from rlgym.utils import StateSetter
from rlgym.utils.state_setters import StateWrapper

from src.state_staters.state_switches import get_difficulty_yaw, MIN_OCTANE_HEIGHT
from src.utils.misc import compute_angle

from rlgym.utils.common_values import BALL_RADIUS

# State Setter for the Distance Environment
class YawState(StateSetter):
    def __init__(self,
                 env_type: str = "yaw",
                 difficulty: int = 0,
                 fw_bw_chance: float = 0.1,
                 boost_chance: float = 0.9,
                 distance: float = 1024):
        super().__init__()
        self.env_type = env_type
        self.difficulty = difficulty
        self.fw_bw_chance = fw_bw_chance
        self.boost_chance = boost_chance
        self.distance = distance

    def reset(self, state_wrapper: StateWrapper):
        fw_bw = np.pi if random.random() < self.fw_bw_chance else 0
        boost = np.random.uniform(0.12, 1.00) if random.random() < self.boost_chance else 0
        # Ball Initialization at center of the field
        state_wrapper.ball.set_pos(0, 0, 0)
        state_wrapper.ball.set_lin_vel(0, 0, 0)
        state_wrapper.ball.set_ang_vel(0, 0, 0)
        # Cars Initialization
        car_yaw = get_difficulty_yaw(self.difficulty, fw_bw)
        n = len(state_wrapper.cars)
        for k, car in enumerate(state_wrapper.cars):
            y = self.distance * np.sin((k * 2 * np.pi) / n)
            x = self.distance * np.cos((k * 2 * np.pi) / n)
            # Set Car Position
            car.set_pos(x, y, MIN_OCTANE_HEIGHT)
            # Set Car Rotation
            car_face_ball_angle = compute_angle(x, y)
            car.set_rot(0, car_face_ball_angle + car_yaw, 0)
            # Set Car Velocity
            car.set_lin_vel(0, 0, 0)
            car.set_ang_vel(0, 0, 0)
            # Set Car Boost
            car.boost = boost