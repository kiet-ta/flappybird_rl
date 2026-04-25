package render

import (
	"fmt"
	"image/color"

	"FlappyBird_RL/internal/core"
	"FlappyBird_RL/internal/env"
	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/ebitenutil"
)

type Game struct {
	env *env.Environment
	obs env.Observation

	done       bool
	lastReward float64
}

func NewGame(seed int64) *Game {
	e := env.New(seed)
	return &Game{
		env: e,
		obs: e.Reset(),
	}
}

func (g *Game) Update() error {
	if g.done {
		if ebiten.IsKeyPressed(ebiten.KeyR) {
			g.obs = g.env.Reset()
			g.done = false
			g.lastReward = 0
		}
		return nil
	}

	action := env.ActionNone
	if ebiten.IsKeyPressed(ebiten.KeySpace) || ebiten.IsMouseButtonPressed(ebiten.MouseButtonLeft) {
		action = env.ActionFlap
	}

	obs, reward, done := g.env.Step(action)
	g.obs = obs
	g.done = done
	g.lastReward = reward

	return nil
}

func (g *Game) Draw(screen *ebiten.Image) {
	screen.Fill(color.RGBA{R: 135, G: 206, B: 235, A: 255})

	state := g.env.State()
	for _, pipe := range state.Pipes {
		gapTop := pipe.GapY - core.PipeGap/2
		gapBottom := pipe.GapY + core.PipeGap/2

		ebitenutil.DrawRect(screen, pipe.X, 0, core.PipeWidth, gapTop, color.RGBA{R: 34, G: 139, B: 34, A: 255})
		ebitenutil.DrawRect(
			screen,
			pipe.X,
			gapBottom,
			core.PipeWidth,
			float64(core.ScreenHeight)-gapBottom,
			color.RGBA{R: 34, G: 139, B: 34, A: 255},
		)
	}

	ebitenutil.DrawRect(screen, core.BirdX, state.BirdY, core.BirdSize, core.BirdSize, color.RGBA{R: 255, G: 215, B: 0, A: 255})

	msg := fmt.Sprintf("Score: %d\nReward: %.2f", state.Score, g.lastReward)
	if g.done {
		msg += "\nGame Over - Press R to restart"
	}
	ebitenutil.DebugPrint(screen, msg)
}

func (g *Game) Layout(_, _ int) (int, int) {
	return core.ScreenWidth, core.ScreenHeight
}
