#include "CamUploader.h"
#define CAMERA_MODEL_AI_THINKER
#include "CameraPins.h"

void CamUploader::connectWiFi(const char* ssid, const char* password) {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("ESP32-CAM IP address: ");
  Serial.println(WiFi.localIP());
}

bool CamUploader::initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  return esp_camera_init(&config) == ESP_OK;
}

bool CamUploader::captureAndUpload(String& imageUrlOut) {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Failed to capture image!");
    return false;
  }

  Serial.printf("Image captured. Size = %d bytes\n", fb->len);

  String boundary = "----WebKitFormBoundaryXyXyXy";
  String bodyStart =
    "--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"file\"; filename=\"esp32.jpg\"\r\n"
    "Content-Type: image/jpeg\r\n\r\n";

  String bodyEnd =
    "\r\n--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"upload_preset\"\r\n\r\n" +
    String(uploadPreset) + "\r\n" +
    "--" + boundary + "--\r\n";

  int totalLength = bodyStart.length() + fb->len + bodyEnd.length();

  WiFiClientSecure client;
  client.setInsecure();

  HTTPClient https;
  https.begin(client, uploadUrl);
  https.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
  https.addHeader("Content-Length", String(totalLength));

  uint8_t* payload = (uint8_t*)malloc(totalLength);
  if (!payload) {
    Serial.println("Not enough memory.");
    esp_camera_fb_return(fb);
    return false;
  }

  memcpy(payload, bodyStart.c_str(), bodyStart.length());
  memcpy(payload + bodyStart.length(), fb->buf, fb->len);
  memcpy(payload + bodyStart.length() + fb->len, bodyEnd.c_str(), bodyEnd.length());

  int httpCode = https.POST(payload, totalLength);
  free(payload);
  esp_camera_fb_return(fb);

  if (httpCode > 0) {
    Serial.printf("Upload success! HTTP code: %d\n", httpCode);
    String response = https.getString();
    Serial.println(response);

    DynamicJsonDocument doc(512);
    DeserializationError err = deserializeJson(doc, response);
    if (!err && doc.containsKey("secure_url")) {
      imageUrlOut = doc["secure_url"].as<String>();
      https.end();
      return true;
    } else {
      Serial.println("Failed to parse secure_url from response.");
    }
  } else {
    Serial.printf("Upload failed! Error: %s\n", https.errorToString(httpCode).c_str());
  }

  https.end();
  return false;
}

