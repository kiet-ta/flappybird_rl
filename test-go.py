import ctypes
import time

import numpy as np

print("--- BẮT ĐẦU TEST ---")

try:
    print("1. Đang nạp khối động cơ Go (.so)...")
    lib = ctypes.cdll.LoadLibrary("./flappy_rl.so")

    print("2. Đang kết nối InitEnv...")
    lib.InitEnv.argtypes = [ctypes.c_longlong]
    lib.InitEnv(int(time.time()))

    print("3. Đang cấp phát tấm bảng RAM (Zero-copy)...")
    buffer = np.zeros(6, dtype=np.float64)
    buffer_ptr = buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    print("4. Đang ép Go ghi đè vào RAM (ResetEnv)...")
    lib.ResetEnv.argtypes = [ctypes.POINTER(ctypes.c_double)]
    lib.ResetEnv(buffer_ptr)

    print(f"\n🎉 THÀNH CÔNG! Data từ Go trả về: {buffer}")
    print("Tọa độ chim hiện tại: Y =", buffer[0])

except Exception as e:
    print(f"❌ Lỗi rồi sếp ơi: {e}")
