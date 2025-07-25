// CamHandler.h
#ifndef CAM_HANDLER_H
#define CAM_HANDLER_H

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "esp_camera.h"

class CamHandler {
public:
    // Constructor: connects Wi-Fi and stores endpoints
    CamHandler(const char* ssid,
               const char* password,
               const char* detectUrl,
               const char* triggerIp,
               int triggerPort);

    // Called when a face is detected in stream_handler
    void run();

private:
    void _sendTrigger();
    bool _captureAndUpload(String &outUrl);
    void _sendCloudinaryUrl(const String &url);

    const char* ssid_;
    const char* password_;
    const char* detectUrl_;
    const char* triggerIp_;
    int         triggerPort_;
    WiFiClientSecure client_;

    // Cloudinary configuration
    const char* uploadUrl_;
    const char* uploadPreset_;
    const char* cloudinaryRootCA_;
};

#endif // CAM_HANDLER_H
