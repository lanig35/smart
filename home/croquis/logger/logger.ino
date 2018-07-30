/*
  Date: 01 Avril 2018
  Auteur: Alain Blanchard
  Objet: récupérer des données d'environnement et les
  stocker sur une carte SD

  capteur température: embarqué sur DS3231
  photorésistance sur A1

  module mémoire I2c AT24C32 (@I2c = 0x57)
  module RTC DS3231 (@I2c = 0x68)

  interface I2C:
    SDA (A4)
    SDL (A5)

  carte SD - interface SPI
    CS (D4)
    MOSI (D11) - MISO (D12) - CLK (D13)

  TODO:
    ajustement RTC
    lecture température et date
      1/ par délai
      2/ par alarme
    écriture sur carte SD (taille et nombre fichiers ?)
    écriture en eeprom (cache) puis vidage SD

    augmentation fréquence I2c et SPI
    diminution fréquence processeur (?)

    LEDs (ou RGB ?) pour informer sur l'état
    bouton pour interagir avec montage / gestion réveil

    basse consommation (sleep mode)

    surveillance voltage (pour arrêt croquis ?)
    autres capteurs: son, soil mosture, mouvement, procimité

  utilisation registres Atmega328 (PORTx, DDRx)
  utilisation "progmem" pour économiser la RAM
  conversion ADC par registre (et interruption) pour LDR
*/

#include "define.h" // définitions communes à tous les "onglets"
#include <LowPower.h>
#include <Wire.h>   // pour access au bus I2C
#include <SPI.h>
#include <SD.h>

// définitions pour module RTC
#define DS3231_ADRESSE_I2C 0x68
ds3231 rtc;

// définitions pour carte SD
#define SD_SS_PIN 4
char fichier [] = "data.log";

// interface des capteurs
const byte fiche_ldr = A3;

// pour formatage message (console et carte SD)
char message [40];
date_t ts;

// pour gestion alarme prise de mesure
volatile bool alarm_on = false;
const byte fiche_alarme = D2;

void Alarm () {
  alarm_on = true;
}
void setup() {
  // lancement port série
  Serial.begin (115200);
  Serial.println (F("Début Initialisation"));

  // préparation I2C
  Wire.begin ();

  // préparation module RTC
  if (!rtc.begin (DS3231_ADRESSE_I2C)) {
    Serial.print (F("DS3231 absent - Vérifier montage"));
    while (1);
  }
  if (!rtc.isRunning ()) {
    // mise à l'heure du module RTC
    Serial.println(F("Horloge arrêtée: mise à l'heure"));
    rtc.adjust (__DATE__, __TIME__);
  }

  // préparation carte SD
  pinMode (SD_SS_PIN, OUTPUT);  // PIN CS carte SD à OUTPUT (cf. SPI forum Arduino)
  if (!SD.begin (SD_SS_PIN)) {
    Serial.println (F("Erreur: carte SD absente"));
    while (1);
  }
  if (!SD.exists (fichier)) {
    Serial.println (F("Création fichier log"));
    File descripteur = SD.open (fichier, FILE_WRITE);
    if (!descripteur) {
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
  // lecture photorésistance
  int ldr = analogRead (fiche_ldr);

  // lecture température
  float temperature = rtc.temperature();

  // récupération horodatage
  rtc.now (&ts);

  // préparation message
  char strtemp [6];
  dtostrf (temperature, 5, 2, strtemp);
  // autre option: printf(str, "String value: %d.%02d", (int)f, (int)(f*100)%100);
  //sprintf (message, "%lu;master;t:%s;l:%3d", heure.unixtime(), strtemp, ldr);
  sprintf (message, "%2.2i:%2.2i:%2.2i;%s;%3i", ts.heure, ts.minute, ts.seconde, strtemp, ldr);
  Serial.println (message);

  // écriture carte SD
  File descripteur = SD.open (fichier, FILE_WRITE);
  if (!descripteur) {
    Serial.println (F("Erreur ouverture fichier"));
  } else {
    descripteur.println (message);
    descripteur.flush ();
    descripteur.close ();
  }

  // mise en veille
  attachInterrupt (digitalPinToInterrupt(fiche_alarm), Alarm, LOW);
  LowPower.powerDown (SLEEP_FOREVER, ADC_OFF, BOD_OFF);
  detachInterrupt (digitalPinToInterrupt(fiche_alarm));
  if (!alarm_on) {
    Serial.println (F("Erreur: réveil sans alarme"));
  }
  alarm_on = false;
}
