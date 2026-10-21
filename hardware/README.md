# ESP32 Medicine Dispenser - A to Z Hardware Setup Guide

This guide covers absolutely everything you need to do once you have your physical ESP32 and RC522 reader in hand.

## Step A: Prepare the Hardware & Wiring
You will need your ESP32, the RC522 (MFRC522) NFC reader, 5 LEDs, 5 Resistors (e.g., 330Ω), and a breadboard.

### 1. Wire the RC522 (NFC Reader)
The RC522 uses the SPI protocol. Connect it directly to the ESP32:
* **3.3V** → **3V3** (CRITICAL: Do not connect to 5V or you will fry the reader)
* **GND** → **GND**
* **RST** → **GPIO 22**
* **SDA (SS)** → **GPIO 21**
* **MOSI** → **GPIO 23**
* **MISO** → **GPIO 19**
* **SCK** → **GPIO 18**

### 2. Wire the Dispensing LEDs
Connect the long leg (Anode) of each LED to the GPIO pin, and the short leg (Cathode) through a resistor to **GND**.
* **Medicine 1 LED** (Blue) → **GPIO 25**
* **Medicine 2 LED** (Yellow) → **GPIO 26**
* **Medicine 3 LED** (White) → **GPIO 27**
* **Success LED** (Green) → **GPIO 13**
* **Error LED** (Red) → **GPIO 14**

---

## Step B: Prepare the Software Environment (Arduino IDE)
1. Download and install the [Arduino IDE](https://www.arduino.cc/en/software).
2. Open the IDE, go to **File > Preferences**, and paste this URL into the "Additional Boards Manager URLs" box: `https://dl.espressif.com/dl/package_esp32_index.json`
3. Go to **Tools > Board > Boards Manager**, search for `esp32`, and install it.
4. Go to **Tools > Board** and select **ESP32 Dev Module**.

---

## Step C: Install the Required Libraries
In the Arduino IDE, go to **Sketch > Include Library > Manage Libraries...** and search for and install:
1. **`MFRC522`** (by GithubCommunity)
2. **`ArduinoJson`** (by Benoit Blanchon, install version 6.x or 7.x)

---

## Step D: Configure the Firmware Code
1. Open the `hardware/esp32_firmware/esp32_firmware.ino` file in the Arduino IDE.
2. At the top of the file, fill in your exact **Wi-Fi Name (SSID)** and **Wi-Fi Password**.
3. **Find your Computer's Local IP**:
   * Open a command prompt on your PC and type `ipconfig` (Windows) or `ifconfig` (Mac/Linux). Look for the IPv4 Address (e.g., `192.168.1.5`).
   * Update the `API_BASE_URL` in the code to point to your computer's IP address (e.g., `"http://192.168.1.5:9001"`). Do NOT use `localhost`.

---

## Step E: Flash the ESP32
1. Plug the ESP32 into your computer using a micro-USB/USB-C data cable.
2. In the Arduino IDE, go to **Tools > Port** and select the COM port that appeared.
3. Click the **Upload** button (the right arrow `->` at the top left).
4. *Note: If it gets stuck at "Connecting...", press and hold the "BOOT" button on the physical ESP32 board until it starts writing.*

---

## Step F: Testing End-to-End
1. Open the **Serial Monitor** in the Arduino IDE (magnifying glass icon in the top right). Set the baud rate in the bottom right corner to **115200**.
2. Make sure your FastAPI backend server is running on your computer (`uvicorn backend.main:app --port 9001 --host 0.0.0.0`). *(Note the `--host 0.0.0.0` is required so your PC accepts connections from the ESP32)*.
3. Watch the Serial Monitor. It should say `Wi-Fi connected!` and `Scan a Patient NFC Card...`
4. Tap an NFC card to the RC522 reader.
5. The ESP32 will instantly print the card's UID, ping your backend, and light up the correct Medicine LEDs for 3 seconds!
