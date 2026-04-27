import os
try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.callbacks import EvalCallback
except ImportError:
    print("❌ Lỗi: Thiếu thư viện 'stable-baselines3'.")
    print("👉 Hãy chạy lệnh: pip install stable-baselines3 shimmy")
    exit(1)

from flappy_env import FlappyEnv

print("--- ĐANG KHỞI CHẠY QUÁ TRÌNH HUẤN LUYỆN RL ---")

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs("./models/best/", exist_ok=True)
    os.makedirs("./models/logs/", exist_ok=True)
    os.makedirs("./models/latest/", exist_ok=True)

    # 1. Khởi tạo môi trường
    env = FlappyEnv(seed=42)

    # 2. Khởi tạo thuật toán PPO
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=0.0003, tensorboard_log="./models/logs/")

    # 3. Setup EvalCallback
    eval_env = FlappyEnv(seed=999) 

    eval_callback = EvalCallback(
        eval_env, 
        best_model_save_path='./models/best/', # File ngon nhất ném vào đây
        log_path='./models/logs/', 
        eval_freq=50000,          # Cứ 50k bước thì vác model ra chấm điểm 1 lần
        deterministic=True, 
        render=False
    )

    print("\n🚀 AI bắt đầu học... (Vui lòng đợi)\n")
    
    try:
        # 4. Chạy huấn luyện 2,000,000 bước
        model.learn(total_timesteps=2_000_000, callback=eval_callback)
        
        # 5. Lưu model sau khi learn xong thành Latest
        model.save("./models/latest/flappy_latest")
        print("\n✅ THÀNH CÔNG: Đã lưu model tại './models/latest/flappy_latest.zip'")
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng huấn luyện và lưu tạm thời...")
        model.save("./models/latest/flappy_interrupted")
        print("✅ Đã lưu tại './models/latest/flappy_interrupted.zip'")
