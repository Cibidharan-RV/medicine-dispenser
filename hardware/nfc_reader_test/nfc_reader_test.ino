#include <MFRC522.h>
#include <MFRC522Extended.h>
#include <deprecated.h>
#include <require_cpp11.h>

#include <SPI.h>
#include <MFRC522.h>

// Pin definitions according to the ESP32 setup guide
#define RST_PIN   22
#define SS_PIN    21

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(115200);   // Initialize serial communications
  delay(2000);            // Wait 2 seconds for Serial Monitor to open!

  SPI.begin();            // Init SPI bus
  mfrc522.PCD_Init();     // Init MFRC522
  delay(50);              // Give the clone chip extra time to boot
  
  // --- CLONE CHIP WORKAROUNDS ---
  // 1. Force the antenna to turn on (clones sometimes fail to do this automatically)
  mfrc522.PCD_AntennaOn();
  
  // 2. Force 100% ASK modulation (required by some 0x82 clones)
  mfrc522.PCD_WriteRegister(mfrc522.TxASKReg, 0x40);
  
  // 3. Set the antenna gain to absolute maximum
  mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);
  // ------------------------------

  delay(4);               // Optional delay
  mfrc522.PCD_DumpVersionToSerial();  // Show details of PCD - MFRC522 Card Reader details
  
  Serial.println(F("======================================="));
  Serial.println(F("NFC Reader Initialized successfully!"));
  Serial.println(F("Scan a card to see its UID printed here."));
  Serial.println(F("======================================="));
}

void loop() {
  // Look for new cards
  if ( ! mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Show UID on serial monitor
  Serial.print("Card UID: ");
  String uidString = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    // Format byte as hex with a leading zero if needed, and uppercase
    if(mfrc522.uid.uidByte[i] < 0x10) {
      Serial.print("0");
      uidString += "0";
    }
    Serial.print(mfrc522.uid.uidByte[i], HEX);
    uidString += String(mfrc522.uid.uidByte[i], HEX);
    
    // Add colon between bytes except for the last one
    if (i != mfrc522.uid.size - 1) {
      Serial.print(":");
      uidString += ":";
    }
  }
  
  uidString.toUpperCase();
  
  Serial.println();
  Serial.println("Formatted UID to copy: " + uidString);
  Serial.println("---------------------------------------");
  
  // Halt PICC to stop reading the same card over and over continuously
  mfrc522.PICC_HaltA();
}
