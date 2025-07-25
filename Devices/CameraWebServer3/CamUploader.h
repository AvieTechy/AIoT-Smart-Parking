#ifndef CAM_UPLOADER_H
#define CAM_UPLOADER_H

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "esp_camera.h"


class CamUploader {
public:
  void connectWiFi(const char* ssid, const char* password);
  bool initCamera();
  bool captureAndUpload(String& imageUrlOut); 


private:
  const char* uploadUrl = "https://api.cloudinary.com/v1_1/dc3jq3pit/image/upload";
  const char* uploadPreset = "esp32-cam";
};

#endif
