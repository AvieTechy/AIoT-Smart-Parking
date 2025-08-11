#pragma once
#include <ESP32Servo.h>

class ServoHandler {
    private:
        Servo servo;
        int servoPin;
    public:
        void begin(int pin);
        void open();
        void close();
};