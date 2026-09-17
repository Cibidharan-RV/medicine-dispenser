# ESP32 Medicine Dispenser Integration

This directory contains the C++ firmware for the ESP32 microcontroller, which connects the physical Medicine Dispenser to our backend API.

## Requirements

### Hardware
1. **ESP32 Development Board**
2. **NFC/RFID Reader**: Standard RC522 (also known as MFRC522) module. *(Note: If you switch to a PN532 later, you will need to swap the `MFRC522` library for `Adafruit_PN532` and adjust the SPI/I2C initialization in the code).*
3. **LEDs & Resistors**: Used to simulate the dispensing mechanism. Each LED represents a unique medicine bin.
4. **Jumper Wires & Breadboard**

### Software (Arduino IDE)
You must install the following libraries via the Arduino Library Manager (`Sketch > Include Library > Manage Libraries`):
1. **`MFRC522`** by GithubCommunity (This is the official library for the RC522 module)
2. **`ArduinoJson`** by Benoit Blanchon (Version 6.x or 7.x, for parsing API responses)

## Wiring Diagram (ESP32 -> RC522)

The MFRC522 uses the SPI protocol. Connect it to the standard ESP32 SPI pins:

| RC522 Pin | ESP32 Pin | Description |
|-----------|-----------|-------------|
| 3.3V | 3V3 | Power (DO NOT CONNECT TO 5V) |
| RST | GPIO 22 | Reset Pin |
| GND | GND | Ground |
| MISO | GPIO 19 | Master In Slave Out |
| MOSI | GPIO 23 | Master Out Slave In |
| SCK | GPIO 18 | SPI Clock |
| SDA (SS)| GPIO 21 | Slave Select |

## Wiring Diagram (ESP32 -> Dispensing LEDs)

In this mock setup, an LED lighting up simulates a medicine being dispensed.

| Component | ESP32 Pin | Description |
|-----------|-----------|-------------|
| LED 1 (Medicine ID: 1) | GPIO 25 | Dispense indicator for Med 1 |
| LED 2 (Medicine ID: 2) | GPIO 26 | Dispense indicator for Med 2 |
| LED 3 (Medicine ID: 3) | GPIO 27 | Dispense indicator for Med 3 |
| Error LED (Red) | GPIO 14 | Flashes on API error or unauthorized card |
| Success LED (Green)| GPIO 13 | Flashes when dispensing is complete |

*Note: Always use an appropriate current-limiting resistor (e.g., 220Ω or 330Ω) in series with each LED connected to ground.*

## Configuration

Before flashing the code, open `esp32_firmware.ino` and update the following variables at the top of the file:
1. `WIFI_SSID`: Your local Wi-Fi network name.
2. `WIFI_PASSWORD`: Your local Wi-Fi password.
3. `API_BASE_URL`: The local IP address of your computer running the FastAPI backend (e.g., `http://192.168.1.5:9001`).
4. `HARDWARE_API_KEY`: Must match the key used in the backend (currently `super_secret_hardware_key_123`).

## Usage
1. Power on the ESP32. It will connect to Wi-Fi.
2. Tap a patient's NFC card to the RC522 module.
3. The ESP32 will read the UID, contact the backend `/dispensing/due` endpoint.
4. If there are schedules due, the ESP32 will light up the corresponding Medicine LED for 3 seconds.
5. It will then send a `POST /dispensing/dispense` to log the event in the database.
