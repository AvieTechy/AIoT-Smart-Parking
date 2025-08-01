#include <WiFi.h>
#include <ArduinoJson.h>
#include <FirebaseHandler.h>
#include "LcdHandler.h"
#include <ServoHandler.h>
#include <secrets.h>
#include <HTTPClient.h>

WiFiServer server(1234);
FirebaseHandler firebase;
LcdHandler lcd;
ServoHandler servoMotor;

String faceUrl = "";
String plateUrl = "";
String gate = ""; // In or Out
String plateNumber = "";
bool readyToCreateSession = false;
bool stopFlag = false;

unsigned long partialReceivedTime = 0;
const unsigned long partialTimeout = 6000;


void setup()
{
  Serial.begin(115200);
  lcd.begin();
  servoMotor.begin(26);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED)
  {
    lcd.printCentered("Connecting...", 0);
  }

  lcd.printCentered("WiFi connected!", 0);
  delay(1000);
  lcd.printWrapped(WiFi.localIP().toString());
  delay(1000);
  lcd.printCentered("VisPark", 0);

  firebase.begin();
  server.begin();
}

bool extractPlateFromURL(const String &imageUrl, String &outPlate)
{
  Serial.println(imageUrl);
  HTTPClient http;
  // http.begin("http://172.20.10.11:8000/ocr/");
  http.begin("http://172.20.10.9:8000/ocr/");
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<256> requestDoc;
  requestDoc["url"] = imageUrl;

  String requestBody;
  serializeJson(requestDoc, requestBody);

  int httpCode = http.POST(requestBody);

  if (httpCode == 200)
  {
    String payload = http.getString();
    Serial.println("[INFO] Server response: ");
    Serial.println(payload);

    StaticJsonDocument<64> responseDoc;
    DeserializationError error = deserializeJson(responseDoc, payload);

    if (error)
    {
      Serial.print("[ERROR] JSON parse failed: ");
      Serial.println(error.c_str());
      http.end();
      return false;
    }

    bool status = responseDoc.as<bool>();
    if (status)
    {
      Serial.println("[SUCCESS] Plate detection successful");
      http.end();
      return true;
    }
    else
    {
      Serial.println("[FAILURE] Plate detection failed");
      http.end();
      return false;
    }
  }

  http.end();
  return false;
}

bool matchFaces(const String &faceUrlIn, const String &faceUrlOut, bool &resultMatch)
{
  Serial.println("Matching faces...");
  HTTPClient http;
  http.begin("http://172.20.10.9:8000/face_matching/");
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<512> body;
  body["image1_path"] = faceUrlIn;
  body["image2_path"] = faceUrlOut;

  String reqBody;
  serializeJson(body, reqBody);

  int httpCode = http.POST(reqBody);
  if (httpCode == 200)
  {
    String payload = http.getString();
    Serial.println("[INFO] Match Faces response: ");
    Serial.println(payload);
    payload.trim();

    if (payload == "true")
    {
      resultMatch = true;
      http.end();
      return true;
    }
    else if (payload == "false")
    {
      resultMatch = false;
      http.end();
      return true;
    }
    else
    {
      Serial.println("[ERROR] Unexpected payload format.");
    }
  }
  else
  {
    Serial.printf("[ERROR] matchFaces HTTP error: %d\n", httpCode);
  }

  http.end();
  return false;
}

bool sendTriggerToCam(String serverUrl)
{
  faceUrl = "";
  plateUrl = "";

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");

  String payload = "{\"captureTrigger\": true}";

  int httpResponseCode = http.POST(payload);

  if (httpResponseCode > 0)
  {
    String response = http.getString();
    Serial.printf("[INFO] Trigger sent to camera, response: %s\n", response.c_str());
    Serial.printf(serverUrl.c_str());
    Serial.println();
    http.end();
    return true;
  }
  else
  {
    Serial.printf("[ERROR] Failed to send trigger to camera, HTTP error code: %d\n", httpResponseCode);
    Serial.printf(serverUrl.c_str());
    http.end();
    return false;
  }
}

void loop()
{
  WiFiClient client = server.available();
  if (client)
  {
    String msg = client.readStringUntil('\n');
    msg.trim();
    Serial.println(msg);
    if (msg.length() == 0)
    {
      Serial.println("[WARNING] Bỏ qua message rỗng");
      client.stop();

      sendTriggerToCam("http://172.20.10.7/receive_detected");
      sendTriggerToCam("http://172.20.10.8/receive_detected");
      return;
    }

    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, msg);

    if (!error)
    {
      String cam = doc["cam"];
      bool isFace = doc["isFace"];
      String url = doc["url"];

      if (isFace)
      {
        faceUrl = url;
        gate = (cam == "1") ? "In" : "Out";
      }
      else
      {
        plateUrl = url;
      }

      if ((faceUrl != "" && plateUrl == "") || (plateUrl != "" && faceUrl == ""))
      {
        partialReceivedTime = millis();
      }
      if (faceUrl != "" && plateUrl != "")
      {
        Serial.println("Processing face and plate URLs...");
        String detectedPlate;
        if (extractPlateFromURL(plateUrl, detectedPlate))
        {
          plateNumber = detectedPlate;
        }
        else
        {
          Serial.println("Không nhận diện được biển số");
          lcd.printLine("Plate detection", 0);
          lcd.printLine("failed", 1);
          delay(1000);
          faceUrl = "";
          plateUrl = "";
          gate = "";
          sendTriggerToCam("http://172.20.10.7/receive_detected");
          sendTriggerToCam("http://172.20.10.8/receive_detected");
          return;
        }

        readyToCreateSession = true;
      }
    }
    else
    {
      Serial.print("[ERROR - DESER] Lỗi khi parse JSON: ");
      Serial.println(error.c_str());
      sendTriggerToCam("http://172.20.10.7/receive_detected");
      sendTriggerToCam("http://172.20.10.8/receive_detected");
      delay(1000);
    }

    client.stop();
  }
  // điều kiện để tạo session mới
  if (readyToCreateSession)
  {
    readyToCreateSession = false;

    // TRƯỜNG HỢP CỔNG VÀO (In)
    // kiểm tra số lượng slot trống
    // Nếu còn slot trống, tạo session mới
    // Nếu không còn slot trống, hiển thị thông báo đầy
    if (gate == "In")
    {
      int available;
      if (firebase.getAvailableSlotCount(available))
      {
        if (available == 0)
        {
          lcd.clear();
          lcd.printCentered("FULL SLOTS", 0);
          delay(1000);
        }
        else
        {
          lcd.clear();
          String slotsText = "Slots left: ";
          slotsText.concat(String(available));
          lcd.printCentered(slotsText, 0);
          delay(500);

          String sessionID;
          bool success = firebase.createSessionFromFaceDetection(faceUrl, plateUrl, plateNumber, gate, sessionID);

          if (success)
          {
            servoMotor.open(); // Mở cổng
            delay(3000);
            firebase.decreaseAvailableSlot();
            servoMotor.close(); // Đóng cổng sau 3 giây
          }
          else
          {
            lcd.printLine("Session failed.", 0);
            delay(1000);
          }

          faceUrl = "";
          plateUrl = "";
          gate = "";
        }
      }
      else
      {
        lcd.printLine("Error checking", 0);
        lcd.printLine("slots.", 1);
      }
    }

    // TRƯỜNG HỢP CỔNG RA (Out)
    // Tạo session mới từ faceUrl và plateUrl

    // Xử lý tạm thời (chưa merge code):
    // Nếu thành công, tạo document MatchingVerify với sessionID và isMatch = false
    // Sau đó, chờ xác minh từ Firebase với hàm waitForMatching(), tự động cập nhật kết quả isMatch ở firebase
    // xác minh thành công, hiển thị "Match: Yes"
    // hoặc tự động để timeout => xác minh không thành công, hiển thị "Match: No"
    else if (gate == "Out")
    {
      String sessionID;
      bool success = firebase.createSessionFromFaceDetection(faceUrl, plateUrl, plateNumber, gate, sessionID);

      if (!success)
      {
        lcd.printLine("Session failed.", 0);
        delay(1000);
        return;
      }

      String matchedSessionID, matchedFaceUrl;
      bool isOut;
      if (firebase.findInSessionByPlate(plateNumber, matchedSessionID, matchedFaceUrl, isOut))
      {
        if (isOut)
        {
          lcd.printLine("Already out", 0);
          delay(2000);
          faceUrl = "";
          plateUrl = "";
          gate = "";
          return;
        }
        bool matchResult;
        Serial.println(matchedSessionID);
        bool matchFacesResult = matchFaces(matchedFaceUrl, faceUrl, matchResult);
        Serial.println(matchResult);
        if (matchFacesResult)
        {
          String text = matchResult ? "Match: Yes" : "Match: No";
          lcd.printLine(text, 0);
          if (matchResult)
          {
            firebase.updateSessionIsOut(matchedSessionID);
            servoMotor.open();
            lcd.printLine("Opening gate...", 1);
            firebase.increaseAvailableSlot();
            delay(3000);
            servoMotor.close();
          }
          else
          {
            lcd.printLine("Please try again", 1);
            delay(3000);
          }
        }
        else
        {
          lcd.printLine("Match API failed", 0);
          delay(3000);
        }
      }
      else
      {
        lcd.printLine("No matching session", 0);
        delay(2000);
      }

      lcd.clear();
      firebase.resetTrigger();
      faceUrl = "";
      plateUrl = "";
      gate = "";
    }
    sendTriggerToCam("http://172.20.10.7/receive_detected");
    sendTriggerToCam("http://172.20.10.8/receive_detected");
  }

  // Reset nếu chỉ có 1 trong 2 URL và đã quá timeout
  if (((faceUrl != "" && plateUrl == "") || (plateUrl != "" && faceUrl == "")) &&
      (millis() - partialReceivedTime > partialTimeout))
  {
    Serial.println("[WARNING] Timeout waiting for second URL. Resetting...");

    faceUrl = "";
    plateUrl = "";
    gate = "";
    partialReceivedTime = 0;

    lcd.clear();
    lcd.printLine("Timeout", 0);
    lcd.printLine("Resetting...", 1);

    sendTriggerToCam("http://172.20.10.7/receive_detected");
    sendTriggerToCam("http://172.20.10.8/receive_detected");
    delay(2000);
  }

  delay(100);
  lcd.printCentered("VisPark", 0);
}
