
boolean writeRegister (byte adresse, byte value) {
  return (true);
}

byte readRegister (byte adresse) {
  return (0);
}

boolean ds3231::begin (const byte adresse) {
  this->_adresse = adresse;

  // vérificaton de l'adresse
  Wire.beginTransmission (this->_adresse);
  return (Wire.endTransmission () == 0);
}

boolean ds3231::isRunning (void) {
  Wire.beginTransmission (this->_adresse);
  Wire.write (0x0F);
  Wire.endTransmission ();

  Wire.requestFrom (this->_adresse, (byte)1);
  byte status_reg = Wire.read ();
  if (status_reg >> 7) {
    Serial.println (F("OSF flag on"));
    return (false);
  } else {
    return (true);
  }
}

void ds3231::adjust (const char* calendrier, const char* horaire) {
  byte h, m, s;
  char mois[4];
  byte j;
  int y;

  Serial.print (calendrier); Serial.print (" "); Serial.println (horaire);
  sscanf (calendrier, "%3s %2hhu %4d", mois, &j, &y);
  Serial.print ("D: "); Serial.print (j); Serial.print (" M: "); Serial.print (mois);
  Serial.print (" Y: "); Serial.println (y);

  sscanf (horaire, "%2hhu:%2hhu:%2hhu", &h, &m, &s);
  Serial.print ("H: "); Serial.print (h); Serial.print (" M: "); Serial.print (m);
  Serial.print (" S: "); Serial.println (s);

  Wire.beginTransmission (0x68);
  Wire.write (0x00);
  Wire.write (bin2bcd(s));
  Wire.write (bin2bcd(m));
  Wire.write (bin2bcd(h)); // format 24 heures (bit 6 à 0)
  Wire.write (bin2bcd(0)); // on ignore le numéro de jour
  Wire.write (bin2bcd(1));
  Wire.write (bin2bcd(4));
  Wire.write (bin2bcd(18));
  if (Wire.endTransmission () != 0) {
    Serial.println ("erreur adjust");
  }

  Wire.beginTransmission (this->_adresse);
  Wire.write (0x0F);
  Wire.endTransmission ();
  Wire.requestFrom (this->_adresse, (byte)1);
  byte status_reg = Wire.read ();
  Wire.beginTransmission (this->_adresse);
  Wire.write (0x0F);
  Wire.write (status_reg & ~(1 << 7));
  Wire.endTransmission ();
}

boolean ds3231::now (date_t* t) {
  Wire.beginTransmission (this->_adresse);
  Wire.write (0x00);
  Wire.endTransmission ();

  Wire.requestFrom (this->_adresse, (byte)7);

  if (Wire.available() != 7) {
    Serial.println ("Erreur lecture DS3231");
    return (false);
  }

  t->seconde = bcd2bin (Wire.read());
  t->minute = bcd2bin (Wire.read());
  t->heure = bcd2bin (Wire.read());
  Wire.read ();
  t->jour = bcd2bin (Wire.read());
  t->mois = bcd2bin (Wire.read());
  t->annee = bcd2bin (Wire.read());

  return (true);
}

float ds3231::temperature () {
  Wire.beginTransmission (this->_adresse);
  Wire.write (0x11);
  Wire.endTransmission ();

  Wire.requestFrom (this->_adresse, (byte)2);

  if (Wire.available() != 2) {
    Serial.println ("Erreur lecture DS3231");
    return (99.0);
  }

  byte msb = Wire.read();
  byte lsb = Wire.read();

  float temperature = (((msb << 8) | lsb) >> 6) / 4.0;
  return (temperature);
}

