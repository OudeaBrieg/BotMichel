import sys
import numpy as np
from torch.nn import Tanh

from src.utils.misc import count_parameters

from rlgym.envs import Match
from rlgym.utils.action_parsers import DiscreteAction
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.vec_env import VecMonitor, VecNormalize, VecCheckNan
from stable_baselines3.ppo import MlpPolicy

from rlgym.utils.obs_builders import AdvancedObs
from src.state_staters.state import BetterRandom
from rlgym.utils.terminal_conditions.common_conditions import TimeoutCondition, NoTouchTimeoutCondition, GoalScoredCondition
from rlgym_tools.sb3_utils import SB3MultipleInstanceEnv
from rlgym.utils.reward_functions.common_rewards.player_ball_rewards import VelocityPlayerToBallReward
from rlgym.utils.reward_functions.common_rewards.ball_goal_rewards import VelocityBallToGoalReward
from src.rewards.botmichel_rewards import JumpTouchReward, SaveBoostReward
from rlgym.utils.reward_functions.common_rewards.misc_rewards import EventReward
from rlgym.utils.reward_functions import CombinedReward

# Checking for RLBot only-compatible Python 3.7.9
if sys.version_info[0] != 3 or sys.version_info[1] != 7 or sys.version_info[2] != 9:
    raise Exception("Must be using Python 3.7.9")


if __name__ == '__main__':  # Required for multiprocessing
    frame_skip = 8          # Number of ticks to repeat an action
    half_life_seconds = 5   # Easier to conceptualize, after this many seconds the reward discount is 0.5

    fps = 120 / frame_skip
    gamma = np.exp(np.log(0.5) / (fps * half_life_seconds))  # Quick mafs
    agents_per_match = 6        # 2 if 1v1, 4 if 2v2, 6 if 3v3
    num_instances = 1           # As many as you can handle
    target_steps = 1_000_000    # How many steps we want to train for each training session
    steps = target_steps // (num_instances * agents_per_match) # Making sure the experience counts line up properly
    batch_size = target_steps//10 # getting the batch size down to something more manageable - 100k in this case
    training_interval = 25_000_000
    mmr_save_frequency = 50_000_000

    def exit_save(model):
        model.save("models/bot_michel")

    def get_match():  # Need to use a function so that each instance can call it and produce their own objects
        return Match(
            team_size=3,
            tick_skip=frame_skip,
            reward_function=CombinedReward(
            (
                VelocityPlayerToBallReward(),
                VelocityBallToGoalReward(),
                SaveBoostReward(),
                #JumpTouchReward(),
                EventReward(
                    team_goal=100.0,
                    concede=-100.0,
                    shot=5.0,
                    save=30.0,
                    demo=10.0,
                    boost_pickup=5.0
                ),
            ),
            (0.1, 1.0, 1.0, 1.0)),
            # if rlgym < 1.2, 'self_play'=True instead of spawn_opponents=True
            spawn_opponents=True,
            terminal_conditions=[TimeoutCondition(fps * 300), NoTouchTimeoutCondition(fps * 45), GoalScoredCondition()],
            obs_builder=AdvancedObs(),  # Not that advanced, good default
            #state_setter=DefaultState(),  # Resets to kickoff position
            state_setter=BetterRandom(), #Resets to a random position
            action_parser=DiscreteAction()  # Discrete > Continuous don't @ me
        )

    env = SB3MultipleInstanceEnv(get_match, num_instances)            # Start num_instances instances, waiting 60 seconds between each
    env = VecCheckNan(env)                                # Optional
    env = VecMonitor(env)                                 # Recommended, logs mean reward and ep_len to Tensorboard
    env = VecNormalize(env, norm_obs=False, gamma=gamma)  # Highly recommended, normalizes rewards

    try:
        model = PPO.load(
            "models/bot_michel.zip",
            env,
            device="auto",
            custom_objects={"n_envs": env.num_envs}, #automatically adjusts to users changing instance count, may encounter shaping error otherwise
            # If you need to adjust parameters mid training, you can use the below example as a guide
            #custom_objects={"n_envs": env.num_envs, "n_steps": steps, "batch_size": batch_size, "n_epochs": 10, "learning_rate": 5e-5}
        )
        print("Loaded previous exit save.")
        total_params = count_parameters(model)
    except:
        print("No saved model found, creating new model.")
        policy_kwargs = dict(
            activation_fn=Tanh,
            net_arch=[512, 512, dict(pi=[256, 256, 256], vf=[256, 256, 256])],
        )

        model = PPO(
            MlpPolicy,
            env,
            n_epochs=10,                 # PPO calls for multiple epochs
            policy_kwargs=policy_kwargs,
            learning_rate=5e-5,          # Around this is fairly common for PPO
            ent_coef=0.01,               # From PPO Atari
            vf_coef=1.,                  # From PPO Atari
            gamma=gamma,                 # Gamma as calculated using half-life
            verbose=3,                   # Print out all the info as we're going
            batch_size=batch_size,             # Batch size as high as possible within reason
            n_steps=steps,                # Number of steps to perform before optimizing network
            tensorboard_log="logs",  # `python -m tensorboard.main --logdir=logs` in terminal to see graphs
            device="auto"                # Uses GPU if available
        )
        total_params = count_parameters(model)
        

    # Save model every so often
    # Divide by num_envs (number of agents) because callback only increments every time all agents have taken a step
    # This saves to specified folder with a specified name
    callback = CheckpointCallback(round(5_000_000 / env.num_envs), save_path="models", name_prefix="rl_model")

    try:
        mmr_model_target_count = model.num_timesteps + mmr_save_frequency
        while True:
            #may need to reset timesteps when you're running a different number of instances than when you saved the model
            model.learn(training_interval, callback=callback, reset_num_timesteps=False) #can ignore callback if training_interval < callback target
            model.save("models/bot_michel")
            if model.num_timesteps >= mmr_model_target_count:
                model.save(f"mmr_models/bot_michel_{model.num_timesteps}")
                mmr_model_target_count += mmr_save_frequency

    except KeyboardInterrupt:
        print("Exiting training")

    print("Saving model")
    exit_save(model)
    print("Save complete")
