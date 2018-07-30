#include <Wire.h>

#define BQ3200_ADDR 0x68
#define I2C_FAST_MODE 400000

static byte bcd2bin (byte val) {
  return val - 6 * (val >> 4);
}
static byte bin2bcd (byte val) {
  return val + 6 * (val / 10);
}

void setup() {
  Serial.begin (9600);

  Wire.begin ();
  Wire.setClock (I2C_FAST_MODE);

  Wire.beginTransmission (BQ3200_ADDR);
  Wire.write (0x00);
  if (Wire.endTransmission() != 0) {
    Serial.println ("Erreur acces BQ3200");
    while (1) ;
  }

  byte nb = Wire.requestFrom (BQ3200_ADDR, (byte)10);
  Serial.print ("Bytes lus: "); Serial.println (nb);
  while (Wire.available()) {
    Serial.println (Wire.read (), BIN);
  }

  Wire.beginTransmission (0x68);
  Wire.write (0x00);
  Wire.endTransmission ();

  Wire.requestFrom (0x68, (byte)7);
  byte s = bcd2bin (Wire.read());
  byte m = bcd2bin (Wire.read());
  byte h = bcd2bin (Wire.read());
  Wire.read ();
  byte d = bcd2bin (Wire.read());
  byte mm = bcd2bin (Wire.read());
  byte y = bcd2bin (Wire.read());

  Serial.print ("H: "); Serial.print (h); Serial.print (" M: "); Serial.print (m);
  Serial.print (" S: "); Serial.println (s);
  Serial.print ("D: "); Serial.print (d); Serial.print (" M: "); Serial.print (mm);
  Serial.print (" Y: "); Serial.println (y + 2000);
  Serial.println ("");

  Serial.println ("adjusting");
  
  Wire.beginTransmission (0x68);
  Wire.write (0x00);
  Wire.write (bin2bcd(8));
  Wire.write (bin2bcd(21));
  Wire.write (bin2bcd(16)); // format 24 heures (bit 6 à 0)
  Wire.write (bin2bcd(0)); // on ignore le numéro de jour
  Wire.write (bin2bcd(6));
  Wire.write (bin2bcd(4));
  Wire.write (bin2bcd(18));
  if (Wire.endTransmission () != 0) {
    Serial.println ("erreur adjust");
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  delay (20000);
  Wire.beginTransmission (0x68);
  Wire.write (0x00);
  Wire.endTransmission ();

  Wire.requestFrom (0x68, (byte)7);
  byte s = bcd2bin (Wire.read());
  byte m = bcd2bin (Wire.read());
  byte h = bcd2bin (Wire.read());
  Wire.read ();
  byte d = bcd2bin (Wire.read());
  byte mm = bcd2bin (Wire.read());
  byte y = bcd2bin (Wire.read());

  Serial.print ("H: "); Serial.print (h); Serial.print (" M: "); Serial.print (m);
  Serial.print (" S: "); Serial.println (s);
  Serial.print ("D: "); Serial.print (d); Serial.print (" M: "); Serial.print (mm);
  Serial.print (" Y: "); Serial.println (y + 2000);
  Serial.println ("");
}
