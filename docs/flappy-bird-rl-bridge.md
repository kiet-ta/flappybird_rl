# Build Flappy Bird RL Bridge (Go -> C ABI -> Python)

This guide explains why this project exposes Go code through a C ABI, how that supports Python RL training, and the standard conventions used in this repository.

## 1. Goal and context

The game engine and physics are implemented in Go (`internal/core`, `internal/env`) for simple, deterministic simulation logic.  
The RL training stack is in Python because the ecosystem is mature (`gymnasium`, `numpy`, `stable-baselines3`, `PyTorch`).

So the target architecture is:

```text
Python RL Agent -> ctypes -> flappy_rl.so (C ABI) -> Go env/core
```

## 2. Why "change Go to C"?

It is **not** rewriting the game in C.  
It means exporting Go functions with a **C-compatible ABI** so Python can call them safely.

Why this is used:

1. **Direct package import is not possible**: Python cannot import Go packages natively.
2. **C ABI is universal**: many languages can call `.so`/`.dll` through C signatures.
3. **Low-overhead interop**: Python passes a pointer to a pre-allocated buffer, and Go writes into it.
4. **Keep best of both worlds**: Go for simulation performance/clarity, Python for RL tooling.

## 3. What is implemented in this bridge

`cmd/rl_bridge/main.go` exports three functions:

- `InitEnv(seed)` -> initialize environment with deterministic seed.
- `ResetEnv(outArray)` -> reset episode and write initial values.
- `StepEnv(action, outArray)` -> apply action and write step result.

Shared output buffer format (length = 6, `float64`):

```text
[BirdY, BirdVel, NextPipeX, NextGapY, Reward, Done]
```

Action convention:

- `0` = no flap
- `1` = flap

Observation convention:

```text
[BirdY, BirdVel, NextPipeX, NextGapY]
```

## 4. Build and run flow

Build shared library from Go:

```bash
go build -buildmode=c-shared -o flappy_rl.so ./cmd/rl_bridge
```

This generates:

- `flappy_rl.so` (runtime shared library)
- `flappy_rl.h` (generated C header)

Use from Python (`cmd/rl_bridge/flappy_env.py`) via `ctypes`:

- Load `./flappy_rl.so`
- Define `argtypes` for strict type conversion
- Pre-allocate `numpy` buffer and pass pointer to Go

## 5. What is `.venv` and why use it?

`.venv` is a **local Python virtual environment** for this project only.

It contains:

- A project-local Python interpreter
- Project-local installed packages
- Activation scripts (`source .venv/bin/activate`)

Why this is standard:

1. **Isolation**: avoids conflicts with global/system Python packages.
2. **Reproducibility**: all project scripts use the same dependency set.
3. **Safety**: system Python remains untouched.
4. **Easy cleanup**: remove `.venv` without affecting other projects.

Typical setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install gymnasium numpy
```

## 6. Standard conventions for this repository

1. **Single source of game truth is Go**  
   Keep physics/reward/episode logic in Go (`internal/core`, `internal/env`), not duplicated in Python.

2. **Bridge is thin and stable**  
   `cmd/rl_bridge` should only convert types and move data across ABI boundaries.

3. **ABI contract must stay explicit**  
   If buffer layout, action IDs, or observation order changes, update Go + Python together.

4. **Deterministic episodes by seed**  
   Use `InitEnv(seed)` and keep randomization controlled inside Go.

5. **Reset before stepping**  
   Always call `ResetEnv` before the first `StepEnv` in an episode.

6. **Keep Python dependencies inside `.venv`**  
   Do not rely on global Python packages for RL scripts.

7. **Rebuild `.so` whenever Go bridge/env changes**  
   Python will continue using old behavior until `flappy_rl.so` is rebuilt.

## 7. Practical note for future scaling

Current bridge uses one global environment instance (`rlEnv`).  
For vectorized/multi-env RL training, refactor to manage multiple env instances by `envID`.
