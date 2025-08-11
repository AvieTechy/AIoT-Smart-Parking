import cv2
import time
import requests
import serial
import threading
import os
from datetime import datetime
from collections import deque

ESP32_CAM_IP = "192.168.1.69"
CAPTURE_URL = f"http://{ESP32_CAM_IP}/capture"
UART_PORT = "/dev/cu.usbserial-110"
UART_BAUD = 115200
CAPTURE_INTERVAL = 3  # giây
OUTPUT_DIR = "captured"
LABEL_FILE = "./artifacts/inference.csv"

detect_queue = deque()
bbox_queue = deque()
image_index = 276
running = True

def uart_reader():
    global detect_queue, bbox_queue
    try:
        ser = serial.Serial(UART_PORT, UART_BAUD, timeout=1)
        print(f"[UART] Đã mở {UART_PORT}")
    except Exception as e:
        print(f"[UART] Không thể mở UART: {e}")
        return

    current_bboxes = []

    while running:
        try:
            line = ser.readline().decode(errors='ignore').strip()
            if not line:
                continue
            print(f"[UART] {line}")

            if line.startswith("CAPTURE_DETECTED:"):
                try:
                    value = line.split(":")[1]
                    detect_queue.append(value)
                    bbox_queue.append(current_bboxes.copy())
                    print(f"[UART] DETECTED={value}, BBOXES={current_bboxes}")
                    current_bboxes.clear()
                except:
                    print("[UART] Không thể phân tích CAPTURE_DETECTED")

            elif line.startswith("BBOX:"):
                try:
                    parts = line.split(":")[1].split(",")
                    bbox = tuple(map(int, parts))
                    current_bboxes.append(bbox)
                except:
                    print("[UART] Không thể phân tích BBOX")

        except Exception as e:
            print(f"[UART] Lỗi đọc: {e}")

def capture_images():
    global image_index, detect_queue, bbox_queue

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(LABEL_FILE, "w") as label_file:
        label_file.write("filename,timestamp,detected,bboxes\n")

        while running:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                filename = f"img_{image_index:03d}.jpg"
                filepath = os.path.join(OUTPUT_DIR, filename)

                response = requests.get(CAPTURE_URL, timeout=5)
                if response.status_code == 200:
                    # Đợi tối đa 2 giây để nhận được detect, nếu không thì bỏ qua ảnh này
                    wait_time = 0
                    detect_value = None
                    while wait_time < 2:
                        if detect_queue:
                            detect_value = detect_queue.popleft()
                            break
                        time.sleep(0.1)
                        wait_time += 0.1

                    if detect_value is None:
                        print("[SKIP] Không nhận được nhãn DETECTED sau 2s → Bỏ ảnh và dữ liệu này.")
                        bbox_queue.clear()  # Xóa bboxes để tránh lỗi
                        continue

                    bboxes = bbox_queue.popleft() if bbox_queue else []

                    # Nếu detected là '?' thì cũng bỏ qua
                    if detect_value == '?':
                        print(f"[SKIP] DETECTED={detect_value} → Bỏ ảnh và dữ liệu này.")
                        bbox_queue.clear()  # Xóa bboxes để tránh lỗi
                        continue

                    with open(filepath, "wb") as f:
                        f.write(response.content)

                    print(f"[CAPTURE] {filename}, time={timestamp}, DETECTED={detect_value}, BBOXES={bboxes}")
                    bbox_str = "|".join(f"{x1},{y1},{x2},{y2}" for (x1, y1, x2, y2) in bboxes)
                    label_file.write(f"{filename},{timestamp},{detect_value},{bbox_str}\n")
                    label_file.flush()

                    image_index += 1
                    time.sleep(CAPTURE_INTERVAL)
                else:
                    print(f"[ERROR] HTTP {response.status_code}")
                    time.sleep(1)

            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(1)

if __name__ == "__main__":
    print(f"[INFO] Kết nối tới ESP32-CAM: {CAPTURE_URL}")
    uart_thread = threading.Thread(target=uart_reader, daemon=True)
    uart_thread.start()

    try:
        capture_images()
    except KeyboardInterrupt:
        print("\n[EXIT] Đang thoát...")
        running = False
