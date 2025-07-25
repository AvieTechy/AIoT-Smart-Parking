#include "ServoHandler.h"

void ServoHandler::begin(int pin) {
    servoPin = pin;
    servo.attach(servoPin); 
    close();
}

void ServoHandler::open() {
    servo.write(90);
}

void ServoHandler::close() {
    servo.write(0);
}
