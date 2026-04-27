import os
import time
import glob
from flappy_env import FlappyEnv
try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.callbacks import EvalCallback
except ImportError:
    print("❌ Lỗi: Thiếu thư viện 'stable-baselines3'.")
    exit(1)

def find_latest_model(model_dir="./models"):
    """Tìm file .zip mới nhất trong thư mục models."""
    files = glob.glob(os.path.join(model_dir, "**/*.zip"), recursive=True)
    if not files:
        return None
    latest_file = max(files, key=os.path.getmtime)
    # SB3 load không cần đuôi .zip
    return latest_file.replace(".zip", "")

def main():
    print("🚀 Mở khóa phòng tập thời gian - PHASE 2 (Tiếp tục cày)...")
    
    # 1. Tìm model mới nhất
    model_path = find_latest_model()
    
    if model_path is None:
        print("❌ Không tìm thấy model cũ để load! Vui lòng chạy train.py trước.")
        return

    print(f"🧠 Đang nạp ký ức từ file: {model_path}.zip")

    # 2. Khởi tạo môi trường
    env = FlappyEnv(seed=int(time.time()))
    eval_env = FlappyEnv(seed=999)

    # 3. Load model
    try:
        model = PPO.load(model_path, env=env, tensorboard_log="./models/logs/")
    except Exception as e:
        print(f"❌ Lỗi khi load model: {e}")
        return

    # 4. Setup EvalCallback để giữ vững phong độ
    eval_callback = EvalCallback(
        eval_env, 
        best_model_save_path='./models/best/',
        log_path='./models/logs/', 
        eval_freq=50000,
        deterministic=True, 
        render=False
    )

    print(f"🔥 Lên đồ! Tiếp tục cày từ bước {model.num_timesteps}...")
    
    try:
        # 5. reset_num_timesteps=False giúp biểu đồ TensorBoard không bị đứt đoạn
        model.learn(
            total_timesteps=2_000_000,
            callback=eval_callback,
            reset_num_timesteps=False,
        )

        model.save("./models/latest/flappy_latest")
        print("✅ Đã hoàn thành quá trình train tiếp!")
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng huấn luyện và lưu tạm thời...")
        model.save("./models/latest/flappy_latest")
        print("✅ Đã lưu an toàn tại './models/latest/flappy_latest.zip'!")


if __name__ == "__main__":
    main()
