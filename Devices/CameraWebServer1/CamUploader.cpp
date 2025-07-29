#include "CamUploader.h"
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

const char* cloudinary_root_ca = R"EOF(
-----BEGIN CERTIFICATE-----
MIIF8TCCBNmgAwIBAgIQCeA8bRbCO57PXVwL9xDD5TANBgkqhkiG9w0BAQsFADA8
MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRwwGgYDVQQDExNBbWF6b24g
UlNBIDIwNDggTTA0MB4XDTI1MDcyNzAwMDAwMFoXDTI2MDgyNDIzNTk1OVowGzEZ
MBcGA1UEAwwQKi5jbG91ZGluYXJ5LmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEP
ADCCAQoCggEBALZ6ejC8ucm794CuoJrS66UlZCBgyVirkfEL+FZ7ChqHCSxR5h8x
nL5r2LKcOKWPIsgweTiPQOUdgRldFER/APHwxVqKFXDWlybqborPUvl11tEmXeOp
PM4+KbxPddKRxHmnBhK8qCs5zBYOvPgZfFJOhCsSCgTMFo09ABPnIri+Xnx0vHop
cR4HfcK15miQoXpOgnxZQvPb+dBbhJPgAIRh58ZfbzzsyqTC4FeDMpSRx3YWObdi
PXOldYkcBkuiv9J/R6YlOt92lVsVfSiJHNzGbeVmtQUhSNIoUk73S8FOqrpyI7G/
l9L92XXuPucFllfn06m8AXj4bEbDBW/6msUCAwEAAaOCAw4wggMKMB8GA1UdIwQY
MBaAFB9SkmFWglR/gWbYHT0KqjJch90IMB0GA1UdDgQWBBTiWzob/NkMJlWPEQgv
BKuyA+AvrzBJBgNVHREEQjBAghAqLmNsb3VkaW5hcnkuY29tgg4qLmltYWdlY29u
LmNvbYIMaW1hZ2Vjb24uY29tgg5jbG91ZGluYXJ5LmNvbTATBgNVHSAEDDAKMAgG
BmeBDAECATAOBgNVHQ8BAf8EBAMCBaAwEwYDVR0lBAwwCgYIKwYBBQUHAwEwOwYD
VR0fBDQwMjAwoC6gLIYqaHR0cDovL2NybC5yMm0wNC5hbWF6b250cnVzdC5jb20v
cjJtMDQuY3JsMHUGCCsGAQUFBwEBBGkwZzAtBggrBgEFBQcwAYYhaHR0cDovL29j
c3AucjJtMDQuYW1hem9udHJ1c3QuY29tMDYGCCsGAQUFBzAChipodHRwOi8vY3J0
LnIybTA0LmFtYXpvbnRydXN0LmNvbS9yMm0wNC5jZXIwDAYDVR0TAQH/BAIwADCC
AX8GCisGAQQB1nkCBAIEggFvBIIBawFpAHYA1219ENGn9XfCx+lf1wC/+YLJM1pl
4dCzAXMXwMjFaXcAAAGYSkSVOgAABAMARzBFAiBZSvQQfEkB67FeucK4CTbvBFSS
zpx1mORSWMDvagqFXgIhAJRRhnWfWVhr0coSZ8otBwurf4LpvudtOJznjuYwjx9h
AHcAwjF+V0UZo0XufzjespBB68fCIVoiv3/Vta12mtkOUs0AAAGYSkSVdgAABAMA
SDBGAiEApTYIVEjp4fjX99h6sonK7QDS8532GgBdorIt8BELodgCIQD/Q42hUMw5
BumS/KNSOCkTvOnDfXW/u0i8NDFX3BLclAB2AJROQ4f67MHvgfMZJCaoGGUBx9Nf
OAIBP3JnfVU3LhnYAAABmEpElYoAAAQDAEcwRQIgIlIIuirpG2fVsOF19pm4qV7z
xnr2KvAa5OH8udDGZesCIQDqqJiuudPupjUAoEtoAkEijflXc+NUJRx80U7tX3rZ
ZDANBgkqhkiG9w0BAQsFAAOCAQEARzntU7AQx/l43HPfGH41ztX/WWKoHVa6hLih
2JjphQ71KkJ2exPD7OMq5yJuXcCqdbbrs+GAJLdxlxpBofsgNtHCVwBA0JeQ8W0z
gwdCV+CCijou8wXEMgkjsMgRVCCHomCFwecFT2IQXr/VybpgNDTOgFNYgHffY56m
yLxqbaxwy5o4skVmRiyGWHjXAzD9q+URlK8lnfAsOm2T0L0grZYlUF6T7oE2I/Y1
smgF6XLQyWuF31uH1LNoMxPVkA4130fYkUgS0HPo24Ux3QloCjqmR6K5GpZezwEF
gEbPadCTGqdPqJMxlUWf11fYKER/9ywBeRo2uM6heD0B+MqaGg==
-----END CERTIFICATE-----
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
)EOF";


void CamUploader::connectWiFi(const char* ssid, const char* password) {
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
  Serial.println("========== BẮT ĐẦU QUY TRÌNH UPLOAD ==========");

  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[ERROR] Không thể chụp ảnh.");
    return false;
  }

  Serial.printf("[INFO] Ảnh đã chụp: %d bytes\n", fb->len);

  const char* server = "172.20.10.9";
  const int port = 8000;
  const char* path = "/postCloud/upload";
  String boundary = "----esp32boundary";
  String contentType = "multipart/form-data; boundary=" + boundary;

  String head = "--" + boundary + "\r\n";
  head += "Content-Disposition: form-data; name=\"file\"; filename=\"esp32.jpg\"\r\n";
  head += "Content-Type: image/jpeg\r\n\r\n";

  String tail = "\r\n--" + boundary + "--\r\n";

  int contentLength = head.length() + fb->len + tail.length();

  WiFiClient client;
  if (!client.connect(server, port)) {
    Serial.println("[ERROR] Không thể kết nối tới server local.");
    esp_camera_fb_return(fb);
    return false;
  }

  // Gửi HTTP request header
  client.print(String("POST ") + path + " HTTP/1.1\r\n");
  client.print(String("Host: ") + server + "\r\n");
  client.print("Content-Type: " + contentType + "\r\n");
  client.print("Content-Length: " + String(contentLength) + "\r\n");
  client.print("Connection: close\r\n\r\n");

  // Gửi body: phần đầu
  client.print(head);

  // Gửi ảnh
  client.write(fb->buf, fb->len);

  // Gửi phần cuối
  client.print(tail);

  Serial.println("[DEBUG] Đã gửi multipart dữ liệu, chờ phản hồi...");

  // Đọc phản hồi
  String response;
  long timeout = millis() + 5000;
  while (client.connected() && millis() < timeout) {
    while (client.available()) {
      char c = client.read();
      response += c;
    }
  }
  client.stop();
  esp_camera_fb_return(fb);

  // Phân tích JSON trong body
  int jsonStart = response.indexOf('{');
  if (jsonStart >= 0) {
    String json = response.substring(jsonStart);
    StaticJsonDocument<512> doc;
    DeserializationError err = deserializeJson(doc, json);
    if (!err && doc.containsKey("url")) {
      imageUrlOut = doc["url"].as<String>();
      Serial.println("[INFO] Link ảnh:");
      Serial.println(imageUrlOut);
      return true;
    } else {
      Serial.println("[WARN] Phản hồi JSON không hợp lệ hoặc thiếu key 'url':");
      Serial.println(json);
    }
  } else {
    Serial.println("[ERROR] Không tìm thấy JSON trong phản hồi:");
    Serial.println(response);
  }

  return false;
}