#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <ArduinoJson.h>


const char* WIFI_SSID = "Mayura1";
const char* WIFI_PASSWORD = "Vista14A";

// Use the local IP of your backend server (e.g., http://192.168.1.100:9001)
// Do NOT use localhost or 127.0.0.1, as the ESP32 is on a separate device.
const char* API_BASE_URL = "http://192.168.5.57:9001";
const char* HARDWARE_API_KEY = "esp32-default-secret-key";

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
  delay(3000); // Wait 3 seconds so the Serial Monitor has time to open before printing!
  
  // Initialize Pins
  pinMode(LED_MED_1, OUTPUT);
  pinMode(LED_MED_2, OUTPUT);
  pinMode(LED_MED_3, OUTPUT);
  pinMode(LED_ERROR, OUTPUT);
  pinMode(LED_SUCCESS, OUTPUT);

  // Initialize SPI bus and MFRC522 (SIMULATED)
  // We completely skip SPI and real reader hardware
  pinMode(0, INPUT_PULLUP); // BOOT button for simulated tapping
  
  delay(100);
  Serial.println("Firmware Version: 0x92 = v2.0");
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
  
  // Test Server Connection
  Serial.println("Testing server connection...");
  HTTPClient http;
  String url = String(API_BASE_URL) + "/health";
  http.begin(url);
  int httpResponseCode = http.GET();
  if (httpResponseCode > 0) {
    Serial.printf("Server Connection Perfect! Status Code: %d\n", httpResponseCode);
  } else {
    Serial.printf("Server Connection Failed! Error Code: %d\n", httpResponseCode);
  }
  http.end();
  Serial.println("=========================================");
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
    String url = String(API_BASE_URL) + "/api/v1/dispensing/dispense";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Hardware-Api-Key", HARDWARE_API_KEY);
    
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
    String url = String(API_BASE_URL) + "/api/v1/dispensing/due?nfc_uid=" + uidStr;
    
    http.begin(url);
    http.addHeader("X-Hardware-Api-Key", HARDWARE_API_KEY);
    
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
  // Wait for the user to press the physical "BOOT" button on the ESP32 (GPIO 0)
  if (digitalRead(0) == LOW) {
    delay(50); // Debounce
    if (digitalRead(0) == LOW) {
      
      // We simulate reading Patient 1's card exactly as it is seeded in the database
      String simulated_uid = "A1:B2:C3:D4";
      
      // Process the simulated card
      processNfcCard(simulated_uid);
      
      // Wait for button to be released so it doesn't trigger 100 times per second
      while(digitalRead(0) == LOW) {
        delay(10);
      }
      
      delay(1000); // 1 second cooldown
    }
  }
}
