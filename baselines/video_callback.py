from stable_baselines3.common.callbacks import BaseCallback

class VideoCallback(BaseCallback):
    """
    A custom callback that derives from ``BaseCallback`` used for various video management things.

    :param verbose: (int) Verbosity level 0: not output 1: info 2: debug
    """
    def __init__(self, stream, verbose=0, ):
        super(VideoCallback, self).__init__(verbose)
        self.stream = stream
        # Those variables will be accessible in the callback
        # (they are defined in the base class)
        # The RL model
        # self.model = None  # type: BaseRLModel
        # An alias for self.model.get_env(), the environment used for training
        # self.training_env = None  # type: Union[gym.Env, VecEnv, None]
        # Number of time the callback was called
        # self.n_calls = 0  # type: int
        # self.num_timesteps = 0  # type: int
        # local and global variables
        # self.locals = None  # type: Dict[str, Any]
        # self.globals = None  # type: Dict[str, Any]
        # The logger object, used to report things in the terminal
        # self.logger = None  # type: logger.Logger
        # # Sometimes, for event callback, it is useful
        # # to have access to the parent object
        # self.parent = None  # type: Optional[BaseCallback]

    def _on_training_start(self) -> None:
        """
        This method is called before the first rollout starts.
        """
        pass

    def _on_rollout_start(self) -> None:
        """
        A rollout is the collection of environment interaction
        using the current policy.
        This event is triggered before collecting new samples.
        """

        print('\nDo some video managing on every rollout start I think.\n ')
        pass

    def _on_step(self) -> bool:
        """
        This method will be called by the model after each call to `env.step()`.

        For child callback (of an `EventCallback`), this will be called
        when the event is triggered.

        :return: (bool) If the callback returns False, training is aborted early.
        """

        # The render creates a new frame every 50 steps. By subtracting 5 here we also update
        # every 50 steps, but we do it 5 steps after the frame was rendered
        if (self.n_calls-5) % 50 == 0:
            self.stream.update_stream_frame()

        return True

    def _on_rollout_end(self) -> None:
        """
        This event is triggered before updating the policy.
        """

        print('\nDo some video managing on every rollout end I think.\n No this is too early. I think we need rollout start instead\n')

        pass

    def _on_training_end(self) -> None:
        """
        This event is triggered before exiting the `learn()` method.
        """
        pass