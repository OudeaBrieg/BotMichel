import numpy as np
from stable_baselines3 import PPO
import pathlib
from src.parsers.discrete_act import DiscreteAction


class Agent:
    def __init__(self):
        _path = pathlib.Path(__file__).parent.resolve()
        model_name = "bot_michel"
        custom_objects = {
            "lr_schedule": 0.000001,
            "clip_range": .02,
            "n_envs": 1,
        }
        # Should modify 'cpu' to 'gpu' when possible
        self.actor = PPO.load(str(_path) + '/models/' + model_name, device='cuda', custom_objects=custom_objects)
        self.parser = DiscreteAction()


    def act(self, state):
        action = self.actor.predict(state, deterministic=True)
        x = self.parser.parse_actions(action[0], state)
        return x[0]

if __name__ == "__main__":
    print("You're doing it wrong.")
