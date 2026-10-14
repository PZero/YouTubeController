#include "ingressi.h"
#include "config.h"

// Tabella di quadratura: indice = (stato precedente << 2) | stato attuale
static const int8_t TABELLA[16] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};

static volatile uint8_t statoAB;
static volatile int8_t transizioni = 0;
static volatile int32_t posizioneIsr = 0;
static volatile uint32_t nonValide = 0;

// Logica provata in test_comandi: EC11E 20 impulsi / 20 scatti, 4 transizioni per scatto,
// riposo su A=B=1, orario = avanti.
static void IRAM_ATTR isrEncoder() {
  uint8_t ora = (digitalRead(PIN_ENC_A) << 1) | digitalRead(PIN_ENC_B);
  if (ora == statoAB) return;
  int8_t d = TABELLA[(statoAB << 2) | ora];
  if (d == 0) nonValide++;
  transizioni += d;
  statoAB = ora;
  if (ora == 3) {
    if (transizioni >= 2) posizioneIsr++;
    else if (transizioni <= -2) posizioneIsr--;
    transizioni = 0;
  }
}

void ingressiInizia() {
  pinMode(PIN_ENC_A, INPUT_PULLUP);
  pinMode(PIN_ENC_B, INPUT_PULLUP);
  pinMode(PIN_PULSANTE, INPUT_PULLUP);
  delay(5);
  statoAB = (digitalRead(PIN_ENC_A) << 1) | digitalRead(PIN_ENC_B);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_A), isrEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_ENC_B), isrEncoder, CHANGE);
}

int32_t encoderPosizione() { return posizioneIsr; }
uint32_t encoderNonValide() { return nonValide; }

// ---- Pulsante ----
static bool swPremuto = false, swLetto = false;
static unsigned long swCambio = 0, swInizio = 0;

int pulsanteAggiorna(unsigned long adesso, unsigned long &durataMs) {
  bool letto = digitalRead(PIN_PULSANTE) == LOW;
  if (letto != swLetto) {
    swLetto = letto;
    swCambio = adesso;
  }
  if (adesso - swCambio > DEBOUNCE_MS && swLetto != swPremuto) {
    swPremuto = swLetto;
    if (swPremuto) {
      swInizio = adesso;
      return 1;
    }
    durataMs = adesso - swInizio;
    return -1;
  }
  return 0;
}

bool pulsantePremuto() { return swPremuto; }
unsigned long pulsanteInizio() { return swInizio; }

// ---- Velocita': media degli ultimi 3 intervalli, isteresi in discesa ----
static unsigned long ultimoScatto = 0;
static unsigned long intervalli[3];
static int nIntervalli = 0;
static int ultimaDir = 0;
static int livello = 1;
static int sottoSoglia = 0;
static float velUltima = 0;

int velocitaScatto(int dir, unsigned long adesso) {
  unsigned long dt = adesso - ultimoScatto;
  ultimoScatto = adesso;
  if (dir != ultimaDir || dt > PAUSA_RESET_VEL) {
    ultimaDir = dir;
    nIntervalli = 0;
    livello = 1;
    sottoSoglia = 0;
    velUltima = 0;
    return livello;
  }
  if (dt == 0) dt = 1;  // piu' scatti nello stesso ms (letti in blocco)
  intervalli[nIntervalli % 3] = dt;
  nIntervalli++;
  int n = nIntervalli < 3 ? nIntervalli : 3;
  unsigned long somma = 0;
  for (int i = 0; i < n; i++) somma += intervalli[i];
  velUltima = 1000.0f * n / somma;

  int nuovo = velUltima > VEL_VELOCE ? 3 : (velUltima > VEL_MEDIA ? 2 : 1);
  if (nuovo > livello) {
    livello = nuovo;  // si sale subito
    sottoSoglia = 0;
  } else if (nuovo < livello) {
    float soglia = (livello == 3 ? VEL_VELOCE : VEL_MEDIA) * ISTERESI;
    if (velUltima < soglia) {
      if (++sottoSoglia >= 2) {
        livello--;
        sottoSoglia = 0;
      }
    } else {
      sottoSoglia = 0;
    }
  } else {
    sottoSoglia = 0;
  }
  return livello;
}

float velocitaUltima() { return velUltima; }
