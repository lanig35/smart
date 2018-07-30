/*

*/

#include <SPI.h>
#include <Ethernet2.h>
#include <VirtualWire.h>

byte mac[] = { 0x90, 0xA2, 0xDA, 0x10, 0xF7, 0x05 };
IPAddress server (192, 168, 1, 16);

// Initialize the Ethernet client library
// with the IP address and port of the server
// that you want to connect to (port 80 is default for HTTP):
EthernetClient client;

void setup() {
  // Open serial communications
  Serial.begin(115200);
  Serial.println ("Début");

  // mise off de la carte SD
  pinMode (4, OUTPUT);
  digitalWrite (4, HIGH);

  // start the Ethernet connection:
  if (Ethernet.begin(mac) == 0) {
    Serial.println(F("Failed to configure Ethernet"));
    while (true);
  }
  // give the Ethernet shield a second to initialize:
  delay(2000);

  // print your local IP address:
  Serial.println (Ethernet.localIP());

  // lancement RF433
  vw_set_tx_pin(5);
  vw_set_rx_pin(6);
  vw_set_ptt_pin (7);

  vw_setup (300);
  vw_rx_start ();
}

void loop()
{
  // lecture message
  // vw_wait_rx();

  if (vw_have_message()) {
    byte taille = 12;
    byte message [12];

    if (vw_get_message (message, &taille)) {
      Serial.println ((char*)message);
    } else {
      Serial.print ("bad: "); Serial.println (vw_get_rx_bad());
    }

    int code = client.connect(server, 5000);
    if (code) {
      Serial.println(F("connected..."));

      client.println("POST /data HTTP/1.1");
      client.println("Host: 192.168.1.16");
      client.println(F("Connection: close"));
      client.println("Connection: close\r\nContent-Type: application/json");
      client.print("Content-Length: 5");
      client.print("\r\n");
      client.println();
      client.println ("hello");

      client.flush ();
      client.stop ();
      Serial.println(F("data emises..."));
    } else {
      Serial.print (F("erreur connection: "));
      Serial.println (code);
    }
  }
}
