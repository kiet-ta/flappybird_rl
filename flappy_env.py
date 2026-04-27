import ctypes
import gymnasium as gym
import numpy as np
from gymnasium import spaces

# 1. Load the shared library (Go game engine module)
try:
    lib = ctypes.cdll.LoadLibrary("./flappy_rl.so")
except OSError:
    print("❌ Lỗi: Không tìm thấy file 'flappy_rl.so'.")
    print("👉 Hãy chạy lệnh: go build -buildmode=c-shared -o flappy_rl.so ./cmd/rl_bridge")
    exit(1)

# 2. Define function signatures (C-ABI) so Python can handle type conversion correctly
lib.InitEnv.argtypes = [ctypes.c_longlong]
lib.ResetEnv.argtypes = [ctypes.POINTER(ctypes.c_double)]
lib.StepEnv.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_double)]
lib.InitEnv.restype = None
lib.ResetEnv.restype = None
lib.StepEnv.restype = None


class FlappyEnv(gym.Env):
    """A standardized Gymnasium environment that wraps a game engine written in Go."""

    # Raw observation bounds from Go env: [BirdY, BirdVel, NextPipeX, NextGapY]
    _RAW_OBS_LOW = np.array([0.0, -20.0, -64.0, 0.0], dtype=np.float32)
    _RAW_OBS_HIGH = np.array([640.0, 20.0, 480.0, 640.0], dtype=np.float32)

    def __init__(self, seed=42):
        super().__init__()

        # Action Space: 0 = Do nothing, 1 = Flap (jump)
        self.action_space = spaces.Discrete(2)

        # Normalized observation space for PPO stability
        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(4,),
            dtype=np.float32,
        )

        # ARCHITECTURE INSIGHT: Pre-allocate memory in Python (20 float64 elements)
        # The Go engine writes directly into this memory instead of returning new arrays
        self.buffer = np.zeros(20, dtype=np.float64)
        self.buffer_ptr = self.buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        # Initialize the Go engine
        lib.InitEnv(seed)

    def _normalize_obs(self, raw_obs: np.ndarray) -> np.ndarray:
        scaled = 2.0 * (raw_obs - self._RAW_OBS_LOW) / (self._RAW_OBS_HIGH - self._RAW_OBS_LOW) - 1.0
        return np.clip(scaled, -1.0, 1.0).astype(np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            lib.InitEnv(seed)

        # Call Go function and pass the memory pointer
        lib.ResetEnv(self.buffer_ptr)

        # Extract the first 4 elements as the observation
        raw_obs = self.buffer[:4].astype(np.float32)
        return self._normalize_obs(raw_obs), {}

    def step(self, action):
        # Send action and memory pointer to Go for physics processing
        lib.StepEnv(int(action), self.buffer_ptr)

        # Unpack data from the shared buffer
        raw_obs = self.buffer[:4].astype(np.float32)
        obs = self._normalize_obs(raw_obs)
        reward = float(self.buffer[4])
        terminated = bool(self.buffer[5] == 1.0)
        truncated = False  # Usually used for time limits; not needed here

        return obs, reward, terminated, truncated, {}
