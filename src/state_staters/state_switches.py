import numpy as np

# Computing Distance from Car to Ball
def difficulty_distance(difficulty):
    def distance_easy():
        y_min, y_max = -200, -1024
        return np.random.uniform(y_min, y_max)
    def distance_medium():
        y_min, y_max = -1024, -1984
        return np.random.uniform(y_min, y_max)
    def distance_hard():
        y_min, y_max = -1984, -2944
        return np.random.uniform(y_min, y_max)
    def distance_default():
        y_min, y_max = -200, -2944
        return np.random.uniform(y_min, y_max)
    distance_switch = {
        0: distance_easy,
        1: distance_medium,
        2: distance_hard
    }
    return distance_switch.get(difficulty, distance_default)()