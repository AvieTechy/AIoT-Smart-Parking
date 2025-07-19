#include "CamUploader.h"
#include "Secrets.h"
#include <WiFi.h>

CamUploader uploader;
WiFiClient client;

// ========== SET UP WIFI + IP ESP32 TRUNG TÂM
const char* server_ip = "172.20.10.6";  // IP của ESP32 trung tâm - đổi theo esp32 trung tâm
const int server_port = 1234;


// ========== BIẾN LƯU TRẠNG THÁI DETECT
bool DETECTED_FACE = false;        // kết quả detect, khi nó true thì gửi tín hiệu là CAM còn lại và chụp
bool triggerFromOtherCam = false;  // cam còn lại nếu nhận trigger thì biến này TRUE

// ========== SAU NÀY BỎ
unsigned long lastCaptureTime = 0;            // sau merge code thì bỏ
const unsigned long captureInterval = 10000;  // sau merge code thì bỏ


// ========== ID CAM, sẽ thay đổi giá trị ứng theo mỗi esp32-cam khi nạp code
#define CAMERA_ID "1"  //  (cam này ở phía trong của cổng vào)
// đổi thành "2" với cam còn lại


// DETECTED_FACE và triggerFromOtherCam trái ngược nhau
// ví dụ CAM #1 detect được face, nó sẽ chụp face và phát tín hiệu cho CAM #2 chụp plate
//   - DETECTED_FACE = true
//   - triggerFromOtherCam = false
//   =>
//   CAM #2 nhận được thì set triggerFromOtherCam true, DETECTED_FACE vẫn giữ nguyên là false
//   - DETECTED_FACE = false
//   - triggerFromOtherCam = true


void setup() {
  Serial.begin(115200);
  uploader.connectWiFi(WIFI_SSID, WIFI_PASS);

  if (!uploader.initCamera()) {
    Serial.println("[ESP32-CAM] Lỗi khởi tạo camera!");
    while (true)
      ;
  }
  Serial.println("ESP32-CAM ready");
}

void loop() {
  // xử lý detect: nếu detect được ==>> DETECTED_FACE = true và gửi trigger
  // trong lúc detect vẫn lắng nghe trigger: nếu nhận được trigger ==>> triggerFromOtherCam = true (DETECTED_FACE vẫn giữ nguyên là false)



  // ==== Mô phỏng detect: thay bằng detect thật sau khi merge ====
  DETECTED_FACE = (millis() - lastCaptureTime >= captureInterval);

  if (DETECTED_FACE) {
    triggerFromOtherCam = false;
    lastCaptureTime = millis();

    // TODO: gửi trigger sang cam còn lại
  }

  // ==== Nếu nhận trigger từ cam còn lại (phần này luôn chạy song song) ====
  // TODO: nếu có tín hiệu trigger từ cam khác:
  if (false) { /* nhận được trigger từ cam còn lại */       // để if (false) để nó không chạy lúc test thôi, merge thì thay logic vào
    triggerFromOtherCam = true;
    DETECTED_FACE = false;
  }





  // ==== Phần chụp hình và gửi đến esp32 trung tâm
  if (DETECTED_FACE || triggerFromOtherCam) {
    Serial.println("[ESP32-CAM] Đang chụp ảnh...");

    String imageUrl;
    if (uploader.captureAndUpload(imageUrl)) {
      Serial.printf("[ESP32-CAM] Upload thành công: %s\n", imageUrl.c_str());

      if (client.connect(server_ip, server_port)) {
        String json = "{";
        json += "\"cam\":\"" + String(CAMERA_ID) + "\",";
        json += "\"isFace\":" + String(DETECTED_FACE ? "true" : "false") + ",";
        json += "\"url\":\"" + imageUrl + "\"";
        json += "}";

        client.println(json);
        client.stop();
        

        // reset lại sau khi gửi 
        DETECTED_FACE = false;
        triggerFromOtherCam = false;

        Serial.println("[ESP32-CAM] Đã gửi URL ảnh qua TCP đến ESP32 trung tâm");
        Serial.println(json);
      } else {
        Serial.println("[ESP32-CAM] Không kết nối được với ESP32 trung tâm");
      }

    } else {
      Serial.println("[ESP32-CAM] Upload thất bại.");
    }

  } 

  delay(100);
}
