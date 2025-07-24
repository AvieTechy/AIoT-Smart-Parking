#include <WiFi.h>
#include <ArduinoJson.h>
#include <FirebaseHandler.h>
#include "LcdHandler.h"
#include <ServoHandler.h>
#include <secrets.h>

WiFiServer server(1234);
FirebaseHandler firebase;
LcdHandler lcd;
ServoHandler servoMotor;

String faceUrl = "";
String plateUrl = "";
String gate = ""; // In or Out
bool readyToCreateSession = false;

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

void loop()
{
  WiFiClient client = server.available();
  if (client)
  {
    String msg = client.readStringUntil('\n');
    msg.trim();
    Serial.println(msg);
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

      if (faceUrl != "" && plateUrl != "")
      {
        readyToCreateSession = true;
      }
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
          bool success = firebase.createSessionFromFaceDetection(faceUrl, plateUrl, gate, sessionID);

          if (success)
          {
            servoMotor.open(); // Mở cổng
            delay(3000);  
            servoMotor.close(); // Đóng cổng sau 2 giây
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
      bool success = firebase.createSessionFromFaceDetection(faceUrl, plateUrl, gate, sessionID);

      if (success)
      {
        lcd.clear();
        lcd.printWrapped(sessionID);
      }
      else
      {
        lcd.printLine("Session failed.", 0);
      }

      String createdDocID;
      if (firebase.createMatchingDoc(sessionID, createdDocID))
      {
        bool result;
        if (firebase.waitForMatching(createdDocID, result))
        {
          String matchText = "Match: ";
          matchText.concat(result ? "Yes" : "No");
          lcd.printLine(matchText, 0);
          if (result)
          {
            servoMotor.open(); 
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
          lcd.printLine("Timeout waiting", 0);
          delay(3000);
        }
      }
      lcd.clear();
      firebase.resetTrigger();
      faceUrl = "";
      plateUrl = "";
      gate = "";
    }
  }

  delay(100);
  lcd.printCentered("VisPark", 0);
}
