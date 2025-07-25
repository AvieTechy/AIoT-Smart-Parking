#include "CamHandler.h"
#include "ArduinoJson.h"

CamHandler::CamHandler(const char* ssid,
                       const char* password,
                       const char* detectUrl,
                       const char* triggerIp,
                       int triggerPort)
  : ssid_(ssid), password_(password),
    detectUrl_(detectUrl), triggerIp_(triggerIp),
    triggerPort_(triggerPort),
    uploadUrl_("https://api.cloudinary.com/v1_1/dc3jq3pit/image/upload"),
    uploadPreset_("esp32-cam"),
    cloudinaryRootCA_(R"EOF(
-----BEGIN CERTIFICATE-----
MIIEXjCCA0agAwIBAgITB3MSSkvL1E7HtTvq8ZSELToPoTANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTIyMDgyMzIyMjUzMFoXDTMwMDgyMzIyMjUzMFowPDEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEcMBoGA1UEAxMTQW1hem9uIFJT
QSAyMDQ4IE0wMjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALtDGMZa
qHneKei1by6+pUPPLljTB143Si6VpEWPc6mSkFhZb/6qrkZyoHlQLbDYnI2D7hD0
sdzEqfnuAjIsuXQLG3A8TvX6V3oFNBFVe8NlLJHvBseKY88saLwufxkZVwk74g4n
WlNMXzla9Y5F3wwRHwMVH443xGz6UtGSZSqQ94eFx5X7Tlqt8whi8qCaKdZ5rNak
+r9nUThOeClqFd4oXych//Rc7Y0eX1KNWHYSI1Nk31mYgiK3JvH063g+K9tHA63Z
eTgKgndlh+WI+zv7i44HepRZjA1FYwYZ9Vv/9UkC5Yz8/yU65fgjaE+wVHM4e/Yy
C2osrPWE7gJ+dXMCAwEAAaOCAVowggFWMBIGA1UdEwEB/wQIMAYBAf8CAQAwDgYD
VR0PAQH/BAQDAgGGMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEFBQcDAjAdBgNV
HQ4EFgQUwDFSzVpQw4J8dHHOy+mc+XrrguIwHwYDVR0jBBgwFoAUhBjMhTTsvAyU
lC4IWZzHshBOCggwewYIKwYBBQUHAQEEbzBtMC8GCCsGAQUFBzABhiNodHRwOi8v
b2NzcC5yb290Y2ExLmFtYXpvbnRydXN0LmNvbTA6BggrBgEFBQcwAoYuaHR0cDov
L2NydC5yb290Y2ExLmFtYXpvbnRydXN0LmNvbS9yb290Y2ExLmNlcjA/BgNVHR8E
ODA2MDSgMqAwhi5odHRwOi8vY3JsLnJvb3RjYTEuYW1hem9udHJ1c3QuY29tL3Jv
b3RjYTEuY3JsMBMGA1UdIAQMMAowCAYGZ4EMAQIBMA0GCSqGSIb3DQEBCwUAA4IB
AQAtTi6Fs0Azfi+iwm7jrz+CSxHH+uHl7Law3MQSXVtR8RV53PtR6r/6gNpqlzdo
Zq4FKbADi1v9Bun8RY8D51uedRfjsbeodizeBB8nXmeyD33Ep7VATj4ozcd31YFV
fgRhvTSxNrrTlNpWkUk0m3BMPv8sg381HhA6uEYokE5q9uws/3YkKqRiEz3TsaWm
JqIRZhMbgAfp7O7FUwFIb7UIspogZSKxPIWJpxiPo3TcBambbVtQOcNRWz5qCQdD
slI2yayq0n2TXoHyNCLEH8rpsJRVILFsg0jc7BaFrMnF462+ajSehgj12IidNeRN
4zl+EoNaWdpnWndvSpAEkq2P
-----END CERTIFICATE-----
)EOF") {
    // Connect to Wi-Fi
    WiFi.begin(ssid_, password_);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
}

void CamHandler::run() {
    _sendTrigger();

    String imageUrl;
    if (_captureAndUpload(imageUrl)) {
        _sendCloudinaryUrl(imageUrl);
    }
}

void CamHandler::_sendTrigger() {
    HTTPClient http;
    http.begin(detectUrl_);
    http.addHeader("Content-Type", "application/json");
    http.POST("{\"detected\":true}");
    http.end();
}

bool CamHandler::_captureAndUpload(String &outUrl) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("CamHandler: capture failed");
        return false;
    }

    // Prepare multipart form-data
    String boundary = "----WebKitFormBoundaryXyXyXy";
    String start = "--" + boundary + "\r\n"
                   "Content-Disposition: form-data; name=\"file\"; filename=\"esp32.jpg\"\r\n"
                   "Content-Type: image/jpeg\r\n\r\n";
    String preset = "\r\n--" + boundary + "\r\n"
                    "Content-Disposition: form-data; name=\"upload_preset\"\r\n\r\n" + uploadPreset_ + "\r\n";
    String end = "--" + boundary + "--\r\n";
    int totalLength = start.length() + fb->len + preset.length() + end.length();

    client_.setCACert(cloudinaryRootCA_);
    client_.setHandshakeTimeout(10);
    HTTPClient https;
    https.begin(client_, uploadUrl_);

    https.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);
    https.addHeader("Content-Length", String(totalLength));

    // Allocate payload buffer
    uint8_t* payload = (uint8_t*)malloc(totalLength);
    if (!payload) {
        esp_camera_fb_return(fb);
        https.end();
        return false;
    }

    uint8_t* ptr = payload;
    memcpy(ptr, start.c_str(), start.length()); ptr += start.length();
    memcpy(ptr, fb->buf, fb->len); ptr += fb->len;
    memcpy(ptr, preset.c_str(), preset.length()); ptr += preset.length();
    memcpy(ptr, end.c_str(), end.length());

    esp_camera_fb_return(fb);

    int code = https.POST(payload, totalLength);
    free(payload);

    if (code > 0) {
        String resp = https.getString();
        DynamicJsonDocument doc(1024);
        if (!deserializeJson(doc, resp) && doc.containsKey("secure_url")) {
            outUrl = doc["secure_url"].as<String>();
            https.end();
            return true;
        }
    }
    https.end();
    return false;
}

void CamHandler::_sendCloudinaryUrl(const String &url) {
    if (client_.connect(triggerIp_, triggerPort_)) {
        String j = String("{\"cam\":1,\"isFace\":true,\"url\":\"") + url + "\"}";
        client_.println(j);
        client_.stop();
    } else {
        Serial.println("CamHandler: TCP connect failed");
    }
}
