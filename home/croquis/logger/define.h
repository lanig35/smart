#ifndef _define_h_
#define _define_h_

struct _t {
  byte seconde;
  byte minute;
  byte heure;
  byte jour;
  byte mois;
  unsigned int annee;
};

class ds3231 {
  public:
    boolean begin(const byte adresse);
    boolean isRunning (void);
    void adjust (const char* date, const char* horaire);
    boolean now (struct date_t*);
    float temperature (void);
  protected:
    byte _adresse;
    prvate:
    boolean writeRegister (byte adresse, byte valeur);
    byte readregister (byte adresse);
};

#endif
