# File: flappy_env.py
import ctypes

import gymnasium as gym
import numpy as np
from gymnasium import spaces

# 1. Load the shared library (Go game engine module)
lib = ctypes.cdll.LoadLibrary("./flappy_rl.so")

# 2. Define function signatures (C-ABI) so Python can handle type conversion correctly
lib.InitEnv.argtypes = [ctypes.c_longlong]
lib.ResetEnv.argtypes = [ctypes.POINTER(ctypes.c_double)]
lib.StepEnv.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_double)]


class FlappyEnv(gym.Env):
    """A standardized Gymnasium environment that wraps a game engine written in Go."""

    def __init__(self, seed=42):
        super().__init__()

        # Action Space: 0 = Do nothing, 1 = Flap (jump)
        self.action_space = spaces.Discrete(2)

        # Observation Space: Min/Max bounds for input parameters
        # [BirdY, BirdVelocity, NextPipeX, NextGapY]
        low = np.array([0.0, -15.0, 0.0, 0.0], dtype=np.float32)
        high = np.array([640.0, 15.0, 480.0, 640.0], dtype=np.float32)
        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)

        # ARCHITECTURE INSIGHT: Pre-allocate memory in Python (6 float64 elements)
        # The Go engine writes directly into this memory instead of returning new arrays
        self.buffer = np.zeros(6, dtype=np.float64)
        self.buffer_ptr = self.buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        # Initialize the Go engine
        lib.InitEnv(seed)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # Call Go function and pass the memory pointer
        lib.ResetEnv(self.buffer_ptr)

        # Extract the first 4 elements as the observation
        obs = self.buffer[:4].astype(np.float32)
        return obs, {}

    def step(self, action):
        # Send action and memory pointer to Go for physics processing
        lib.StepEnv(int(action), self.buffer_ptr)

        # Unpack data from the shared buffer
        obs = self.buffer[:4].astype(np.float32)
        reward = float(self.buffer[4])
        terminated = bool(self.buffer[5] == 1.0)
        truncated = False  # Usually used for time limits; not needed here

        return obs, reward, terminated, truncated, {}
