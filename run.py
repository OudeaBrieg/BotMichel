import sys, os
import shutil
import argparse
from argparse import RawTextHelpFormatter
import numpy as np

from src.utils.misc import count_parameters
from src.environment.terminal_conditions import BallTouchedCondition
from src.state_staters.state import DistanceState
from src.rewards.botmichel_rewards import TouchBallReward

from torch.nn import Tanh
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.vec_env import VecMonitor, VecNormalize, VecCheckNan
from stable_baselines3.ppo import MlpPolicy

from rlgym.envs import Match
from rlgym.utils.action_parsers import DiscreteAction
from rlgym.utils.obs_builders import AdvancedObs
from rlgym.utils.terminal_conditions.common_conditions import TimeoutCondition
from rlgym.utils.reward_functions.common_rewards.player_ball_rewards import VelocityPlayerToBallReward
from rlgym.utils.terminal_conditions.common_conditions import TimeoutCondition
from rlgym.utils.reward_functions import CombinedReward

from rlgym_tools.sb3_utils import SB3MultipleInstanceEnv

# Checking for RLBot only-compatible Python 3.7.9
if sys.version_info[0] != 3 or sys.version_info[1] != 7 or sys.version_info[2] != 9:
    raise Exception("Must be using Python 3.7.9")


if __name__ == '__main__':  # Required for multiprocessing
    parser = argparse.ArgumentParser(
        description=f'Personalized Gym for training PPO-based Rocket League Reinforcement \
                      Learning Agents (e.g. : a Dojo for Rocket-powered Soccer playing \
                      Vehicles).',
        formatter_class=RawTextHelpFormatter)

    # In-Game Metadata
    parser.add_argument('-agents_per_match', type=int, default=1,
                        help='Number of Agents per Instance\n' + \
                             '(1 if solo, 2 if 1v1, 4 if 2v2, 6 if 3v3)')
    parser.add_argument('-spawn_opponents', type=bool, default=False,
                        help='Enabling opponents to spawn')
    parser.add_argument('-team_size', type=int, default=1,
                        help='Number of Agents per Team\n' + \
                             '(1 if solo, 2 if twos, 3 if threes)')
    
    # Training Session Parameters
    parser.add_argument('-num_instances', type=int, default=1,
                        help='Number of Training Instances to be run in parallel')
    parser.add_argument('-device', type=str, default='auto',
                        help='Device (cpu, cuda, ...) on which the code should be run\n' + \
                             '(Setting it to auto, the code will run on GPU if possible)')
    parser.add_argument('-frame_skip', type=int, default=8,
                        help='Number of Ticks to repeat an action')
    parser.add_argument('-half_life_seconds', type=int, default=5,
                        help='Number of Seconds until Half-life\n' + \
                             '(After this many seconds the reward discount is 0.5)')
    parser.add_argument('-env_type', type=str, default="distance",
                        help='Which Training environment to set up')
    parser.add_argument('-difficulty', type=int, default=0,
                        help='Training Chosen Environment Difficulty')
    parser.add_argument('-episode_len', type=int, default=10,
                        help='Maximum episode length (in seconds)')

    # Model Hyperparameters
    parser.add_argument('-learning_rate', type=float, default=5e-5,
                        help='The Learning Rate\n' + \
                             '(Around 5e-5 is fairly common for PPO)')
    parser.add_argument('-target_steps', type=int, default=1_000_000,
                        help='Number of Steps we want to train for each training session\n' + \
                             '(Represents 10 times the batch size)')
    parser.add_argument('-n_epochs', type=int, default=10,
                        help='Number of epoch when optimizing the surrogate loss\n' + \
                             '(PPO recommmends multiple epochs)')
    parser.add_argument('-ent_coef', type=float, default=0.01,
                        help='Entropy coefficient for the loss calculation\n' + \
                             '(PPO Atari recommmends setting it to 0.01)')
    parser.add_argument('-v_coef', type=float, default=1.,
                        help='Value function coefficient for the loss calculation\n' + \
                             '(PPO Atari recommmends setting it to 1)')

    # Saving Paths
    parser.add_argument('-model_path', type=str, default='models',
                        help='Relative Path to save the Trained Model')
    parser.add_argument('-model_name', type=str, default='bot_michel',
                        help='Name of the Model')
    parser.add_argument('-logs_path', type=str, default='logs',
                        help='`python -m tensorboard.main --logdir=your-path` at the root.')
    parser.add_argument('-clear_models', type=bool, default=False,
                        help='Enables clearing of all models in model_path')
    parser.add_argument('-clear_logs', type=bool, default=False,
                        help='Enables clearing of all logs in logs_path')
    
    args = parser.parse_args()

    frame_skip = args.frame_skip                # Number of ticks to repeat an action
    half_life_seconds = args.half_life_seconds  # Easier to conceptualize, after this many seconds the reward discount is 0.5

    fps = 120 / frame_skip
    gamma = np.exp(np.log(0.5) / (fps * half_life_seconds))     # Quick mafs
    agents_per_match = args.agents_per_match                    # 2 if 1v1, 4 if 2v2, 6 if 3v3
    num_instances = args.num_instances                          # As many as you can handle
    target_steps = args.target_steps                            # How many steps we want to train for each training session
    steps = target_steps // (num_instances * agents_per_match)  # Making sure the experience counts line up properly
    batch_size = target_steps//10                               # Getting the batch size down to something more manageable - 100k in this case
    training_interval = 25_000_000
    mmr_save_frequency = 50_000_000
    model_save_path = f"{args.model_path}/{args.model_name}.zip"
    physics_ticks_per_second = 120
    ep_len_seconds = args.episode_len
    max_steps = int(round(ep_len_seconds * physics_ticks_per_second / frame_skip))

    def exit_save(model, path):
        model.save(path)
    
    def clear_folder(path):
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    
    if args.clear_models:
        print(f"Clearing all models in {args.model_path}")
        clear_folder(args.model_path)
        print(f"Cleared {args.model_path}")
    if args.clear_logs:
        print(f"Clearing all logs in {args.logs_path}")
        clear_folder(args.logs_path)
        print(f"Cleared {args.logs_path}")

    # Need to use a function, so that each instance can call it and produce their own objects
    def get_match():  
        return Match(
            team_size=args.team_size,
            tick_skip=frame_skip,
            reward_function=CombinedReward(
            (
                VelocityPlayerToBallReward(),
                TouchBallReward(),
                #TODO :
            ),
            (1.0, 1.0)),
            spawn_opponents=args.spawn_opponents,
            terminal_conditions=[TimeoutCondition(max_steps), BallTouchedCondition()],
            #terminal_conditions=[TimeoutCondition(fps * 300), NoTouchTimeoutCondition(fps * 45), GoalScoredCondition()],
            obs_builder=AdvancedObs(),      # Not that advanced, good default
            state_setter=DistanceState(env_type=args.env_type,
                                       difficulty=args.difficulty,
                                       give_boost=False),
            action_parser=DiscreteAction()  # Discrete > Continuous don't @ me
        )

    env = SB3MultipleInstanceEnv(get_match,
                                 num_instances,             # Start num_instances instances 
                                 wait_time=20)              # Waiting 20 seconds between each
    env = VecCheckNan(env)                                  # Optional
    env = VecMonitor(env)                                   # Recommended, logs mean reward and ep_len to Tensorboard
    env = VecNormalize(env, norm_obs=False, gamma=gamma)    # Highly recommended, normalizes rewards

    try:
        model = PPO.load(model_save_path,
                         env,
                         device="auto",
                         custom_objects={"n_envs": env.num_envs}, # Automatically adjusts to users changing instance count, may encounter shaping error otherwise
                         # If you need to adjust parameters mid training, you can use the below example as a guide
                         # custom_objects={"n_envs": env.num_envs, "n_steps": steps, "batch_size": batch_size, "n_epochs": 10, "learning_rate": 5e-5}
        )
        model._last_obs = None
        print(f"Loaded previous exit save : {model_save_path}")
    except:
        print(f"No saved model found, creating new model : {model_save_path}")
        policy_kwargs = dict(
            activation_fn=Tanh,
            net_arch=[512, 512, dict(pi=[256, 256, 256], vf=[256, 256, 256])],
        )

        model = PPO(
            MlpPolicy,
            env,
            n_epochs=args.n_epochs,               # PPO calls for multiple epochs
            policy_kwargs=policy_kwargs,
            learning_rate=args.learning_rate,     # Around this is fairly common for PPO
            ent_coef=args.ent_coef,               # From PPO Atari
            vf_coef=args.v_coef,                  # From PPO Atari
            gamma=gamma,                          # Gamma as calculated using half-life
            verbose=3,                            # Print out all the info as we're going
            batch_size=batch_size,                # Batch size as high as possible within reason
            n_steps=steps,                        # Number of steps to perform before optimizing network
            tensorboard_log=args.logs_path,       # `python -m tensorboard.main --logdir=logs` in terminal to see graphs
            device=args.device                    # Uses GPU if available
        )        

    # Save model every so often
    # Divide by num_envs (number of agents) because callback only increments every time all agents have taken a step
    # This saves to specified folder with a specified name
    callback = CheckpointCallback(round(5_000_000 / env.num_envs), save_path=args.model_path, name_prefix="rl_model")

    try:
        mmr_model_target_count = model.num_timesteps + mmr_save_frequency
        while True:
            #may need to reset timesteps when you're running a different number of instances than when you saved the model
            model.learn(training_interval, callback=callback, reset_num_timesteps=False) #can ignore callback if training_interval < callback target
            model.save(model_save_path)
            if model.num_timesteps >= mmr_model_target_count:
                model.save(f"mmr_models/{args.model_name}_{model.num_timesteps}")
                mmr_model_target_count += mmr_save_frequency

    except KeyboardInterrupt:
        print("Exiting training")

    print("Saving model")
    exit_save(model, model_save_path)
    print(f"Save complete : {model_save_path}")
