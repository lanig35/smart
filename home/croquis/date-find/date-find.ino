/*
  Web client

  This sketch connects to a website (http://www.google.com)
  using an Arduino Wiznet Ethernet shield.

  Circuit:
   Ethernet shield attached to pins 10, 11, 12, 13

  created 18 Dec 2009
  by David A. Mellis
  modified 9 Apr 2012
  by Tom Igoe, based on work by Adrian McEwen

*/

#include <SPI.h>
#include <Ethernet2.h>

#include <ArduinoJson.h>

const short tmpSensor = A0;
const short lightSensor = A1;
const short statusPin = 5;

int light = 0;
float temperature = 0;

const long toggleInterval = 1000;
const long sensorInterval = 10000;

unsigned long lastToggleTime = 0;
unsigned long lastSensorTime = 0;

byte mac[] = { 0x90, 0xA2, 0xDA, 0x10, 0xF7, 0x05 };
IPAddress server (192, 168, 1, 16);

// Initialize the Ethernet client library
// with the IP address and port of the server
// that you want to connect to (port 80 is default for HTTP):
EthernetClient client;

unsigned long lastConnectionTime = 0;             // last time you connected to the server, in milliseconds
const unsigned long postingInterval = 20000; // delay between updates, in milliseconds

int sensor = 0;

void setup() {
  int code;

  // Open serial communications
  Serial.begin(9600);
  Serial.println ("Hello");

  // mise off de la carte SD
  pinMode (4, OUTPUT);
  digitalWrite (4, HIGH);

  pinMode (statusPin, OUTPUT);
  digitalWrite (statusPin, LOW);
  pinMode (LED_BUILTIN, OUTPUT);
  digitalWrite (LED_BUILTIN, LOW);

  // start the Ethernet connection:
  if (Ethernet.begin(mac) == 0) {
    Serial.println(F("Failed to configure Ethernet"));
    while (true);
  }
  // give the Ethernet shield a second to initialize:
  delay(2000);

  // print your local IP address:
  Serial.println (Ethernet.localIP());

  code = client.connect ("www.google.com", 80);
  if (code) {
    Serial.println ("connection");
    // On construit l'en-tête de la requête
    client.println("HEAD / HTTP/1.1");
    client.println("Host: www.google.com");
    client.println("Connection: close");
    client.println();

    client.flush ();

    if (client.find ("Date:")) {
      char infoDate [40];
      int index = 0;
      index = client.readBytesUntil ('\n', infoDate, 40);
      if (index != 0) {
        infoDate[index] = '\0';
        Serial.println (infoDate);
        char * tok;
        tok = strtok (infoDate, ",: ");
        while (tok != NULL) {
          Serial.println (tok);
          tok =  strtok (NULL, ",: ");
        }
      } else {
        Serial.println ("pb lect date");
      }
      Serial.println(F("Deconnexion !"));

      // On ferme le client
      client.stop();

    } else {
      Serial.println ("Not found");
    }
  } else {
    Serial.print (F("erreur connection: "));
    Serial.println (code);
  }
}

void loop()
{
  unsigned long currentMillis = millis ();

  if (currentMillis - lastToggleTime > toggleInterval) {
    lastToggleTime = currentMillis;
    digitalWrite (statusPin, !digitalRead (statusPin));
  }

  if (currentMillis - lastSensorTime > sensorInterval) {
    lastSensorTime = currentMillis;
    light = analogRead (lightSensor);
    int tmpAnalog = analogRead (tmpSensor);
    float tmpVoltage = (tmpAnalog / 1024.0) * 5.0;
    temperature = (tmpVoltage - 0.5) * 100;

    Serial.print ("Lux: "); Serial.print (light);
    Serial.print (" Temp: "); Serial.println (temperature);
  }
  
  if (currentMillis - lastConnectionTime > postingInterval) {
    lastConnectionTime = currentMillis;
    Serial.println(F("connecting..."));

    if (client.connect(server, 5000)) {
      StaticJsonBuffer<40> jsonBuffer;
      Serial.println(F("connected..."));

      JsonObject& root = jsonBuffer.createObject();
      root ["tmp"] = temperature;
      root ["lux"] = light;
      
      root.printTo(Serial);

      client.println("POST /data HTTP/1.1");
      client.println("Host: 192.168.1.16");
      client.println(F("Connection: close"));
      client.println("Connection: close\r\nContent-Type: application/json");
      client.print("Content-Length: ");
      client.print(root.measureLength());
      client.print("\r\n");
      client.println();
      root.printTo(client);

      /*
        client.print (sensor);
        client.println ("\"}");
      */
      client.flush ();

      Serial.println(F("data emises..."));
      sensor++;

      /*
            int index = 0;
            char reponse[256];

            while (client.connected()) {
              while (client.available()) {
                reponse[index] = client.read();
                index++;
              }
              Serial.println (index);
            }
            Serial.println (index);
      */
      if (client.find ("HTTP")) {
        char resultat [15];
        int index = 0;
        index = client.readBytesUntil ('\n', resultat, 15);
        if (index != 0) {
          resultat[index] = '\0';
          Serial.println (resultat);
          char * tok;
          tok = strtok (resultat, " ");
          while (tok != NULL) {
            Serial.println (tok);
            tok =  strtok (NULL, " ");
          }
        } else {
          Serial.println ("pb lect code");
        }
      }

      client.stop();
    } else {
      Serial.println (F("Erreur connexion Flask"));
    }


  }

}

