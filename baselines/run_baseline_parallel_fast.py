from os.path import exists
from pathlib import Path
import socket
import uuid
import time
import os
import re
from red_gym_env import RedGymEnv
from stable_baselines3 import PPO
from stable_baselines3.common import env_checker
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, DummyVecEnv
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
from tensorboard_callback import TensorboardCallback
from stream_agent_wrapper import StreamWrapper

def make_env(rank, env_conf, seed=0):
    """
    Utility function for multiprocessed env.
    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the initial seed for RNG
    :param rank: (int) index of the subprocess
    """

    # def _init():
    #     env = RedGymEnv(env_conf)
    #     env.reset(seed=(seed + rank))
    #     return env
    # set_random_seed(seed)
    # return _init


    def _init():
        env = StreamWrapper(
            RedGymEnv(env_conf),
            stream_metadata = {
                "user": "josh-testing",
                "env_id": rank,
                "color": "#f5bf42",
                "extra": "", # any extra text you put here will be displayed
            }
        )
        env.reset(seed=(seed + rank))
        return env
    set_random_seed(seed)
    return _init

if __name__ == '__main__':

    use_wandb_logging = False
    ep_length = 2048 * 10
    # sess_id = str(uuid.uuid4())[:8]
    # sess_path = Path(f'session_{sess_id}')
    # sess_path = Path(f'session_{socket.gethostname()}')
    sess_path = Path(f'session_docker')

    previous_session_file_name = ''

    env_config = {
                'headless': True, 'save_final_state': True, 'early_stop': False, 'add_score': True,
                'action_freq': 24, 'init_state': '../has_pokedex_nballs.state', 'max_steps': ep_length,
                'print_rewards': True, 'save_video': False, 'fast_video': True, 'session_path': sess_path,
                'gb_path': '../PokemonRed.gb', 'debug': True, 'sim_frame_dist': 2_000_000.0,
                'use_screen_explore': True, 'reward_scale': 4, 'extra_buttons': False,
                'explore_weight': 3 # 2.5
            }

    print(env_config)

    if exists(sess_path):
        prev_sess_path = f'{sess_path}.{time.strftime("%Y%m%d-%H%M%S")}'
        # Rename previous session before starting a new one
        os.rename(sess_path, prev_sess_path)
        steps_file=''
        steps_count=0
        for _, _, files in os.walk(prev_sess_path):
            for name in files:
                if name.endswith('steps.zip'):
                    if int(name.split("_")[1]) > steps_count:
                        steps_count = int(name.split("_")[1])
                        steps_file = name
        if steps_file != '':
            previous_session_file_name = f'{prev_sess_path}/{steps_file}'
            print (f'Found previous session @ {previous_session_file_name}')


    num_cpu = 8  # Also sets the number of episodes per training iteration
    env = SubprocVecEnv([make_env(i, env_config) for i in range(num_cpu)])
    # env = make_env(0, env_config)

    checkpoint_callback = CheckpointCallback(save_freq=ep_length, save_path=sess_path,
                                     name_prefix='poke')

    callbacks = [checkpoint_callback, TensorboardCallback()]

    if use_wandb_logging:
        import wandb
        from wandb.integration.sb3 import WandbCallback
        run = wandb.init(
            project="pokemon-train",
            id=sess_id,
            config=env_config,
            sync_tensorboard=True,
            monitor_gym=True,
            save_code=True,
        )
        callbacks.append(WandbCallback())

    #env_checker.check_env(env)
    # put a checkpoint here you want to start from
    # file_name = 'session_100it/poke_3932160_steps'
    # file_name = 'session_placeholder/poke_3276800_steps'

    print('main 9')


    # if exists(file_name + '.zip'):
    if exists(previous_session_file_name):
        print('\nloading checkpoint')
        model = PPO.load(previous_session_file_name, env=env)
        model.n_steps = ep_length
        model.n_envs = num_cpu
        model.rollout_buffer.buffer_size = ep_length
        model.rollout_buffer.n_envs = num_cpu
        model.rollout_buffer.reset()
    else:
        model = PPO('CnnPolicy', env, verbose=1, n_steps=ep_length // 8, batch_size=128, n_epochs=3, gamma=0.998, tensorboard_log=sess_path)

    print('main 10')


    # run for up to 5k episodes
    model.learn(total_timesteps=(ep_length)*num_cpu*5000, callback=CallbackList(callbacks))

    if use_wandb_logging:
        run.finish()
