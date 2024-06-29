from os.path import exists
from pathlib import Path
import time
import os
import shutil
import pathlib
from red_gym_env import RedGymEnv
from stable_baselines3 import PPO
from stable_baselines3.common import env_checker
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, DummyVecEnv
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
from tensorboard_callback import TensorboardCallback
from stream_agent_wrapper import StreamWrapper

EP_LENGTH = 2048 * 10 # How many steps per episode
NUM_CPU = 12  # Also sets the number of episodes per training iteration
# PPO_DEVICE = 'cpu'
PPO_DEVICE = 'cuda'
STREAM_USER = 'joshhsoj1902'
STREAM_COLOR = '#c97f06'

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
                "user": STREAM_USER,
                "env_id": rank,
                "color": STREAM_COLOR,
                "extra": "", # any extra text you put here will be displayed
            }
        )
        env.reset(seed=(seed + rank))
        return env
    set_random_seed(seed)
    return _init

if __name__ == '__main__':

    use_wandb_logging = False
    sess_path = Path(f'session_fast')

    previous_session_file_name = ''

    env_config = {
                'headless': True, 'save_final_state': True, 'early_stop': False, 'add_score': True,
                'action_freq': 24, 'init_state': '../has_pokedex_nballs.state', 'max_steps': EP_LENGTH,
                'print_rewards': True, 'save_video': True, 'fast_video': True, 'session_path': sess_path,
                'gb_path': '../PokemonRed.gb', 'debug': True, 'sim_frame_dist': 2_000_000.0,
                'use_screen_explore': False, 'reward_scale': 4, 'extra_buttons': False,
                'explore_weight': 3 # 2.5
            }

    print(env_config)

    if exists(sess_path):
        prev_sess_path = f'{sess_path}.{time.strftime("%Y%m%d-%H%M%S")}'
        # Rename previous session before starting a new one
        os.rename(sess_path, prev_sess_path)
        sess_path.mkdir(exist_ok=True)

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

            # Record into the new session where the old session was pulled from
            f = open(sess_path / "checkpoint_source.txt", "w")
            f.write(previous_session_file_name)
            f.close()
        else:
            checkpoint_file = f'{prev_sess_path}/checkpoint_source.txt'
            print(f"Step file not found, attempting to recover previous session from {checkpoint_file}")
            if exists(checkpoint_file):
                print(f'Found previous session reference... attempting to load')
                f = open(checkpoint_file, "r")
                previous_session_file_name = f.read()
                print(f'Previous session:: {previous_session_file_name}')
                f.close()
                shutil.copyfile(checkpoint_file, f'{sess_path}/checkpoint_source.txt')
                os.rename(prev_sess_path, f'{prev_sess_path}.corrupt')

            else:
                print(f'{checkpoint_file} does not exist')


    env = SubprocVecEnv([make_env(i, env_config) for i in range(NUM_CPU)])
    # env = make_env(0, env_config)

    checkpoint_callback = CheckpointCallback(save_freq=EP_LENGTH, save_path=sess_path,
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

    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

    # if exists(file_name + '.zip'):
    if exists(previous_session_file_name):
        print(f'\nloading checkpoint {previous_session_file_name}')
        model = PPO.load(previous_session_file_name, env=env)
        model.n_steps = EP_LENGTH
        model.n_envs = NUM_CPU
        model.rollout_buffer.buffer_size = EP_LENGTH
        model.rollout_buffer.n_envs = NUM_CPU
        model.rollout_buffer.reset()
        model.tensorboard_log=sess_path
        model.device=PPO_DEVICE

    else:
        model = PPO('CnnPolicy', env, verbose=1, n_steps=EP_LENGTH // 8, batch_size=128, n_epochs=3, gamma=0.998, tensorboard_log=sess_path, device=PPO_DEVICE)

    pathlib.PosixPath = temp
    print('main 10')

    # run for up to 5k episodes
    model.learn(total_timesteps=(EP_LENGTH)*NUM_CPU*5000, callback=CallbackList(callbacks))

    if use_wandb_logging:
        run.finish()
