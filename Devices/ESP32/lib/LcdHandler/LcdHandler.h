#ifndef LCD_HANDLER_H
#define LCD_HANDLER_H

#include <Arduino.h>
#include <LiquidCrystal_I2C.h>

class LcdHandler {
public:
    LcdHandler(uint8_t lcd_addr = 0x27, uint8_t cols = 16, uint8_t rows = 2);

    void begin();
    void clear();
    void printLine(const String &text, uint8_t line = 0);
    void scrollText(const String &text, uint8_t line = 0, unsigned int delayMs = 200);
    void printCentered(const String &text, uint8_t line = 0);
    void printWrapped(const String &text);

private:
    LiquidCrystal_I2C lcd;
    uint8_t numCols;
    uint8_t numRows;
};

#endif 
