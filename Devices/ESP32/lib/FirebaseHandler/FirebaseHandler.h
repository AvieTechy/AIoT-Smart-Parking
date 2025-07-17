#pragma once
#include <Firebase_ESP_Client.h>
#include <Arduino.h>

class FirebaseHandler {
    private:
        FirebaseData fbdo;
        FirebaseAuth auth;
        FirebaseConfig config;
    
    public:
        void begin();
        bool createSessionFromFaceDetection(const String& faceUrl, const String& plateUrl, const String& gate, String& sessionID);
        bool checkNewSession(String& sessionID);
        bool getSessionData(const String& sessionID, String& gate, String& timestamp);
        bool createMatchingDoc(const String& sessionID, String& createdDocID);
        bool waitForMatching(const String& docID, bool& result);
        void resetTrigger();
        bool getAvailableSlotCount(int &availableCount);

};