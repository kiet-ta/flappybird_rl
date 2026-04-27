// File: cmd/rl_bridge/main.go
package main

import "C"
import (
	"unsafe"
	"FlappyBird_RL/internal/env"
)

// Global reference to the environment instance.
// Note for future scaling: If using Vectorized Environments (parallel training), 
// this should be refactored into a map/array of environments accessed by an envID.
var rlEnv *env.Environment

//export InitEnv
// InitEnv initializes the core game environment with a specific seed for deterministic behavior.
func InitEnv(seed C.longlong) {
	rlEnv = env.New(int64(seed)) //
}

//export ResetEnv
// ResetEnv resets the environment and writes the initial state into the provided C array.
// outArray MUST be a pre-allocated array of 6 float64 elements from Python.
func ResetEnv(outArray *C.double) {
	if rlEnv == nil {
		return
	}
	obs := rlEnv.Reset() //
	fillBuffer(obs, 0.0, false, outArray)
}

//export StepEnv
// StepEnv advances the game by one frame based on the given action.
// outArray MUST be a pre-allocated array of 6 float64 elements from Python.
func StepEnv(action C.int, outArray *C.double) {
	if rlEnv == nil {
		return
	}
	
	// Convert C integer to Go Action enum (0: None, 1: Flap)
	goAction := env.Action(int(action)) //
	
	// Execute the physical step
	obs, reward, done := rlEnv.Step(goAction) //
	
	// Write results directly to Python's memory
	fillBuffer(obs, reward, done, outArray)
}

// fillBuffer maps the C pointer to a Go slice for zero-copy memory writing.
func fillBuffer(obs env.Observation, reward float64, done bool, outArray *C.double) {
	// Cast the C double pointer to a Go slice of float64 with length 20.
	out := unsafe.Slice((*float64)(unsafe.Pointer(outArray)), 20)

	// 1. Dữ liệu chuẩn cho RL (không đổi để tránh lỗi model)
	out[0] = obs.BirdY
	out[1] = obs.BirdVel
	out[2] = obs.NextPipeX
	out[3] = obs.NextGapY
	
	// 2. Thông tin hỗ trợ
	out[4] = reward
	if done {
		out[5] = 1.0
	} else {
		out[5] = 0.0
	}

	// 3. Dữ liệu bổ sung cho "Full HD" Visualization
	state := rlEnv.State()
	out[6] = float64(state.Score)
	
	pipes := state.Pipes
	numPipes := len(pipes)
	if numPipes > 5 {
		numPipes = 5 // Giới hạn 5 ống để không tràn buffer
	}
	out[7] = float64(numPipes)

	for i := 0; i < numPipes; i++ {
		out[8+i*2] = pipes[i].X
		out[9+i*2] = pipes[i].GapY
	}
}

func main() {
	// Main function is required for Go compiler to build -buildmode=c-shared,
	// even though it is intentionally left empty.
}
