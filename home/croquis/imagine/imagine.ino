/*
  Date: 16 Mars 2018
  Auteur: Alain Blanchard
  Objet: interfacer la carte via le port série afin de
  remonter la température et une valeur d'éclairage

  basé sur le shield Imagine Evola avec:
  horloge BQ3200 I2C en A4(SDA) et A5 (SCL)
  capteur TMP36 sur A2
  photorésistance sur A3

  8 LEDs (4 V 2 0 2 R) sur D2 et D3 (registre 74HC164)
  bouton poussoir en D4
  buzzer en D5

  bouton tactile en A1 et D12 désactive (carte SD SPI)
  LCD désactivé (idem)

  TODO:
  enregistrement carte SD avec horodatage
  module radio (RF433 ou NRF24l01) pour réseau capteurs
  clignotement LEDs
  utilisation buzzer et bouton poussoir ?
  réception de commandes pour activer des éléments (led, buzzer)
  vérification tension pour calcul précis température

  accès direct horloge avec Wire
  utilisation registres Atmega328 (PORTx, DDRx)
  utilisation "progmem" pour économiser la RAM (cf. jours)
  désactivation LEDs pour bénéficier des interruptions ?
*/

#include <Wire.h>
#include <RTClib.h>
#include <VirtualWire.h>

RTC_DS1307 BQ3200;
char jours [7][10] = {"Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"};

char message [40];

// interfaces des capteurs
const byte fiche_tmp36 = A2;
const byte fiche_ldr = A3;

// pour gestion delai entre 2 acqusitions
const long delai_releve = 10000;

unsigned long dernier_releve = 0;

void setup() {
  // lancement port série
  Serial.begin (9600);

  // préparation module RTC
  if (!BQ3200.begin()) {
    Serial.println ("Erreur: Horloge absente");
    while (1);
  }

  if (! BQ3200.isrunning ()) {
    Serial.println("Horloge arrêtée: mise à l'heure");
    BQ3200.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }
  BQ3200.adjust(DateTime(F(__DATE__), F(__TIME__)));

  Serial.println (F("Démarrage"));

  // lancement RF433
  vw_set_rx_pin(6);
  vw_set_tx_pin(7);
  vw_set_ptt_pin (8);
  vw_setup (300);
  vw_rx_start ();
}

void loop() {
  unsigned long maintenant = millis ();

  // lecture message en provenance noeuds Arduino
  if (vw_have_message()) {
    byte taille = 40;
    byte data [40];

    if (vw_get_message (data, &taille)) {
      // récupération horodatage
      DateTime heure = BQ3200.now ();
      
      sprintf (message, "%lu;%s", heure.unixtime(), (char*)data);
      Serial.println (message);
    } else {
      char erreur[20];
      strncpy (erreur, data, taille);
      Serial.print (F("Erreur réception")); Serial.println (erreur);
    }
  }

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
    DateTime heure = BQ3200.now ();

    // préparation message
    char strtemp [6];
    dtostrf (temperature, 5, 2, strtemp);
    // autre option: printf(str, "String value: %d.%02d", (int)f, (int)(f*100)%100);
    sprintf (message, "%lu;master;t:%s;l:%3d", heure.unixtime(), strtemp, ldr);
    Serial.println (message);
  }
}

