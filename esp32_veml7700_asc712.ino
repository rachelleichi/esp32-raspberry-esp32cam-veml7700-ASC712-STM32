#include <Wire.h>
#include "Adafruit_VEML7700.h"
#include <WiFi.h>
#include <HTTPClient.h>


Adafruit_VEML7700 veml = Adafruit_VEML7700();

const int currentPin = A0;  // PIN analogique pour ACS712
const float VCC = 5.0;       // Tension d'alimentation du capteur (en volts)
const float sensitivity = 100 ; // Sensibilité du capteur (en mV/A)
const float offset = 2.5; // 2.5 si alimenté en 5v et 1.65 si 3.3V (sortie quand courant est a 0A)
const float Voltage_V = 230.0;
unsigned long previousMillis = 0;  // Pour stocker le temps précédent
const long interval = 60000;  // Intervalle de temps entre chaque mesure (en ms)
float totalCurrent = 0;  

void setup() {
  Serial.begin(9600);
  delay(10000);  // Temps pour ouvrir le moniteur série 10 S
  
  const char* ssid = "Raspberry";
  const char* password = "Stage.2025";
  const char* serverName = "http://192.168.43.32:5010/data";

  void connectToWiFi() {
    WiFi.begin(ssid, password);
    Serial.print("Connexion Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println("Connecté !");
  }



  // Initialiser le capteur VEML7700
  if (!veml.begin()) {
    Serial.println("Erreur : VEML7700 non détecté");
    while (1);
  }
  Serial.println("Capteur VEML7700 initialisé");

  veml.setGain(VEML7700_GAIN_1);         // Réglage du gain standard, valeurs possibles 1 ,2 ,1/4 , 1/8
  //Plus le gain est élevé, plus le capteur est sensible (utile dans un environnement sombre).
  veml.setIntegrationTime(VEML7700_IT_100MS);  // Temps d’intégration, valeurs possibles : 25 ,50 ,100 ,200 ,400 ,800
 

  

}

void loop() {

 
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval){
    previousMillis = currentMillis; //toutes les 60s
    //lecture luminosité
    float lux = veml.readLux();
    Serial.print("Luminosité (lux) : ");
    Serial.println(lux);

    //lecture tension
    int raw = analogRead(currentPin); //lecture de valeur du pin
    float voltage = (raw / 4095.0) * VCC ;  // conversion en tension , 4095 car esp32 utilise adc 12 bits
    
    Serial.print("Tension analogique ACS712 : ");
    Serial.println(voltage);
    Serial.println(" V");
    
    //conversion courant
    float current = (voltage - offset) / sensitivity; 
    Serial.print("Courant estimé : ");
    Serial.print(current);
    Serial.println(" A");

    // Calcul de la puissance
    float power = Voltage_V * abs(current); // abs() pour éviter puissance négative
    Serial.print("Puissance estimée : ");
    Serial.print(power);
    Serial.println(" W");

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

