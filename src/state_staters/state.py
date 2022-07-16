from shutil import register_unpack_format
import numpy as np
import random
from rlgym.utils import StateSetter
from rlgym.utils.state_setters import StateWrapper
from rlgym.utils.math import rand_vec3

from rlgym.utils.common_values import CAR_MAX_SPEED, SIDE_WALL_X, BACK_WALL_Y, CEILING_Z, BALL_RADIUS, CAR_MAX_ANG_VEL, \
    BALL_MAX_SPEED

LIM_X = SIDE_WALL_X - 1152 / 2 - BALL_RADIUS * 2 ** 0.5
LIM_Y = BACK_WALL_Y - 1152 / 2 - BALL_RADIUS * 2 ** 0.5
LIM_Z = CEILING_Z - BALL_RADIUS

PITCH_LIM = np.pi / 2
YAW_LIM = np.pi
ROLL_LIM = np.pi

GOAL_X_MAX = 800.0
GOAL_X_MIN = -800.0

PLACEMENT_BOX_X = 5000
PLACEMENT_BOX_Y = 2000
PLACEMENT_BOX_Y_OFFSET = 3000

GOAL_LINE = 5100

YAW_MAX = np.pi

class DistanceState(StateSetter):  # Random state with some triangular distributions
    def __init__(self,
                 env_type: str = "distance",
                 difficulty: int = 0,
                 cars_on_ground: bool = True, 
                 ball_on_ground: bool = True,
                 give_boost: bool = False):
        super().__init__()
        self.env_type = env_type
        self.difficulty = difficulty
        self.cars_on_ground = cars_on_ground
        self.ball_on_ground = ball_on_ground
        self.give_boost = give_boost

    def reset(self, state_wrapper: StateWrapper):
        def difficulty_distance(difficulty):
            def distance_easy():
                return np.random.uniform(-128, -1024)
            def distance_medium():
                return np.random.uniform(-1024, -1984)
            def distance_hard():
                return np.random.uniform(-1984, -2944)
            def distance_default():
                return np.random.uniform(-128, -2944)
            distance_switch = {
                0: distance_easy,
                1: distance_medium,
                2: distance_hard
            }
            return distance_switch.get(difficulty, distance_default)()

        # Ball Initialization
        if self.ball_on_ground:
            state_wrapper.ball.set_pos(0, 0, 0)     # Set Ball Position
        else:
            state_wrapper.ball.set_pos(0, 0, np.random.uniform(90, 642)) # Set Ball Position
        state_wrapper.ball.set_lin_vel(0, 0, 0)     # Set Ball Linear Velocity
        state_wrapper.ball.set_ang_vel(0, 0, 0)     # Set Ball Angular Velocity
        
        # Cars Initialization
        for car in state_wrapper.cars:
            distance = difficulty_distance(self.difficulty)   # Computing Distance from Car to Ball
            if self.cars_on_ground:
                car_height = 0 
            else:
                car_height = np.random.uniform(90, 642)
            car.set_pos(0, distance, car_height)
                

            yaw_treshold = (random.random() - 0.5) * (np.pi * 0.15)
            car.set_rot(0, (np.pi/2) + yaw_treshold, 0) # Set Car Rotation at (0, pi/2 +th, 0)
            
            car.set_lin_vel(0, 0, 0)                    # Set Car Linear Velocity to (0, 0, 0)
            car.set_ang_vel(0, 0, 0)                    # Set Car Angular Velocity to (0, 0, 0)
            
            if self.give_boost:
                car.boost = np.random.uniform(0.12, 1.00)
            else:
                car.boost = 0

    

    

    