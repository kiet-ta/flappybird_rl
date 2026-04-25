package core

import "math/rand"

const (
	ScreenWidth  = 480
	ScreenHeight = 640

	BirdX    = 96.0
	BirdSize = 18.0

	Gravity      = 0.35
	JumpVelocity = -5.2

	PipeWidth     = 64.0
	PipeGap       = 170.0
	PipeSpeed     = 2.4
	PipeSpawnTick = 105
)

type Pipe struct {
	X      float64
	GapY   float64
	Passed bool
}

type State struct {
	BirdY   float64
	BirdVel float64
	Pipes   []Pipe
	Score   int
	Alive   bool
	Tick    int
}

type Game struct {
	state State
	rng   *rand.Rand
	spawnCounter int
}

func NewGame(seed int64) *Game {
	g := &Game{
		rng: rand.New(rand.NewSource(seed)),
	}
	g.Reset()
	return g
}

func (g *Game) Reset() State {
	g.state = State{
		BirdY: float64(ScreenHeight) / 2,
		Alive: true,
	}
	g.spawnCounter = PipeSpawnTick / 2
	return g.State()
}

func (g *Game) State() State {
	cp := g.state
	cp.Pipes = append([]Pipe(nil), g.state.Pipes...)
	return cp
}

func (g *Game) Jump() {
	if !g.state.Alive {
		return
	}
	g.state.BirdVel = JumpVelocity
}

func (g *Game) Step() (State, bool) {
	if !g.state.Alive {
		return g.State(), true
	}

	g.state.Tick++
	g.state.BirdVel += Gravity
	g.state.BirdY += g.state.BirdVel

	g.spawnCounter++
	if g.spawnCounter >= PipeSpawnTick {
		g.spawnPipe()
		g.spawnCounter = 0
	}

	surviving := g.state.Pipes[:0]
	for _, pipe := range g.state.Pipes {
		pipe.X -= PipeSpeed

		if !pipe.Passed && pipe.X+PipeWidth < BirdX {
			pipe.Passed = true
			g.state.Score++
		}
		if pipe.X+PipeWidth >= 0 {
			surviving = append(surviving, pipe)
		}
	}
	g.state.Pipes = surviving

	if g.state.BirdY < 0 || g.state.BirdY+BirdSize > ScreenHeight {
		g.state.Alive = false
		return g.State(), true
	}
	if g.hitPipe() {
		g.state.Alive = false
		return g.State(), true
	}

	return g.State(), false
}

func (g *Game) spawnPipe() {
	minGapY := PipeGap/2 + 40
	maxGapY := float64(ScreenHeight) - PipeGap/2 - 40

	gapY := minGapY + g.rng.Float64()*(maxGapY-minGapY)
	g.state.Pipes = append(g.state.Pipes, Pipe{
		X:    float64(ScreenWidth),
		GapY: gapY,
	})
}

func (g *Game) hitPipe() bool {
	birdLeft := BirdX
	birdRight := BirdX + BirdSize
	birdTop := g.state.BirdY
	birdBottom := g.state.BirdY + BirdSize

	for _, pipe := range g.state.Pipes {
		pipeLeft := pipe.X
		pipeRight := pipe.X + PipeWidth
		overlapX := birdRight > pipeLeft && birdLeft < pipeRight
		if !overlapX {
			continue
		}

		gapTop := pipe.GapY - PipeGap/2
		gapBottom := pipe.GapY + PipeGap/2
		if birdTop < gapTop || birdBottom > gapBottom {
			return true
		}
	}

	return false
}
