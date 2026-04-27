import cv2
import numpy as np
from stable_baselines3 import PPO
from flappy_env import FlappyEnv
import time

def visualize_ai(model_path):
    env = FlappyEnv(seed=123)
    model = PPO.load(model_path)
    
    obs, info = env.reset()
    
    width, height = 480, 640
    pipe_width = 64
    pipe_gap = 170
    bird_size = 18

    print("🚀 Đang khởi chạy bản FULL HD...")
    print("👉 Nhấn 'q' để thoát.")

    while True:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        
        # --- LẤY DỮ LIỆU TỪ BUFFER MỚI ---
        raw_data = env.buffer
        bird_y = raw_data[0]
        score = int(raw_data[6])
        num_pipes = int(raw_data[7])
        
        # --- VẼ GIAO DIỆN ---
        # 1. Nền trời
        canvas = np.full((height, width, 3), (235, 206, 135), dtype=np.uint8)
        
        # 2. Vẽ TẤT CẢ các ống cống
        for i in range(num_pipes):
            px = raw_data[8 + i*2]
            py = raw_data[9 + i*2]
            
            # Ống trên
            cv2.rectangle(canvas, (int(px), 0), (int(px + pipe_width), int(py - pipe_gap/2)), (34, 139, 34), -1)
            cv2.rectangle(canvas, (int(px), 0), (int(px + pipe_width), int(py - pipe_gap/2)), (0, 0, 0), 2) # Viền
            
            # Ống dưới
            cv2.rectangle(canvas, (int(px), int(py + pipe_gap/2)), (int(px + pipe_width), height), (34, 139, 34), -1)
            cv2.rectangle(canvas, (int(px), int(py + pipe_gap/2)), (int(px + pipe_width), height), (0, 0, 0), 2) # Viền

        # 3. Vẽ Chim (với hiệu ứng đổ bóng nhẹ)
        cv2.rectangle(canvas, (96, int(bird_y)), (96 + bird_size, int(bird_y + bird_size)), (0, 215, 255), -1)
        cv2.rectangle(canvas, (96, int(bird_y)), (96 + bird_size, int(bird_y + bird_size)), (0, 0, 0), 2)

        # 4. Hiển thị UI
        cv2.putText(canvas, f"SCORE: {score}", (20, 50), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 3)
        cv2.putText(canvas, f"SCORE: {score}", (20, 50), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 1)
        
        cv2.imshow("Flappy Bird RL - FULL HD", canvas)
        
        if cv2.waitKey(15) & 0xFF == ord('q'):
            break
            
        if terminated:
            print(f"💀 Game Over! Score cuối cùng: {score}")
            time.sleep(1.0)
            obs, info = env.reset()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    MODEL_PATH = "./models/latest/flappy_interrupted"
    visualize_ai(MODEL_PATH)
