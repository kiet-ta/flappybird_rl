# Gymnasium in AI: The Standard for Reinforcement Learning

This guide introduces **Gymnasium**, the toolkit used in this project to connect our Go-based game engine with modern Reinforcement Learning (RL) algorithms.

## 1. What is Gymnasium?

**Gymnasium** is an open-source Python library that provides a standardized API for Reinforcement Learning. It is a maintained fork of the original OpenAI `Gym` library.

In RL, we have two main components:
1.  **The Agent**: The "brain" (AI) that learns to make decisions.
2.  **The Environment**: The "world" (like our Flappy Bird game) where the agent lives and acts.

Gymnasium acts as the **standard interface** (the bridge) between them. It ensures that no matter how complex your game is, the AI can "talk" to it using a simple, universal language.

## 2. What does it help with?

Without Gymnasium, every AI researcher would have to write custom code to connect their AI to every different game. Gymnasium solves this by providing:

- **Standardized Communication**: Defines exactly how an agent receives information (observations) and sends commands (actions).
- **Environment Variety**: Access to hundreds of pre-made environments (Atari games, robotic simulations, board games).
- **Compatibility**: Most popular RL libraries (like **Stable Baselines3**, **Ray RLLib**, or **CleanRL**) are built to work perfectly with Gymnasium.
- **Reproducibility**: Tools for seeding and versioning ensure that your AI experiments can be repeated and verified by others.

## 3. The Core API (The "Language")

Every Gymnasium environment follows the same lifecycle:

| Method | Description |
| :--- | :--- |
| `reset()` | Starts a new episode and returns the initial observation. |
| `step(action)` | Applies an action, updates the physics, and returns the result. |
| `render()` | (Optional) Shows a visual window of the game. |
| `close()` | Cleans up resources. |

### The `step()` result
When the agent takes a "step", Gymnasium returns five important values:
1.  **Observation**: What the agent "sees" (e.g., Bird height, distance to pipe).
2.  **Reward**: A score indicating how "good" the action was (e.g., +1 for staying alive).
3.  **Terminated**: True if the agent crashed (Game Over).
4.  **Truncated**: True if the episode ended due to an external limit (e.g., time out).
5.  **Info**: Extra debugging data.

## 4. How it is used in this project

In this repository, we use Gymnasium to wrap our Go physics engine.

- **The File**: `cmd/rl_bridge/flappy_env.py`
- **The Role**: It creates a class `FlappyEnv(gym.Env)`.
- **The Magic**: This class takes raw data from our Go shared library (`.so`) and packages it into the standard Gymnasium format. 

Because we follow this standard, you can plug in an advanced AI from **Stable Baselines3** and it will "just work" with our Go game.

## 5. Related Information to Study

To master Gymnasium and AI, here are the key concepts and resources to explore:

### Key Concepts
- **Observation Space**: Defines what the agent sees.
  - *Discrete*: A list of options (e.g., Up, Down, Left).
  - *Box*: Continuous numbers (e.g., Velocity from -15.0 to 15.0).
- **Action Space**: Defines what the agent can do (In our case, `Discrete(2)` for "Do Nothing" or "Flap").
- **Markov Decision Process (MDP)**: The mathematical framework behind RL that Gymnasium implements.

### Recommended Learning Path
1.  **[Official Gymnasium Docs](https://gymnasium.farama.org/)**: The best place to start for API details.
2.  **[Stable Baselines3 Tutorials](https://stable-baselines3.readthedocs.io/)**: Learn how to train an agent in 10 lines of code.
3.  **[Hugging Face Deep RL Course](https://huggingface.co/learn/deep-rl-course/)**: A free, world-class course on how RL works from scratch.
4.  **[Spinning Up in Deep RL (OpenAI)](https://spinningup.openai.org/)**: A deep dive into the math and theory of RL algorithms.

---
*This document is part of the Flappy Bird RL documentation. It helps bridge the gap between Go game development and Python AI research.*
