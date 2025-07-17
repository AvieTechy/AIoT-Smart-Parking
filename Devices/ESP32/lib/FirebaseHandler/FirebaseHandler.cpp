#include "FirebaseHandler.h"
#include <secrets.h>
#include <config.h>

void FirebaseHandler::begin()
{
    config.api_key = API_KEY;
    auth.user.email = USER_EMAIL;
    auth.user.password = USER_PASSWORD;

    setenv("TZ", "UTC-7", 1);
    tzset();

    configTime(0, 0, "pool.ntp.org", "time.nist.gov");

    time_t now;
    do
    {
        delay(100);
        now = time(nullptr);
    } while (now < 100000);

    Firebase.begin(&config, &auth);
    Firebase.reconnectWiFi(true);
}


// Tạo session mới
bool FirebaseHandler::createSessionFromFaceDetection(const String &faceUrl, const String& plateUrl, const String& gate, String &sessionID)
{
    sessionID = "sess_";
    sessionID.concat(String(millis()));

    FirebaseJson doc;
    doc.set("fields/sessionID/stringValue", sessionID);
    doc.set("fields/plateUrl/stringValue", plateUrl);
    doc.set("fields/faceUrl/stringValue", faceUrl);
    time_t now = time(nullptr);
    struct tm *tm_info = localtime(&now);
    char buf[30];
    strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%S", tm_info);
    String timestampISO = String(buf);
    timestampISO.concat(".000Z");

    doc.set("fields/timestamp/timestampValue", timestampISO);

    doc.set("fields/gate/stringValue", gate);
    doc.set("fields/isOut/booleanValue", false);
    doc.set("fields/faceIndex/stringValue", "");
    doc.set("fields/platenumber/stringValue", "");

    String fullPath = COLLECTION_SESSION;
    fullPath.concat("/");
    fullPath.concat(sessionID);

    if (Firebase.Firestore.createDocument(&fbdo, FIREBASE_PROJECT_ID, "", fullPath, doc.raw()))
    {
        FirebaseJson trigger;
        trigger.set("fields/status/booleanValue", true);
        trigger.set("fields/sessionID/stringValue", sessionID);
        String triggerPath = COLLECTION_TRIGGER "/" DOCUMENT_TRIGGER;
        Firebase.Firestore.patchDocument(&fbdo, FIREBASE_PROJECT_ID, "", triggerPath, trigger.raw(), "status,sessionID");

        return true;
    }
    else
    {
        Serial.println("[Firebase] Tạo session thất bại:");
        Serial.println(fbdo.errorReason()); 
    }
    return false;
}


// Kiểm tra session mới (tạm thời không dùng)
bool FirebaseHandler::checkNewSession(String &sessionID)
{
    String path = COLLECTION_TRIGGER "/" DOCUMENT_TRIGGER;
    if (Firebase.Firestore.getDocument(&fbdo, FIREBASE_PROJECT_ID, "", path.c_str(), ""))
    {
        FirebaseJson json;
        json.setJsonData(fbdo.payload());

        FirebaseJsonData statusField, sessionField;
        json.get(statusField, "fields/status/booleanValue");
        json.get(sessionField, "fields/sessionID/stringValue");

        if (statusField.success && statusField.boolValue && sessionField.success)
        {
            sessionID = sessionField.stringValue;
            return true;
        }
    }
    return false;
}

// Lấy dữ liệu session (tạm thời không dùng)
bool FirebaseHandler::getSessionData(const String &sessionID, String &gate, String &timestamp)
{
    String path = COLLECTION_SESSION;
    path.concat("/");
    path.concat(sessionID);
    if (Firebase.Firestore.getDocument(&fbdo, FIREBASE_PROJECT_ID, "", path.c_str(), ""))
    {
        FirebaseJson json;
        json.setJsonData(fbdo.payload());

        FirebaseJsonData gateField, timeField;
        json.get(gateField, "fields/gate/stringValue");
        json.get(timeField, "fields/timestamp/timestampValue");

        if (gateField.success && timeField.success)
        {
            gate = gateField.stringValue;
            timestamp = timeField.stringValue;
            return true;
        }
    }
    return false;
}

// Tạo document xác minh (MatchingVerify)
// Nếu tạo thành công:
// createdDocID trả về dạng "MatchingVerify/docID"
// Hàm trả true
// Nếu lỗi: trả false
bool FirebaseHandler::createMatchingDoc(const String &sessionID, String &createdDocID)
{
    FirebaseJson doc;
    doc.set("fields/sessionID/stringValue", sessionID);
    doc.set("fields/isMatch/booleanValue", false);

    if (Firebase.Firestore.createDocument(&fbdo, FIREBASE_PROJECT_ID, "", COLLECTION_VERIFY, doc.raw()))
    {
        FirebaseJson resp;
        resp.setJsonData(fbdo.payload());
        FirebaseJsonData docName;
        if (resp.get(docName, "name") && docName.success)
        {
            String fullPath = docName.stringValue;
            int idx = fullPath.lastIndexOf("/");
            createdDocID = COLLECTION_VERIFY;
            createdDocID.concat("/");
            createdDocID.concat(fullPath.substring(idx + 1));
            return true;
        }
    }
    return false;
}

// kiểm tra document vừa tạo ở trên để xem kết quả isMatch đã được cập nhật hay chưa.
bool FirebaseHandler::waitForMatching(const String &docID, bool &result)
{
    unsigned long start = millis();
    while (millis() - start < FIREBASE_TIMEOUT)
    {
        if (Firebase.Firestore.getDocument(&fbdo, FIREBASE_PROJECT_ID, "", docID.c_str(), ""))
        {
            FirebaseJson json;
            json.setJsonData(fbdo.payload());

            FirebaseJsonData field;
            if (json.get(field, "fields/isMatch/booleanValue") && field.success)
            {
                if (field.boolValue)
                {
                    Serial.println("Khuôn mặt trùng khớp, mở cổng");
                    result = true;
                    return true;
                }
                else
                {
                    Serial.println("Chưa xác minh xong...");
                }
            }
            else
            {
                Serial.println("Không tìm thấy trường isMatch.");
            }
        }
        else
        {
            Serial.println("Không lấy được document.");
        }
        delay(1000);
    }

    Serial.println("Hết thời gian chờ");
    result = false;
    return false;
}

void FirebaseHandler::resetTrigger()
{
    FirebaseJson json;
    json.set("fields/status/booleanValue", false);
    String path = COLLECTION_TRIGGER "/" DOCUMENT_TRIGGER;
    Firebase.Firestore.patchDocument(&fbdo, FIREBASE_PROJECT_ID, "", path.c_str(), json.raw(), "status");
}

bool FirebaseHandler::getAvailableSlotCount(int &availableCount)
{
    String path = "ParkingMeta/slotCounter";
    
    if (Firebase.Firestore.getDocument(&fbdo, FIREBASE_PROJECT_ID, "", path.c_str(), "")) {
        FirebaseJson json;
        json.setJsonData(fbdo.payload());

        FirebaseJsonData availableField;
        if (json.get(availableField, "fields/available/integerValue") && availableField.success) {
            availableCount = availableField.intValue;
            Serial.print("[INFO] Số slot còn trống: ");
            Serial.println(availableCount);
            return true;
        } else {
            Serial.println("[ERROR] Không tìm thấy trường 'available'.");
        }
    } else {
        Serial.print("[ERROR] Không thể lấy tài liệu slotCounter: ");
        Serial.println(fbdo.errorReason());
    }

    return false;
}
