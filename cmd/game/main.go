package main

import (
	"log"
	"time"

	"FlappyBird_RL/internal/core"
	"FlappyBird_RL/internal/render"
	"github.com/hajimehoshi/ebiten/v2"
)

func main() {
	game := render.NewGame(time.Now().UnixNano())

	ebiten.SetWindowSize(core.ScreenWidth, core.ScreenHeight)
	// ebiten.SetWindowTitle("Flappy Bird (Go + Ebiten)")

	if err := ebiten.RunGame(game); err != nil {
		log.Fatal(err)
	}
}
