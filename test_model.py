import time
from stable_baselines3 import PPO
from flappy_env import FlappyEnv

def test_model(model_path, num_episodes=5):
    print(f"--- ĐANG KIỂM TRA MODEL: {model_path} ---")
    
    # 1. Khởi tạo môi trường
    # Lưu ý: Nếu môi trường của bạn có hỗ trợ render cửa sổ, bạn có thể thêm logic ở đây
    env = FlappyEnv(seed=123)
    
    # 2. Load model đã train
    try:
        model = PPO.load(model_path, env=env)
        print("✅ Đã load model thành công!")
    except Exception as e:
        print(f"❌ Lỗi khi load model: {e}")
        return

    # 3. Chạy thử nghiệm
    for episode in range(1, num_episodes + 1):
        obs, info = env.reset()
        done = False
        score = 0
        steps = 0
        
        while not done:
            # AI dự đoán hành động dựa trên quan sát (observation)
            # deterministic=True giúp AI chọn hành động tốt nhất thay vì ngẫu nhiên
            action, _states = model.predict(obs, deterministic=True)
            
            obs, reward, terminated, truncated, info = env.step(action)
            
            score += reward
            steps += 1
            done = terminated or truncated
            
            # Nếu bạn muốn quan sát AI chơi chậm lại một chút (nếu có UI)
            # time.sleep(0.01) 
            
        print(f"🔹 Episode {episode}: Score = {score:.2f}, Steps = {steps}")

    print("\n--- HOÀN THÀNH KIỂM TRA ---")

if __name__ == "__main__":
    MODEL_PATH = "./models/latest/flappy_interrupted"
    test_model(MODEL_PATH)
