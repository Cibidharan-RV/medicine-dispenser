#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <ArduinoJson.h>

// ==========================================
// CONFIGURATION
// ==========================================
const char* WIFI_SSID = "Cibi's iPhone";
const char* WIFI_PASSWORD = "112233444";

// Use the local IP of your backend server (e.g., http://192.168.1.100:9001)
// Do NOT use localhost or 127.0.0.1, as the ESP32 is on a separate device.
const char* API_BASE_URL = "http://172.20.10.10:9001";
const char* HARDWARE_API_KEY = "super_secret_hardware_key_123";

// ==========================================
// PINS & HARDWARE
// ==========================================
#define RST_PIN         22
#define SS_PIN          21
MFRC522 mfrc522(SS_PIN, RST_PIN);

// Dispensing LEDs (Map Medicine IDs to GPIO pins)
const int LED_MED_1 = 25;
const int LED_MED_2 = 26;
const int LED_MED_3 = 27;

// Status LEDs
const int LED_ERROR = 14;
const int LED_SUCCESS = 13;

void setup() {
  Serial.begin(115200);
  
  // Initialize Pins
  pinMode(LED_MED_1, OUTPUT);
  pinMode(LED_MED_2, OUTPUT);
  pinMode(LED_MED_3, OUTPUT);
  pinMode(LED_ERROR, OUTPUT);
  pinMode(LED_SUCCESS, OUTPUT);

  // Initialize SPI bus and MFRC522
  SPI.begin();
  mfrc522.PCD_Init();
  delay(4);
  mfrc522.PCD_DumpVersionToSerial();
  Serial.println("Scan a Patient NFC Card to check for due medicines...");

  // Connect to Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void flashError() {
  for(int i=0; i<3; i++) {
    digitalWrite(LED_ERROR, HIGH);
    delay(200);
    digitalWrite(LED_ERROR, LOW);
    delay(200);
  }
}

void flashSuccess() {
  digitalWrite(LED_SUCCESS, HIGH);
  delay(1000);
  digitalWrite(LED_SUCCESS, LOW);
}

void dispenseMedicine(int medicine_id) {
  int pin = -1;
  // Map medicine_id to the specific LED pin
  if (medicine_id == 1) pin = LED_MED_1;
  else if (medicine_id == 2) pin = LED_MED_2;
  else if (medicine_id == 3) pin = LED_MED_3;
  
  if (pin != -1) {
    Serial.printf("Dispensing Medicine ID: %d on Pin %d\n", medicine_id, pin);
    digitalWrite(pin, HIGH);
    delay(3000); // Dispense for 3 seconds
    digitalWrite(pin, LOW);
  } else {
    Serial.printf("ERROR: Medicine ID %d is not mapped to any pin!\n", medicine_id);
    flashError();
  }
}

bool confirmDispense(int schedule_id, String nfc_uid) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(API_BASE_URL) + "/dispensing/dispense";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Hardware-Key", HARDWARE_API_KEY);
    
    // Create JSON Payload
    StaticJsonDocument<200> doc;
    doc["schedule_id"] = schedule_id;
    doc["nfc_uid"] = nfc_uid;
    String requestBody;
    serializeJson(doc, requestBody);
    
    int httpResponseCode = http.POST(requestBody);
    
    if (httpResponseCode == 200) {
      Serial.printf("Successfully logged dispense for Schedule ID: %d\n", schedule_id);
      http.end();
      return true;
    } else {
      Serial.printf("Failed to log dispense. HTTP Code: %d\n", httpResponseCode);
      http.end();
      return false;
    }
  }
  return false;
}

void processNfcCard(String uidStr) {
  Serial.printf("\nCard Detected! UID: %s\n", uidStr.c_str());
  
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    // URL Encode isn't strictly necessary for hex UID, but good practice
    String url = String(API_BASE_URL) + "/dispensing/due?nfc_uid=" + uidStr;
    
    http.begin(url);
    http.addHeader("X-Hardware-Key", HARDWARE_API_KEY);
    
    int httpResponseCode = http.GET();
    
    if (httpResponseCode == 200) {
      String payload = http.getString();
      Serial.println("Response Payload: " + payload);
      
      // Parse JSON
      DynamicJsonDocument doc(2048);
      DeserializationError error = deserializeJson(doc, payload);
      
      if (error) {
        Serial.print("deserializeJson() failed: ");
        Serial.println(error.c_str());
        flashError();
        http.end();
        return;
      }
      
      JsonArray schedules = doc.as<JsonArray>();
      
      if (schedules.size() == 0) {
        Serial.println("No medicines due right now for this patient.");
        flashError();
      } else {
        Serial.printf("Found %d medicines due!\n", schedules.size());
        
        for (JsonObject schedule : schedules) {
          int schedule_id = schedule["schedule_id"];
          int medicine_id = schedule["medicine_id"];
          String medicine_name = schedule["medicine_name"].as<String>();
          
          Serial.printf("Processing %s (ID: %d)...\n", medicine_name.c_str(), medicine_id);
          
          // Trigger physical dispense mechanism
          dispenseMedicine(medicine_id);
          
          // Notify backend
          bool logged = confirmDispense(schedule_id, uidStr);
          if(logged) {
            flashSuccess();
          } else {
            flashError();
          }
          delay(1000); // brief pause between medicines
        }
      }
    } else {
      Serial.printf("API Request failed, HTTP Code: %d\n", httpResponseCode);
      String payload = http.getString();
      Serial.println("Error: " + payload);
      flashError();
    }
    
    http.end();
  } else {
    Serial.println("Wi-Fi not connected!");
    flashError();
  }
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
  
  // Format UID to string (e.g. "0A 1B 2C 3D" -> "0a1b2c3d" or just a clean hex string)
  String uidStr = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if(mfrc522.uid.uidByte[i] < 0x10) {
      uidStr += "0";
    }
    uidStr += String(mfrc522.uid.uidByte[i], HEX);
  }
  uidStr.toLowerCase(); // Ensure lowercase matching if required by backend
  
  // Process the card
  processNfcCard(uidStr);
  
  // Halt PICC to avoid scanning multiple times rapidly
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  
  delay(1000); // 1 second cooldown
}
