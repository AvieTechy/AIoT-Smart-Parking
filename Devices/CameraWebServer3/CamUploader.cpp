#include "CamUploader.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <esp_camera.h>
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// Structure to hold upload task parameters
struct UploadTaskParams {
  String uploadUrl;
  String uploadPreset;
  String* imageUrlOut;
  SemaphoreHandle_t semaphore;
};

// Initialize camera (unchanged)
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
  config.jpeg_quality = 15; // Increased to reduce memory usage
  config.fb_count = 1;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return false;
  }
  return true;
}

// Connect to WiFi with enhanced stability
void CamUploader::connectWiFi(const char* ssid, const char* password) {
  // Set static DNS to Google DNS
  WiFi.config(IPAddress(0, 0, 0, 0), IPAddress(0, 0, 0, 0), IPAddress(255, 255, 255, 0), IPAddress(8, 8, 8, 8));
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\nFailed to connect to WiFi!");
    return;
  }
  Serial.println("\nWiFi connected!");
  Serial.print("ESP32-CAM IP address: ");
  Serial.println(WiFi.localIP());
  Serial.printf("WiFi RSSI: %d dBm\n", WiFi.RSSI());
}

// Test server connectivity with retry and fallback IPs
bool testServerConnection(const char* host, int port = 443, int retries = 5) {
  WiFiClientSecure client;
  client.setCACert(nullptr); // Insecure, as requested
  client.setTimeout(5000); // 5-second timeout

  // List of fallback IPs for api.cloudinary.com (as of 2025, may change)
  IPAddress fallbackIPs[] = {
    IPAddress(44, 212, 198, 19),  // From your log
    IPAddress(104, 18, 191, 145), // Known Cloudinary IP
    IPAddress(104, 18, 190, 145)  // Alternative Cloudinary IP
  };
  int numFallbacks = 3;

  // Test DNS resolution
  IPAddress ip;
  Serial.print("Resolving DNS for ");
  Serial.println(host);
  if (WiFi.hostByName(host, ip)) {
    Serial.print("Resolved IP: ");
    Serial.println(ip);
  } else {
    Serial.println("DNS resolution failed!");
    ip = fallbackIPs[0]; // Use first fallback IP
    Serial.print("Using fallback IP: ");
    Serial.println(ip);
  }

  for (int i = 0; i < retries; i++) {
    Serial.printf("Attempt %d to connect to %s:%d (IP: %s)\n", i + 1, host, port, ip.toString().c_str());
    if (client.connect(ip, port)) {
      Serial.println("Connection to server successful!");
      client.stop();
      return true;
    }
    Serial.println("Connection to server failed!");
    if (i < numFallbacks - 1) {
      ip = fallbackIPs[i + 1]; // Try next fallback IP
      Serial.print("Switching to fallback IP: ");
      Serial.println(ip);
    }
    delay(1000); // Wait before retry
  }
  client.stop();
  return false;
}

// Capture image
camera_fb_t* captureImage() {
  Serial.println("[ESP32-CAM] Đang chụp ảnh...");
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Failed to capture image!");
    return nullptr;
  }
  Serial.printf("Image captured. Size = %d bytes\n", fb->len);
  return fb;
}

// Prepare payload for HTTP POST
uint8_t* preparePayload(camera_fb_t* fb, String& boundary, String& uploadPreset, size_t& totalLength) {
  String bodyStart =
    "--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"file\"; filename=\"esp32.jpg\"\r\n"
    "Content-Type: image/jpeg\r\n\r\n";

  String bodyEnd =
    "\r\n--" + boundary + "\r\n"
    "Content-Disposition: form-data; name=\"upload_preset\"\r\n\r\n" +
    uploadPreset + "\r\n" +
    "--" + boundary + "--\r\n";

  totalLength = bodyStart.length() + fb->len + bodyEnd.length();
  Serial.printf("Free heap before payload allocation: %d\n", ESP.getFreeHeap());
  uint8_t* payload = (uint8_t*)malloc(totalLength);
  if (!payload) {
    Serial.println("Not enough memory for payload.");
    return nullptr;
  }
  Serial.printf("Free heap after payload allocation: %d\n", ESP.getFreeHeap());

  memcpy(payload, bodyStart.c_str(), bodyStart.length());
  memcpy(payload + bodyStart.length(), fb->buf, fb->len);
  memcpy(payload + bodyStart.length() + fb->len, bodyEnd.c_str(), bodyEnd.length());

  return payload;
}

// Perform HTTP POST request
bool performUpload(WiFiClientSecure& client, HTTPClient& http, String& uploadUrl, String& boundary, uint8_t* payload, size_t totalLength, String& imageUrlOut) {
  // Verify WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected before upload!");
    return false;
  }

  // Extract host from uploadUrl
  String host = uploadUrl.substring(uploadUrl.indexOf("://") + 3);
  host = host.substring(0, host.indexOf("/"));
  if (!testServerConnection(host.c_str(), 443, 5)) {
    Serial.println("Cannot connect to server, aborting upload!");
    return false;
  }

  // Initialize HTTP connection
  client.setTimeout(15000); // Increased to 15-second timeout
  Serial.print("Attempting to connect to: ");
  Serial.println(uploadUrl);

  if (!http.begin(client, uploadUrl)) {
    Serial.println("Failed to initialize HTTPS connection!");
    client.stop();
    return false;
  }

  // Add headers
  http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
  http.addHeader("Content-Length", String(totalLength));

  // Perform POST
  Serial.println("Sending HTTP POST...");
  int httpCode = http.POST(payload, totalLength);
  Serial.printf("HTTP POST returned code: %d\n", httpCode);

  if (httpCode > 0) {
    String response = http.getString();
    Serial.println("Response: " + response);

    DynamicJsonDocument doc(512);
    DeserializationError err = deserializeJson(doc, response);
    if (!err && doc.containsKey("secure_url")) {
      imageUrlOut = doc["secure_url"].as<String>();
      http.end();
      client.stop();
      return true;
    } else {
      Serial.println("Failed to parse secure_url from response.");
    }
  } else {
    Serial.printf("Upload failed! Error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
  client.stop();
  return false;
}

// Task to handle image capture and upload
void uploadTask(void* params) {
  UploadTaskParams* taskParams = (UploadTaskParams*)params;
  String boundary = "----WebKitFormBoundaryXyXyXy";

  // Capture image
  camera_fb_t* fb = captureImage();
  if (!fb) {
    xSemaphoreGive(taskParams->semaphore);
    vTaskDelete(NULL);
    return;
  }

  // Prepare payload
  size_t totalLength;
  uint8_t* payload = preparePayload(fb, boundary, taskParams->uploadPreset, totalLength);
  if (!payload) {
    esp_camera_fb_return(fb);
    xSemaphoreGive(taskParams->semaphore);
    vTaskDelete(NULL);
    return;
  }

  // Perform upload
  WiFiClientSecure client;
  client.setCACert(nullptr); // Insecure, as requested
  HTTPClient http;
  bool success = performUpload(client, http, taskParams->uploadUrl, boundary, payload, totalLength, *taskParams->imageUrlOut);

  // Cleanup
  free(payload);
  esp_camera_fb_return(fb);
  xSemaphoreGive(taskParams->semaphore);
  vTaskDelete(NULL);
}

// Main function to start the upload task
bool CamUploader::captureAndUpload(String& imageUrlOut) {
  // Verify WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected! Attempting to reconnect...");
    connectWiFi("your_ssid", "your_password"); // Replace with your credentials
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Reconnection failed!");
      return false;
    }
  }

  // Create semaphore to synchronize task completion
  SemaphoreHandle_t semaphore = xSemaphoreCreateBinary();
  if (!semaphore) {
    Serial.println("Failed to create semaphore!");
    return false;
  }

  // Prepare task parameters
  UploadTaskParams params = {
    uploadUrl,
    uploadPreset,
    &imageUrlOut,
    semaphore
  };

  // Create task with increased stack size
  TaskHandle_t uploadTaskHandle;
  BaseType_t taskCreated = xTaskCreate(
    uploadTask,
    "UploadTask",
    8192, // Stack size
    &params,
    1,
    &uploadTaskHandle
  );

  if (taskCreated != pdPASS) {
    Serial.println("Failed to create upload task!");
    vSemaphoreDelete(semaphore);
    return false;
  }

  // Wait for task completion
  xSemaphoreTake(semaphore, portMAX_DELAY);
  vSemaphoreDelete(semaphore);
  return !imageUrlOut.isEmpty();
}