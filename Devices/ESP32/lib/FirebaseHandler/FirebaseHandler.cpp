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
bool FirebaseHandler::createSessionFromFaceDetection(const String &faceUrl, const String &plateUrl, const String &plateNumber, const String &gate, String &sessionID)
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
    doc.set("fields/platenumber/stringValue", plateNumber);

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

bool FirebaseHandler::updateSessionIsOut(const String &sessionID)
{
    String path = COLLECTION_SESSION;
    path.concat("/");
    path.concat(sessionID);

    FirebaseJson patchDoc;
    patchDoc.set("fields/isOut/booleanValue", true);

    if (Firebase.Firestore.patchDocument(&fbdo, FIREBASE_PROJECT_ID, "", path.c_str(), patchDoc.raw(), "isOut"))
    {
        Serial.println("[Firebase] Cập nhật isOut thành công.");
        return true;
    }
    else
    {
        Serial.print("[ERROR] Cập nhật isOut thất bại: ");
        Serial.println(fbdo.errorReason());
        return false;
    }
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

// Tìm session IN theo biển số xe
bool FirebaseHandler::findInSessionByPlate(const String &plateNumber, String &foundSessionID, String &foundFaceUrl, bool &isOut)
{
    FirebaseJson field1, field2, value1, value2;
    FirebaseJson fieldFilter1, fieldFilter2, filter1, filter2;
    FirebaseJson compositeFilter, where, structuredQuery;
    FirebaseJsonArray filtersArray;

    // Lồng field & value cho filter1
    field1.set("fieldPath", "platenumber");
    value1.set("stringValue", plateNumber);
    fieldFilter1.set("field", field1);
    fieldFilter1.set("op", "EQUAL");
    fieldFilter1.set("value", value1);
    filter1.set("fieldFilter", fieldFilter1);

    // Lồng field & value cho filter2
    field2.set("fieldPath", "gate");
    value2.set("stringValue", "In");
    fieldFilter2.set("field", field2);
    fieldFilter2.set("op", "EQUAL");
    fieldFilter2.set("value", value2);
    filter2.set("fieldFilter", fieldFilter2);

    // Mảng filters
    filtersArray.add(filter1);
    filtersArray.add(filter2);

    // compositeFilter
    compositeFilter.set("op", "AND");
    compositeFilter.set("filters", filtersArray);

    // where
    where.set("compositeFilter", compositeFilter);

    // from
    FirebaseJson from;
    from.set("collectionId", COLLECTION_SESSION);

    // orderBy timestamp desc
    FirebaseJson orderByField;
    orderByField.set("fieldPath", "timestamp");

    FirebaseJson orderBy;
    orderBy.set("field", orderByField);
    orderBy.set("direction", "DESCENDING");

    FirebaseJsonArray orderByArray;
    orderByArray.add(orderBy);

    // structuredQuery
    structuredQuery.add("from", from);
    structuredQuery.set("where", where);
    structuredQuery.set("orderBy", orderByArray);
    structuredQuery.set("limit", 1);

    if (Firebase.Firestore.runQuery(&fbdo, FIREBASE_PROJECT_ID, "", "", &structuredQuery))
    {
        FirebaseJsonArray resultArray;
        resultArray.setJsonArrayData(fbdo.payload());

        if (resultArray.size() > 0)
        {
            FirebaseJsonData jsonData;
            if (resultArray.get(jsonData, 0))
            {
                FirebaseJson wrapperJson;
                wrapperJson.setJsonData(jsonData.stringValue);

                FirebaseJson docJson;
                FirebaseJsonData temp;
                if (wrapperJson.get(temp, "document") && docJson.setJsonData(temp.stringValue))

                {
                    FirebaseJsonData docPathData;

                    if (docJson.get(docPathData, "name"))
                    {
                        String docPath = docPathData.stringValue;
                        int idx = docPath.lastIndexOf("/");
                        foundSessionID = docPath.substring(idx + 1);
                    }
                    else
                    {
                        Serial.println("[ERROR] Không lấy được document.name");
                    }

                    FirebaseJsonData fieldsData;
                    if (docJson.get(fieldsData, "fields"))
                    {
                        FirebaseJson fieldsJson;
                        fieldsJson.setJsonData(fieldsData.stringValue); // chứa toàn bộ fields

                        FirebaseJsonData faceUrlField;
                        if (fieldsJson.get(faceUrlField, "faceUrl"))
                        {
                            FirebaseJson faceUrlJson;
                            faceUrlJson.setJsonData(faceUrlField.stringValue);

                            FirebaseJsonData urlValue;
                            if (faceUrlJson.get(urlValue, "stringValue"))
                            {
                                foundFaceUrl = urlValue.stringValue;
                            }
                            else
                            {
                                Serial.println("[ERROR] Không lấy được stringValue trong faceUrl");
                            }
                        }
                        else
                        {
                            Serial.println("[ERROR] Không tìm thấy field faceUrl");
                        }
                        FirebaseJsonData isOutField;
                        if (fieldsJson.get(isOutField, "isOut"))
                        {
                            FirebaseJson isOutJson;
                            isOutJson.setJsonData(isOutField.stringValue);

                            FirebaseJsonData boolValue;
                            if (isOutJson.get(boolValue, "booleanValue"))
                            {
                                isOut = (boolValue.stringValue == "true");
                            }
                            else
                            {
                                Serial.println("[ERROR] Không lấy được booleanValue trong isOut");
                                isOut = false; // fallback
                            }
                        }
                        else
                        {
                            Serial.println("[ERROR] Không tìm thấy field isOut");
                            isOut = false; // fallback nếu field không tồn tại
                        }
                    }
                    else
                    {
                        Serial.println("[ERROR] Không lấy được fields từ docJson");
                    }

                    Serial.println("[DEBUG] Thoát khỏi findInSessionByPlate");
                    return true;
                }
                else
                {
                    Serial.print("[ERROR] Lỗi khi parse JSON: ");
                    Serial.println(docJson.errorPosition());
                }
            }
        }
        else
        {
            Serial.println("[Firebase] Không tìm thấy session IN.");
        }
    }
    else
    {
        Serial.print("[Firebase] Lỗi runQuery: ");
        Serial.println(fbdo.errorReason());
        Serial.println("fbdo.payload():");
        Serial.println(fbdo.payload());
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

    if (Firebase.Firestore.getDocument(&fbdo, FIREBASE_PROJECT_ID, "", path.c_str(), ""))
    {
        FirebaseJson json;
        json.setJsonData(fbdo.payload());

        FirebaseJsonData availableField;
        if (json.get(availableField, "fields/available/integerValue") && availableField.success)
        {
            availableCount = availableField.intValue;
            Serial.print("[INFO] Số slot còn trống: ");
            Serial.println(availableCount);
            return true;
        }
        else
        {
            Serial.println("[ERROR] Không tìm thấy trường 'available'.");
        }
    }
    else
    {
        Serial.print("[ERROR] Không thể lấy tài liệu slotCounter: ");
        Serial.println(fbdo.errorReason());
    }

    return false;
}

bool FirebaseHandler::increaseAvailableSlot()
{
    String path = "ParkingMeta/slotCounter";

    if (Firebase.Firestore.getDocument(&fbdo, FIREBASE_PROJECT_ID, "", path.c_str(), "")) {
        FirebaseJson json;
        json.setJsonData(fbdo.payload());

        FirebaseJsonData availableField;
        if (json.get(availableField, "fields/available/integerValue") && availableField.success) {
            int currentAvailable = availableField.intValue;

            if (currentAvailable <= 0) {
                Serial.println("[INFO] Không còn chỗ trống.");
                return false;
            }

            int updatedAvailable = currentAvailable + 1;

            FirebaseJson patchDoc;
            patchDoc.set("fields/available/integerValue", updatedAvailable);

            if (Firebase.Firestore.patchDocument(&fbdo, FIREBASE_PROJECT_ID, "", path.c_str(), patchDoc.raw(), "available")) {
                Serial.print("[INFO] Đã cập nhật available còn lại: ");
                Serial.println(updatedAvailable);
                return true;
            } else {
                Serial.print("[ERROR] Lỗi khi cập nhật available: ");
                Serial.println(fbdo.errorReason());
            }
        } else {
            Serial.println("[ERROR] Không tìm thấy trường available.");
        }
    } else {
        Serial.print("[ERROR] Không thể lấy tài liệu slotCounter: ");
        Serial.println(fbdo.errorReason());
    }

    return false;
}

bool FirebaseHandler::decreaseAvailableSlot()
{
    String path = "ParkingMeta/slotCounter";

    if (Firebase.Firestore.getDocument(&fbdo, FIREBASE_PROJECT_ID, "", path.c_str(), "")) {
        FirebaseJson json;
        json.setJsonData(fbdo.payload());

        FirebaseJsonData availableField;
        if (json.get(availableField, "fields/available/integerValue") && availableField.success) {
            int currentAvailable = availableField.intValue;

            if (currentAvailable <= 0) {
                Serial.println("[INFO] Không còn chỗ trống.");
                return false;
            }

            int updatedAvailable = currentAvailable - 1;

            FirebaseJson patchDoc;
            patchDoc.set("fields/available/integerValue", updatedAvailable);

            if (Firebase.Firestore.patchDocument(&fbdo, FIREBASE_PROJECT_ID, "", path.c_str(), patchDoc.raw(), "available")) {
                Serial.print("[INFO] Đã cập nhật available còn lại: ");
                Serial.println(updatedAvailable);
                return true;
            } else {
                Serial.print("[ERROR] Lỗi khi cập nhật available: ");
                Serial.println(fbdo.errorReason());
            }
        } else {
            Serial.println("[ERROR] Không tìm thấy trường available.");
        }
    } else {
        Serial.print("[ERROR] Không thể lấy tài liệu slotCounter: ");
        Serial.println(fbdo.errorReason());
    }

    return false;
}
