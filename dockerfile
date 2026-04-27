# Dùng base image của Golang chuẩn (Debian Bookworm) để có sẵn môi trường C/C++ (CGO)
FROM golang:1.22-bookworm

# Cài đặt Python 3 và môi trường ảo
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# Set thư mục làm việc bên trong Container
WORKDIR /app

# Bốc toàn bộ code từ ngoài copy vào trong Container
COPY . .

# XÓA file .so cũ (nếu có copy nhầm) để tránh đụng độ hệ điều hành
RUN rm -f flappy_rl.so

# BÍ QUYẾT KIẾN TRÚC: Build lại file .so từ đầu ngay bên trong môi trường chuẩn của Debian
RUN go build -buildmode=c-shared -o flappy_rl.so ./cmd/rl_bridge

# Setup môi trường Python venv độc lập bên trong Container
RUN python3 -m venv .venv
RUN .venv/bin/pip install --upgrade pip
RUN .venv/bin/pip install -r requirements.txt

# Bật cờ này để xem log realtime của Python không bị nghẽn
ENV PYTHONUNBUFFERED=1

# Lệnh cuối cùng: Tự động chạy file resume-train.py khi Container khởi động
CMD ["/app/.venv/bin/python", "resume-train.py"]
