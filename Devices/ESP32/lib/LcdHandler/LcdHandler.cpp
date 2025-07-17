#include "LcdHandler.h"

LcdHandler::LcdHandler(uint8_t lcd_addr, uint8_t cols, uint8_t rows)
    : lcd(lcd_addr, cols, rows), numCols(cols), numRows(rows) {}

void LcdHandler::begin() {
    lcd.init();
    lcd.backlight();
    lcd.clear();
}

void LcdHandler::clear() {
    lcd.clear();
}

void LcdHandler::printLine(const String &text, uint8_t line) {
    if (line >= numRows) return;

    lcd.setCursor(0, line);
    lcd.print(text);
    for (uint8_t i = text.length(); i < numCols; i++) {
        lcd.print(' ');
    }
}

void LcdHandler::printCentered(const String &text, uint8_t line) {
    if (line >= numRows) return;

    uint8_t padding = (numCols > text.length()) ? (numCols - text.length()) / 2 : 0;
    lcd.setCursor(0, line);

    for (uint8_t i = 0; i < padding; i++) {
        lcd.print(' ');
    }

    lcd.print(text);

    for (uint8_t i = padding + text.length(); i < numCols; i++) {
        lcd.print(' ');
    }
}

void LcdHandler::scrollText(const String &text, uint8_t line, unsigned int delayMs) {
    if (line >= numRows) return;

    uint8_t len = text.length();

    if (len <= numCols) {
        printLine(text, line);
        return;
    }

    for (uint8_t i = 0; i <= len - numCols; i++) {
        lcd.setCursor(0, line);
        lcd.print(text.substring(i, i + numCols));
        delay(delayMs);
    }

    delay(500);
}

void LcdHandler::printWrapped(const String &text) {
    clear();
    for (uint8_t i = 0; i < numRows; i++) {
        uint8_t startIdx = i * numCols;
        if (startIdx >= text.length()) break;

        String lineText = text.substring(startIdx, startIdx + numCols);
        printLine(lineText, i);
    }
}
