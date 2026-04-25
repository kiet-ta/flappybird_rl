package env

import "FlappyBird_RL/internal/core"

type Action int

const (
	ActionNone Action = iota
	ActionFlap
)

type Observation struct {
	BirdY     float64
	BirdVel   float64
	NextPipeX float64
	NextGapY  float64
	Score     int
	Alive     bool
}

type Environment struct {
	game *core.Game
}

func New(seed int64) *Environment {
	return &Environment{game: core.NewGame(seed)}
}

func (e *Environment) Reset() Observation {
	state := e.game.Reset()
	return makeObservation(state)
}

func (e *Environment) Step(action Action) (Observation, float64, bool) {
	prevScore := e.game.State().Score

	if action == ActionFlap {
		e.game.Jump()
	}

	state, done := e.game.Step()
	reward := 0.1 + float64(state.Score-prevScore)
	if done {
		reward = -1
	}

	return makeObservation(state), reward, done
}

func (e *Environment) State() core.State {
	return e.game.State()
}

func makeObservation(state core.State) Observation {
	nextPipeX := float64(core.ScreenWidth)
	nextGapY := float64(core.ScreenHeight) / 2

	for _, pipe := range state.Pipes {
		if pipe.X+core.PipeWidth >= core.BirdX {
			nextPipeX = pipe.X - core.BirdX
			nextGapY = pipe.GapY
			break
		}
	}

	return Observation{
		BirdY:     state.BirdY,
		BirdVel:   state.BirdVel,
		NextPipeX: nextPipeX,
		NextGapY:  nextGapY,
		Score:     state.Score,
		Alive:     state.Alive,
	}
}
