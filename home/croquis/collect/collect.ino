/*
  Date: 12 Avril 2018
  Auteur: Alain Blanchard
  Objet: Enregistrer température et luminosité sur
  carte SD

  basé sur le shield Imagine Evola avec:
  horloge BQ3200 I2C en A4(SDA) et A5 (SCL)
  capteur TMP36 sur A2
  photorésistance sur A3

  carte SD en 13 (SCK) 12 (MISO) 11 (MOSI) et 10 (CS/SS)
  
  8 LEDs (4 V 2 0 2 R) sur D2 et D3 (registre 74HC164)
  bouton poussoir en D4
  buzzer en D5

  bouton tactile en A1 et D12 désactive (carte SD SPI)
  LCD désactivé (idem)

  TODO:
  module radio (RF433 ou NRF24l01) pour réseau capteurs
  utilisation LEDs (alerte, statut, etc. )
  utilisation buzzer et bouton poussoir:
    1/ phase init (calibrage, vérification, mise à l'heure tc.)
    2/ alerte sonore
  réception de commandes pour activer des éléments (led, buzzer)
  vérification tension pour calcul précis température
  surveillance tension sur batterie

  passage en mode sleep (watchdog, autre ?)
  activer super capacité BQ3200
  
  accès direct horloge avec Wire
  utilisation registres Atmega328 (PORTx, DDRx)
  utilisation "progmem" pour économiser la RAM (cf. jours)
  désactivation LEDs pour bénéficier des interruptions ?
*/

#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <RTClib.h>

// définitions pour module RTC
#define BQ_ADDR_I2C 0x68
RTC_DS1307 BQ3200;

// définitions pour carte SD
#define SD_SS_PIN 10
char fichier [] = "data.log";

// interfaces des capteurs
const byte fiche_tmp36 = A2;
const byte fiche_ldr = A3;

// pour gestion delai entre 2 acqusitions
const long delai_releve = 60000L;
unsigned long dernier_releve = 0;

// pour formatage message (console et carte SD)
char message [40];

void setup() {
  // lancement port série
  Serial.begin (115200);
  Serial.println (F("Début Initialisation"));
  
  // préparation module RTC
  if (!BQ3200.begin()) {
    Serial.println (F("Erreur: Horloge absente"));
    while (1);
  }

  if (!BQ3200.isrunning ()) {
    Serial.println(F("Horloge arrêtée: mise à l'heure"));
    BQ3200.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }
  BQ3200.adjust(DateTime(F(__DATE__), F(__TIME__)));

  // préparation carte SD
  pinMode (SD_SS_PIN, OUTPUT);  // PIN CS carte SD à OUTPUT (cf. SPI forum Arduino)
  if (!SD.begin (SD_SS_PIN)) {
    Serial.println (F("Erreur: carte SD absente"));
    while (1);
  }
  if (!SD.exists (fichier)) {
    Serial.println (F("Création fichier log"));
    File descripteur = SD.open (fichier, FILE_WRITE);
    if (!descripteur){
      Serial.println (F("Erreur: création fichier"));
      while (1);
    }
    // écriture entête
    descripteur.println (F("horodatage;temperature;luminosite"));
    descripteur.flush ();
    descripteur.close ();
  }
  
  Serial.println (F("Fin Initialisation"));
}

void loop() {
  unsigned long maintenant = millis ();

  if (maintenant - dernier_releve > delai_releve) {
    dernier_releve = maintenant;

    // lecture capteur temperature (2 fois pour pb impédance ?)
    analogRead (fiche_tmp36);
    int valeur_capteur = analogRead (fiche_tmp36);
    float voltage = (valeur_capteur / 1024.0) * 5.0;
    float temperature = (voltage - 0.5) * 100;

    // lecture photorésistance
    int ldr = analogRead (fiche_ldr);

    // récupération horodatage
    DateTime now = BQ3200.now ();

    // préparation message
    char strtemp [6];
    dtostrf (temperature, 5, 2, strtemp);
    // autre option: printf(str, "String value: %d.%02d", (int)f, (int)(f*100)%100);
    //sprintf (message, "%lu;master;t:%s;l:%3d", heure.unixtime(), strtemp, ldr);
    sprintf (message, "%2.2i:%2.2i:%2.2i;t:%s;l:%3i",now.hour(), now.minute(),now.second(),strtemp, ldr);
    Serial.println (message);
    File descripteur = SD.open (fichier, FILE_WRITE);
    if (!descripteur) {
      Serial.println (F("Erreur ouverture fichier")); 
    } else {
      descripteur.println (message);
      descripteur.flush ();
      descripteur.close ();
    }
  }
}

