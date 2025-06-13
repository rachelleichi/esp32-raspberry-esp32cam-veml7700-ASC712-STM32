#include <Wire.h>
#include "Adafruit_VEML7700.h"
#include <WiFi.h>
#include <HTTPClient.h>

Adafruit_VEML7700 veml = Adafruit_VEML7700();

const int currentPin = A0;  // PIN analogique pour ACS712
const float VCC = 5.0;
const float sensitivity = 100; // Sensibilité en mV/A
const float offset = 2.5;
const float Voltage_V = 230.0;
unsigned long previousMillis = 0;
const long interval = 60000;

float totalCurrent = 0;

// Wi-Fi & serveur
const char* ssid = "Raspberry";
const char* password = "Stage.2025";
const char* serverName = "http://10.42.0.1:5010/data";

void connectToWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connexion Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" Connecté !");
}

void setup() {
  Serial.begin(9600);
  delay(10000);

  connectToWiFi();

  if (!veml.begin()) {
    Serial.println("Erreur : VEML7700 non détecté");
    while (1);
  }
  Serial.println("Capteur VEML7700 initialisé");

  veml.setGain(VEML7700_GAIN_1);
  veml.setIntegrationTime(VEML7700_IT_100MS);
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    float lux = veml.readLux();
    Serial.print("Luminosité (lux) : ");
    Serial.println(lux);

    int raw = analogRead(currentPin);
    float voltage = (raw / 4095.0) * VCC;
    Serial.print("Tension analogique ACS712 : ");
    Serial.println(voltage);

    float current = (voltage - offset) / sensitivity;
    Serial.print("Courant estimé : ");
    Serial.println(current);

    float power = Voltage_V * abs(current);
    Serial.print("Puissance estimée : ");
    Serial.println(power);

    Serial.println("----------------------------");

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverName);
      http.addHeader("Content-Type", "application/json");

      String jsonData = "{";
      jsonData += "\"lux\":" + String(lux) + ",";
      jsonData += "\"current\":" + String(current) + ",";
      jsonData += "\"power\":" + String(power);
      jsonData += "}";

      int httpResponseCode = http.POST(jsonData);

      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      http.end();
    } else {
      Serial.println("Wi-Fi non connecté !");
    }
  }
}
