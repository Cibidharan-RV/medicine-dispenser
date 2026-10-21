#include <SPI.h>
#include <MFRC522.h>

// Pin definitions according to the ESP32 setup guide
#define RST_PIN   22
#define SS_PIN    21

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(115200);   
  delay(3000); // Wait 3 seconds for Serial Monitor to open!

  Serial.println(F("\n======================================="));
  Serial.println(F("NFC Reader (RC522) Connection Test"));
  Serial.println(F("======================================="));
  
  Serial.println(F("Initializing SPI bus..."));
  SPI.begin();            
  
  Serial.println(F("Initializing RC522 Reader..."));
  mfrc522.PCD_Init();     
  
  Serial.println(F("Reading Firmware Version from RC522..."));
  byte v = mfrc522.PCD_ReadRegister(mfrc522.VersionReg);

  Serial.print(F("Firmware Version: 0x"));
  Serial.print(v, HEX);
  Serial.println();

  if (v == 0x00 || v == 0xFF) {
    Serial.println(F("\n❌ ERROR: COMMUNICATION FAILED! ❌"));
    Serial.println(F("The ESP32 cannot talk to the NFC reader."));
    Serial.println(F("Please check the following wires:"));
    Serial.println(F("1. Is 3.3V connected correctly? (DO NOT use 5V!)"));
    Serial.println(F("2. Is GND connected correctly?"));
    Serial.println(F("3. SCK  (Clock)  must be on GPIO 18"));
    Serial.println(F("4. MISO (Input)  must be on GPIO 19"));
    Serial.println(F("5. MOSI (Output) must be on GPIO 23"));
    Serial.println(F("6. SDA  (SS)     must be on GPIO 21"));
    Serial.println(F("7. RST  (Reset)  must be on GPIO 22"));
  } else if (v == 0x91 || v == 0x92 || v == 0x88) {
    Serial.println(F("\n✅ SUCCESS: READER DETECTED! ✅"));
    Serial.println(F("Your wiring is 100% correct."));
    mfrc522.PCD_DumpVersionToSerial(); 
  } else {
    Serial.println(F("\n⚠️ WARNING: Unknown Firmware Version."));
    Serial.println(F("The wiring might be loose, or this is a clone chip."));
  }
  
  Serial.println(F("=======================================\n"));
}

void loop() {
  // We don't need to do anything in the loop for a pure connection test.
}
