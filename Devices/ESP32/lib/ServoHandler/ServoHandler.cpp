#include "ServoHandler.h"

void ServoHandler::begin(int pin) {
    servoPin = pin;
    servo.setPeriodHertz(50);  
    servo.attach(servoPin, 500, 2400); 
    close();
}

void ServoHandler::open() {
    servo.write(90);
}

void ServoHandler::close() {
    servo.write(0);
}
