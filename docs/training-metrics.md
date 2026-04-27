# Giải thích các Thông số Huấn luyện (PPO Metrics)

Khi chạy `train.py` hoặc `resume-train.py`, thư viện Stable Baselines3 sẽ in ra một bảng thông số sau mỗi lần cập nhật. Dưới đây là ý nghĩa chi tiết của từng chỉ số để bạn theo dõi sức khỏe của model.

## 1. Nhóm Rollout (Hiệu suất trong Game)

Đây là nhóm quan trọng nhất để biết AI chơi có tốt hay không.

- **ep_len_mean (295):** Độ dài trung bình của một ván chơi (số bước/frames). Con số này càng cao nghĩa là AI càng sống dai. 295 steps là một con số khá tốt.
- **ep_rew_mean (29.6):** Tổng điểm thưởng trung bình mỗi ván. Trong Flappy Bird, nó thường tương lệ thuận với thời gian sống. Nếu con số này tăng dần theo thời gian = AI đang học đúng hướng.

## 2. Nhóm Time (Hiệu năng hệ thống)

- **fps (582):** Frames Per Second. AI đang "nhìn" và học với tốc độ 582 khung hình/giây. Tốc độ này phụ thuộc vào CPU và độ tối ưu của logic Go.
- **total_timesteps (1,323,008):** Tổng số bước AI đã thực hiện từ trước đến nay.

## 3. Nhóm Train (Thông số kỹ thuật thuật toán PPO)

Nhóm này dành cho việc tinh chỉnh sâu (Fine-tuning).

- **entropy_loss (-0.272):** Thể hiện độ "hỗn loạn" hoặc tính khám phá của AI.
  - Giá trị âm càng lớn (về trị tuyệt đối, ví dụ -0.6) nghĩa là AI đang thử nghiệm nhiều hành động ngẫu nhiên.
  - Giá trị tiến về 0 (ví dụ -0.1) nghĩa là AI đã rất tự tin vào hành động của mình (ít ngẫu nhiên hơn).
  - _Lưu ý:_ Nếu nó về 0 quá nhanh, AI có thể bị kẹt vào một hành vi lặp đi lặp lại và không học thêm được cái mới.
- **explained_variance (0.768):** Đo lường khả năng dự đoán điểm số của "Value Function".
  - Càng gần **1.0** càng tốt (model hiểu rõ kết quả của hành động).
  - Nếu < 0, model đang dự đoán rất tệ (thường thấy ở giai đoạn đầu). 0.768 là mức cực kỳ ổn định.
- **learning_rate (0.0003):** Tốc độ học. Bạn đang để mặc định là 0.0003.
- **loss (0.978):** Tổng lỗi của mạng thần kinh. Nó sẽ trồi sụt, nhưng về dài hạn nên ổn định hoặc giảm nhẹ.
- **approx_kl (0.0077):** (Kullback-Leibler divergence). Đo mức độ thay đổi của "chiến thuật" giữa 2 lần cập nhật.
  - Nên là một số nhỏ (thường < 0.02).
  - Nếu số này vọt lên quá cao (ví dụ > 0.05), training có thể bị mất ổn định (AI bỗng dưng quên hết kiến thức cũ).
- **value_loss (1.16):** Lỗi trong việc dự đoán tổng điểm thưởng tương lai. Số này càng thấp thì AI càng "biết mình biết ta".

---

### Tóm tắt nhanh:

- Muốn biết AI chơi giỏi chưa? Nhìn **ep_rew_mean**.
- Muốn biết AI có đang học ổn định không? Nhìn **explained_variance** (nên > 0.5) và **approx_kl** (nên thấp).
- Muốn biết AI còn muốn khám phá cái mới không? Nhìn **entropy_loss** (không nên bằng 0 quá sớm).
