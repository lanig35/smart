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

#include <VirtualWire.h>

char message [40];

// pour gestion delai entre 2 acqusitions
const long delai_releve = 20000;
unsigned long dernier_releve = 0;

void setup() {
  Serial.begin (9600);

  // initialisation RF433
  vw_set_tx_pin (4);
  vw_set_rx_pin (5);
  vw_set_ptt_pin (6);

  vw_setup (300);
}

void loop() {
  unsigned long maintenant = millis ();

  if (maintenant - dernier_releve > delai_releve) {
    dernier_releve = maintenant;

    sprintf (message, "%s", "Hello!");
    Serial.println (message);

    // émission message
    vw_send (message, strlen(message) + 1);
    vw_wait_tx ();
  }
}
