import sys, os
import shutil
import argparse
import configparser
from argparse import RawTextHelpFormatter
import numpy as np

from src.utils.misc import clear_folder, estimate_supported_processes
from src.environment.terminal_conditions import BallTouchedCondition
from src.state_setters.multistate_weighted import WeightedSampleSetter
from src.state_setters.state_dojo import DojoState
from src.state_setters.distance_state import DistanceState
from src.state_setters.yaw_state import YawState
from src.rewards.botmichel_rewards import TouchBallReward, VelocityPlayerToBallReward

from torch.nn import Tanh
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.vec_env import VecMonitor, VecNormalize, VecCheckNan
from stable_baselines3.ppo import MlpPolicy

from rlgym.envs import Match
from rlgym.utils.action_parsers import DiscreteAction
from rlgym.utils.obs_builders import AdvancedObs
from rlgym.utils.terminal_conditions.common_conditions import TimeoutCondition
from rlgym.utils.reward_functions import CombinedReward

from rlgym_tools.sb3_utils import SB3MultipleInstanceEnv

# Checking for RLBot only-compatible Python 3.7.9
if sys.version_info[0] != 3 or sys.version_info[1] != 7 or sys.version_info[2] != 9:
    raise Exception("Must be using Python 3.7.9")

if __name__ == '__main__':  # Required for multiprocessing
    here = os.path.realpath('.')
    parser = argparse.ArgumentParser(
        description=f'Personalized Gym for training PPO-based Rocket League Reinforcement \
                      Learning Agents (e.g. : a Dojo for Rocket-powered Soccer playing \
                      Vehicles).',
        formatter_class=RawTextHelpFormatter)
    config = configparser.ConfigParser(defaults = {'here': here})
    # Load from Configuration File
    parser.add_argument('-config_file', type=str, default='',
                        help='Path to Configuration File to load the Parameters from')
    # In-Game Metadata
    parser.add_argument('-agents_per_match', type=int, default=6,
                        help='Number of Agents per Instance\n' + \
                             '(1 if solo, 2 if 1v1, 4 if 2v2, 6 if 3v3)')
    parser.add_argument('-team_size', type=int, default=3,
                        help='Number of Agents per Team\n' + \
                             '(1 if solo, 2 if twos, 3 if threes)')
    parser.add_argument('-spawn_opponents', type=bool, default=True,
                        help='Enabling opponents to spawn')
    
    # Training Session Parameters
    parser.add_argument('-num_instances', type=int, default=1,
                        help='Number of Training Instances to be run in parallel')
    parser.add_argument('-wait_time', type=int, default=20,
                        help='Time to wait between each instance start')
    parser.add_argument('-device', type=str, default='auto',
                        help='Device (cpu, cuda, ...) on which the code should be run\n' + \
                             '(Setting it to auto, the code will run on GPU if possible)')
    parser.add_argument('-frame_skip', type=int, default=8,
                        help='Number of Ticks to repeat an action')
    parser.add_argument('-half_life_seconds', type=int, default=5,
                        help='Number of Seconds until Half-life\n' + \
                             '(After this many seconds the reward discount is 0.5)')
    # Environment Parameters
    parser.add_argument('-difficulty_levels', type=lambda s: [int(item) for item in s.split(',')],
                        default=[1, 1, 1],
                        help='Selecting Difficulties for the Training Environment (format="diffficulty_0,diffficulty_1,,...weight_n")')
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
    parser.add_argument('-model_name', type=str, default='',
                        help='Name of the Model')
    parser.add_argument('-logs_path', type=str, default='logs',
                        help='`python -m tensorboard.main --logdir=your-path` at the root.')
    parser.add_argument('-clear_models', type=bool, default=False,
                        help='Enables clearing of all models in model_path')
    parser.add_argument('-clear_logs', type=bool, default=False,
                        help='Enables clearing of all logs in logs_path')
    args = parser.parse_args()
    if len(args.config_file):
        print(f'Reading configuration from {args.config_file}')
        config.read(args.config_file)
        def parse_all_args(args, config):
            args.agents_per_match = int(config["METADATA"]["agents_per_match"])
            args.team_size = int(config["METADATA"]["team_size"])
            args.spawn_opponents = config.getboolean("METADATA", "spawn_opponents")
            args.num_instances = int(config["TRAININGSESSION"]["num_instances"])
            args.wait_time = int(config["TRAININGSESSION"]["wait_time"])
            args.device = str(config["TRAININGSESSION"]["device"])
            args.frame_skip = int(config["TRAININGSESSION"]["frame_skip"])
            args.half_life_seconds = int(config["TRAININGSESSION"]["half_life_seconds"])
            args.difficulty_levels = [float(level) for level in str(config["ENVIRONMENT"]["difficulty_levels"]).split(',')]
            args.episode_len = int(config["ENVIRONMENT"]["episode_len"])
            args.learning_rate = float(config["MODEL"]["learning_rate"])
            args.target_steps = int(config["MODEL"]["target_steps"])
            args.n_epochs = int(config["MODEL"]["n_epochs"])
            args.ent_coef = float(config["MODEL"]["ent_coef"])
            args.v_coef = float(config["MODEL"]["v_coef"])
            args.logs_path = str(config["SAVELOAD"]["logs_path"])
            args.model_path = str(config["SAVELOAD"]["model_path"])
            args.model_name = str(config["SAVELOAD"]["model_name"])
            args.clear_models = config.getboolean("SAVELOAD", "clear_models")
            args.clear_logs = config.getboolean("SAVELOAD", "clear_logs")
        parse_all_args(args, config)

    frame_skip = args.frame_skip                # Number of ticks to repeat an action
    half_life_seconds = args.half_life_seconds  # Easier to conceptualize, after this many seconds the reward discount is 0.5
    fps = 120 / frame_skip
    gamma = np.exp(np.log(0.5) / (fps * half_life_seconds))     # Quick mafs
    agents_per_match = args.agents_per_match                    # 2 if 1v1, 4 if 2v2, 6 if 3v3
    num_instances = args.num_instances                          # As many as you can handle
    target_steps = args.target_steps                            # How many steps we want to train for each training session
    n_steps = target_steps // (num_instances * agents_per_match)# Making sure the experience counts line up properly
    batch_size = target_steps//10                               # Getting the batch size down to something more manageable - 100k in this case
    training_interval = 25_000_000
    mmr_save_frequency = 50_000_000
    model_save_path = f"{args.model_path}/{args.model_name}.zip"
    physics_ticks_per_second = 120
    ep_len_seconds = args.episode_len
    max_steps = int(round(ep_len_seconds * physics_ticks_per_second / frame_skip))

    def exit_save(model, path):
        model.save(path)
    
    if args.clear_models:
        clear_folder(args.model_path)
    if args.clear_logs:
        clear_folder(args.logs_path)

    # Need to use a function, so that each instance can call it and produce their own objects
    def get_match():  
        return Match(
            team_size=args.team_size,
            tick_skip=frame_skip,
            reward_function=CombinedReward(
            (
                VelocityPlayerToBallReward(use_scalar_projection=True),
                TouchBallReward(),
            ), (1.0, 1.0)),
            spawn_opponents=args.spawn_opponents,
            terminal_conditions=[TimeoutCondition(max_steps), BallTouchedCondition()],
            obs_builder=AdvancedObs(),
            state_setter=WeightedSampleSetter([DojoState(difficulty_list = {
                                                            "distance" : args.difficulty_levels[0],
                                                            "car_yaw" : args.difficulty_levels[1],
                                                            "car_speed" : args.difficulty_levels[2]
                                                        })],
                                              [1.0]),
            action_parser=DiscreteAction()  # Discrete > Continuous
        )

    print(f"Estimation for max CPU instances in parallel : {estimate_supported_processes()}")
    env = SB3MultipleInstanceEnv(get_match,
                                 num_instances,             # Start num_instances instances 
                                 wait_time=args.wait_time)  # Waiting some time between each
    env = VecCheckNan(env)                                  # Optional
    env = VecMonitor(env)                                   # Recommended, logs mean reward and ep_len to Tensorboard
    env = VecNormalize(env, norm_obs=False, gamma=gamma)    # Highly recommended, normalizes rewards
    # If a model with that name exists, load it
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
    # If no model with that name exists/could not load, create it
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
            n_steps=n_steps,                        # Number of steps to perform before optimizing network
            tensorboard_log=args.logs_path,       # `python -m tensorboard.main --logdir=logs` in terminal to see graphs
            device=args.device                    # Uses GPU if available
        )        

    # Callback defines saving model strategy every so often
    callback = CheckpointCallback(round(5_000_000 / env.num_envs), save_path=args.model_path, name_prefix=args.model_name)
    try:
        mmr_model_target_count = model.num_timesteps + mmr_save_frequency
        while True:
            model.learn(training_interval, callback=callback, reset_num_timesteps=True) #can ignore callback if training_interval < callback target
            model.save(model_save_path)
            if model.num_timesteps >= mmr_model_target_count:
                model.save(f"mmr_models/{args.model_name}_{model.num_timesteps}")
                mmr_model_target_count += mmr_save_frequency
    except KeyboardInterrupt:
        print("Exiting training")

    print("Saving model")
    exit_save(model, model_save_path)
    print(f"Save complete : {model_save_path}")
