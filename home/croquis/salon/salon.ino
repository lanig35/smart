/*
  Date: 23 Mars 2018
  Auteur: Alain Blanchard
  Objet: récupérer des données d'environnement et les
  transmettre via liaison radio RF433 au pilote Arduino

  capteur TMP36 sur A2
  photorésistance sur A3
  émetteur TX en D2 (RX et PTT eb D3 et D4)

  Note: librairie VirtualWire utilise Timer 1 et la fonction
  millis le timer 0 ce qui laisse le timer

  TODO:
  tester la porté RF433
  LEDs (ou RGB ?) pour informer sur l'état
  bouton pour interagir avec montage / gestion réveil
  basse consommation (sleep mode)
  surveillance température interne et voltage (pour calcul tmp)
  autres capteurs: son, soil mosture, mouvement, procimité

  déplacer RF pour récupérer D2 et D3 (external interrupt)

  utilisation registres Atmega328 (PORTx, DDRx)
  utilisation "progmem" pour économiser la RAM
  conversion ADC par registre et interruption
*/
#include "define.h"

#include <arduino.h>
#include <VirtualWire.h>

char message [40];

// interfaces des capteurs
const byte fiche_tmp36 = A2;
const byte fiche_ldr = A3;

// pour gestion delai entre 2 acqusitions
const long delai_releve = 20000;

unsigned long dernier_releve = 0;

void setup() {
  Serial.begin (9600);

  // initialisation RF433
  vw_set_tx_pin (4);
  vw_set_rx_pin (3);
  vw_set_ptt_pin (4);

  vw_setup (300);

  // initialisation ref analog
  //  analogReference (INTERNAL);
  dummy ();
  int a = alain;
}

/** Mesure la référence interne à 1.1 volts */
unsigned int analogReadReference(void) {
  /* Elimine toutes charges résiduelles */
  ADMUX = 0x4F;
  delayMicroseconds(5);
  /* Sélectionne la référence interne à 1.1 volts comme point de mesure, avec comme limite haute VCC */
  ADMUX = 0x4E;
  delayMicroseconds(200);
  /* Active le convertisseur analogique -> numérique */
  ADCSRA |= (1 << ADEN);
  /* Lance une conversion analogique -> numérique */
  ADCSRA |= (1 << ADSC);
  /* Attend la fin de la conversion */
  while (ADCSRA & (1 << ADSC));
  /* Récupère le résultat de la conversion */
  return ADCL | (ADCH << 8);
}
unsigned int analogrefV2 (void) {
  //  ADMUX = (1 << REFS2) | (1 << REFS1) | (1 << MUX2) | (1 << MUX2) | (1 << MUX1);
  ADMUX = (1 << REFS1) | (1 << REFS0) | (1 << MUX3) | (1 << MUX2) | (1 << MUX1);
  byte old_adcsra = ADCSRA;
  Serial.print ("OLD reg :"); Serial.println (ADCSRA, HEX);
  ADCSRA = (1 << ADEN);
  delay (10);
  ADCSRA |= (1 << ADSC);
  while (ADCSRA & (1 << ADSC));
  ADCSRA = old_adcsra;
  return ADCL | (ADCH << 8);
}

unsigned int internalTemp (void) {
  byte old_adcsra = ADCSRA;
  Serial.print ("OLD reg :"); Serial.println (ADCSRA, HEX);
  ADMUX = (1 << REFS0) | (1 << REFS1) | 0x08;
  ADCSRA = (1 << ADEN);
  ADCSRA |= bit (ADPS0) |  bit (ADPS1) | bit (ADPS2);
  delay (10);
  ADCSRA |= (1 << ADSC);
  while (ADCSRA & (1 << ADSC));
  ADCSRA = old_adcsra;
  return (ADC);
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

    // préparation message
    char strtemp [6];
    dtostrf (temperature, 5, 2, strtemp);
    sprintf (message, "salon;t:%s;l:%3d", strtemp, ldr);
    Serial.println (message);
    voltage = (valeur_capteur / 1024.0) * 1.1;
    temperature = (voltage - 0.5) * 100;
    Serial.print ("int: "); Serial.println (temperature);

    // émission message
    vw_send (message, strlen(message) + 1);
    vw_wait_tx ();

    float tension_alim = (1023 * 1.1) / analogReadReference();
    Serial.print ("al-1: "); Serial.println(tension_alim, 3);
    tension_alim = (1023 * 1.1) / analogrefV2();
    Serial.print ("al-2: "); Serial.println(tension_alim, 3);
    Serial.print ("temp: "); Serial.println (internalTemp());

// lecture voltage
    ADCSRA =  bit (ADEN);   // turn ADC on
    ADCSRA |= bit (ADPS0) |  bit (ADPS1) | bit (ADPS2);  // Prescaler of 128
    ADMUX = bit (REFS0) | bit (MUX3) | bit (MUX2) | bit (MUX1);

    delay (10);  // let it stabilize

    bitSet (ADCSRA, ADSC);  // start a conversion
    while (bit_is_set(ADCSRA, ADSC))
    { }

    float results = 1.1 / float (ADC + 0.5) * 1024.0;
    Serial.print ("Voltage = ");
    Serial.println (results);
  }
}
