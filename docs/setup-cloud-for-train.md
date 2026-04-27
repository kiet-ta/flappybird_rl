# 📘 Sổ Tay System Architecture & MLOps: Đưa Flappy Bird AI Lên Mây

Tài liệu này tổng hợp lại toàn bộ hành trình xây dựng, tối ưu và vận hành hệ thống Reinforcement Learning cho dự án Flappy Bird. Từ việc bắt bug kiến trúc dữ liệu AI trên local đến việc thiết lập cơ sở hạ tầng bảo mật chuẩn công nghiệp trên DigitalOcean Droplet.

---

## Chương 1: Tối Ưu Hóa Kiến Trúc Dữ Liệu AI (Bắt Bug Policy Collapse)

### 1. Vấn Đề Gặp Phải

Trong quá trình huấn luyện bằng Stable Baselines3 (PPO), biểu đồ TensorBoard xuất hiện hình răng cưa (tăng vọt lên rồi cắm đầu xuống đất). Đây là hiện tượng **Policy Collapse (Tẩu hỏa nhập ma)**.

### 2. Phân Tích Nguyên Nhân (Root Causes)

- **Ngộ độc số lớn (Unnormalized Observations):** Mạng Neural Network bị "nhồi" các con số quá lớn (tọa độ 640.0, 480.0). Điều này tạo ra lực cập nhật (Gradients) khổng lồ, phá nát ma trận trọng số (Weights) mỗi khi AI nhận hình phạt gắt.
- **Rách không gian (Bounds Violation):** Tọa độ `NextPipeX` bị âm khi chim bay vào giữa khe ống, nhưng `Observation Space` lại khai báo Min là `0.0`, khiến PPO đọc sai lệch không gian trạng thái.

### 3. Giải Pháp (Kiến Trúc Chuẩn Hóa Dữ Liệu)

Thêm một lớp Data Pre-processing tại tầng Python (`flappy_env.py`) để ép toàn bộ dữ liệu thô về dải `[-1.0, 1.0]`:

````
```text?code_stdout&code_event_index=2
File generated: FlappyBird_MLOps_System_Architecture_Guide.md
```python
def _normalize_obs(self, raw_obs):
    norm_obs = np.zeros(4, dtype=np.float32)
    norm_obs[0] = (raw_obs[0] - 320.0) / 320.0  # BirdY
    norm_obs[1] = raw_obs[1] / 20.0             # BirdVel
    norm_obs[2] = (raw_obs[2] - 240.0) / 240.0  # NextPipeX
    norm_obs[3] = (raw_obs[3] - 320.0) / 320.0  # NextGapY
    return np.clip(norm_obs, -1.0, 1.0)
````

_Kết quả:_ AI học mượt mà, đường đồ thị hội tụ và đi lên vững chắc.

---

## Chương 2: Thiết Lập Hạ Tầng Mạng & Bảo Mật VPS (Zero Trust Security)

Để chạy AI liên tục 24/7 trên DigitalOcean (Ubuntu), hệ thống cần được bọc thép. Không bao giờ chạy service trực tiếp dưới quyền `root`.

### 1. Phân Quyền Hệ Thống (Privilege Separation)

Tạo user dành riêng cho việc vận hành để giới hạn vùng ảnh hưởng nếu bị tấn công.

```bash
adduser kiet_dev
usermod -aG sudo kiet_dev   # Cấp quyền leo thang (Sudo)
usermod -aG docker kiet_dev # Cấp quyền chạy Docker không cần root
```

### 2. Chuyển Giao Workspace & Đóng Cửa Root

Di dời toàn bộ code về `/home/kiet_dev/` và khóa chức năng đăng nhập thẳng bằng root từ internet.

```bash
mv /root/FlappyBird_RL /home/kiet_dev/
chown -R kiet_dev:kiet_dev /home/kiet_dev/FlappyBird_RL
# Chỉnh file /etc/ssh/sshd_config
# PermitRootLogin no
sudo systemctl restart ssh
```

### 3. Sơ Đồ Kiến Trúc Phân Quyền

```plantuml
@startuml
skinparam monochrome true
actor "Hacker" as Hacker
actor "Dev (kiet_dev)" as Dev

package "DigitalOcean VPS" {
  node "Quyền ROOT" as RootNode
  node "Quyền USER" as UserNode {
    [Docker Environment]
  }
}

Dev --> UserNode : SSH an toàn
UserNode .> RootNode : Gọi sudo (yêu cầu pass)
Hacker -x-> RootNode : Bị block ở cửa chính
@enduml
```

---

## Chương 3: Kiến Trúc Reverse Proxy & Giám Sát (TensorBoard)

### 1. Bài Toán

Làm sao để xem TensorBoard Realtime trên điện thoại qua 4G mà không sợ hacker scan port 6006 để chọc ngoáy?

### 2. Giải Pháp: Nginx + Basic Auth

Ẩn port 6006 vào mạng nội bộ (Localhost), dùng Nginx đón request ở port 80 và bật khiên yêu cầu nhập mật khẩu.

**Cài đặt:**

```bash
sudo ufw allow 'Nginx HTTP'
sudo apt install nginx apache2-utils -y
sudo htpasswd -c /etc/nginx/.htpasswd admin  # Tạo mật khẩu
```

**Cấu hình Nginx (`/etc/nginx/sites-available/tensorboard`):**

```nginx
server {
    listen 80;
    server_name _;
    location / {
        auth_basic "Restricted Area";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass [http://127.0.0.1:6006](http://127.0.0.1:6006);
        # Hỗ trợ Websocket cho TensorBoard
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Bảng Trade-off Các Chiến Lược Expose Port

| Chiến lược             | Security                  | Dev UX                        | Đánh giá System                   |
| :--------------------- | :------------------------ | :---------------------------- | :-------------------------------- |
| Mở thẳng UFW Port 6006 | Rất Tệ (Ai cũng vào được) | Nhanh                         | Không bao giờ dùng cho Production |
| SSH Tunneling          | Tốt                       | Tệ (Khó xem trên Mobile)      | Phù hợp dev cục bộ                |
| **Nginx + Basic Auth** | **Cực Tốt**               | **Tuyệt Vời (Có popup pass)** | **Chuẩn Kiến Trúc Cloud**         |

---

## Chương 4: Triển Khai Containerization (Docker Pipeline)

### 1. Pipeline Vận Chuyển Dữ Liệu

Dùng `rsync` để đồng bộ hóa mã nguồn cực nhanh từ Arch Linux lên VPS, bỏ qua các file thừa.

```bash
# Đẩy code lên mây (Tối đi ngủ)
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='*.so' --exclude='.git' ./ kiet_dev@68.183.23.220:/home/kiet_dev/FlappyBird_RL/

# Thu hoạch model (Sáng hôm sau)
rsync -avz kiet_dev@68.183.23.220:/home/kiet_dev/FlappyBird_RL/models/ ./models/
```

### 2. Cấu Trúc Dockerfile (Giải Quyết Đụng Độ glibc & Go Version)

Đóng gói Go Compiler và Python vào chung một Container để độc lập hoàn toàn với OS của VPS.

```dockerfile
# Sử dụng base image golang bản mới nhất khớp với go.mod
FROM golang:1.26-bookworm

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv
WORKDIR /app
COPY . .
# Xóa bản build từ Arch Linux và build lại bằng Debian
RUN rm -f flappy_rl.so
RUN go build -buildmode=c-shared -o flappy_rl.so ./cmd/rl_bridge

RUN python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["/app/.venv/bin/python", "resume-train.py"]
```

### 3. Khởi Động Tiến Trình Background

Sử dụng cờ `-v` (Volume) để chọc ống hút nối từ trong container ra ngoài ổ cứng thật của Droplet.

```bash
docker build -t flappy_ai .
docker run -d --name flappy_train --restart unless-stopped -p 127.0.0.1:6006:6006 -v $(pwd)/models:/app/models flappy_ai
```

---

## Chương 5: Nhật Ký Bắt Bug & Khắc Phục Sự Cố

Xuyên suốt quá trình, hệ thống đã gặp và xử lý các lỗi kiến trúc & công cụ sau:

1. **`zsh: no matches found: stable-baselines3[extra]`**
   - _Nguyên nhân:_ Terminal Zsh hiểu nhầm dấu `[]` là cú pháp tìm file (globbing).
   - _Cách fix:_ Bọc thư viện vào ngoặc kép: `pip install "stable-baselines3[extra]"`.
2. **`xterm-kitty: unknown terminal type` khi SSH**
   - _Nguyên nhân:_ VPS Ubuntu không có từ điển màu sắc của terminal Kitty.
   - _Cách fix:_ Dùng tính năng bọc lệnh của Kitty: `kitty +kitten ssh kiet_dev@ip` để nó tự đồng bộ terminfo.
3. **`SyntaxError: import ctypes` ở cuối file Python**
   - _Nguyên nhân:_ Lỗi Copy-Paste dính dòng chữ vào cuối hàm `print`.
   - _Cách fix:_ Xóa phần text thừa ở cuối block `try-except`.
4. **`No dashboards are active` trên TensorBoard**
   - _Nguyên nhân:_ Quá trình ghi file log bị I/O Buffering, hoặc chỉ sai đường dẫn `--logdir`.
   - _Cách fix:_ Đợi AI chạy đủ 1 vòng Rollout (2048 steps) để xả buffer xuống đĩa.
5. **`docker: Error response from daemon: pull access denied`**
   - _Nguyên nhân:_ Chạy lệnh `docker run` trước khi tạo Image.
   - _Cách fix:_ Phải chạy lệnh `docker build -t flappy_ai .` để đúc khuôn trước.
6. **`go.mod requires go >= 1.26.2 (running go 1.22.12)`**
   - _Nguyên nhân:_ Lệch pha môi trường. Local dùng Go 1.26, nhưng Dockerfile cấu hình lấy `golang:1.22`.
   - _Cách fix:_ Nâng cấp base image trong Dockerfile thành `FROM golang:1.26-bookworm`.
7. **`Failed to restart sshd.service`**
   - _Nguyên nhân:_ Gọi sai tên dịch vụ. `sshd` là tên trên Arch/CentOS.
   - _Cách fix:_ Trên Ubuntu, dùng lệnh `sudo systemctl restart ssh`.

---

_Tài liệu được đúc kết từ quá trình thực chiến - Kiến trúc hệ thống luôn là việc trade-off để chọn ra con đường tối ưu nhất!_
