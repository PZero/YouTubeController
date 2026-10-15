#include "tasti.h"
#include "config.h"
#include "ble_tastiera.h"

static const char *NOMI[] = {
  "Spazio", "L",
  "Sinistra", "Destra",
  "Shift+Sinistra", "Shift+Destra",
  "Alt+Sinistra", "Alt+Destra",
  "F13", "F14", "F15", "F16",
};

const char *tastoNome(Tasto t) { return NOMI[t]; }

void tastoHid(Tasto t, uint8_t &mod, uint8_t &usage) {
  mod = 0;
  switch (t) {
    case T_SPAZIO: usage = 0x2C; break;
    case T_L: usage = 0x0F; break;
    case T_SINISTRA: usage = 0x50; break;
    case T_DESTRA: usage = 0x4F; break;
    case T_SHIFT_SINISTRA: mod = 0x02; usage = 0x50; break;
    case T_SHIFT_DESTRA: mod = 0x02; usage = 0x4F; break;
    case T_ALT_SINISTRA: mod = 0x04; usage = 0x50; break;
    case T_ALT_DESTRA: mod = 0x04; usage = 0x4F; break;
    case T_F13: usage = 0x68; break;
    case T_F14: usage = 0x69; break;
    case T_F15: usage = 0x6A; break;
    case T_F16: usage = 0x6B; break;
  }
}

Tasto tastoFreccia(int dir, int livello) {
  if (livello >= 3) return dir > 0 ? T_ALT_DESTRA : T_ALT_SINISTRA;
  if (livello == 2) return dir > 0 ? T_SHIFT_DESTRA : T_SHIFT_SINISTRA;
  return dir > 0 ? T_DESTRA : T_SINISTRA;
}

static int verso(Tasto t) {
  switch (t) {
    case T_DESTRA: case T_SHIFT_DESTRA: case T_ALT_DESTRA: return 1;
    case T_SINISTRA: case T_SHIFT_SINISTRA: case T_ALT_SINISTRA: return -1;
    default: return 0;
  }
}

static Tasto coda[CODA_MAX];
static int nCoda = 0;
static unsigned long ultimoInvio = 0;

// Unico punto di uscita verso l'iPad: report BLE HID (pressione con modificatore
// e tasto insieme, poi subito rilascio). Senza iPad collegato resta solo il log.
void tastoInvia(Tasto t) {
  uint8_t mod, usage;
  tastoHid(t, mod, usage);
  int r = bleInviaTasto(mod, usage);
  Serial.printf("TASTO %s %s %d\n", tastoNome(t), r == 1 ? "INVIATO" : r == 2 ? "INVIATO_FORZATO" : r == 0 ? "NON_COLLEGATO" : r == -2 ? "ERRORE_NOTIFICA" : "NON_SOTTOSCRITTO", nCoda);
}

void tastiAccoda(Tasto t) {
  int v = verso(t);
  if (v != 0) {
    // cancella le frecce del verso opposto ancora in coda
    int j = 0;
    for (int i = 0; i < nCoda; i++)
      if (verso(coda[i]) != -v) coda[j++] = coda[i];
    nCoda = j;
    if (nCoda >= CODA_MAX) return;  // satura: lo scatto in eccesso si perde
  } else if (nCoda >= CODA_MAX) {
    nCoda--;  // i tasti dei gesti non vanno mai persi
  }
  coda[nCoda++] = t;
}

void tastiAggiorna(unsigned long adesso) {
  if (nCoda == 0 || adesso - ultimoInvio < CADENZA_TASTI) return;
  ultimoInvio = adesso;
  Tasto t = coda[0];
  nCoda--;
  memmove(coda, coda + 1, nCoda * sizeof(Tasto));
  tastoInvia(t);
}

void tastiSvuota() { nCoda = 0; }
int tastiInCoda() { return nCoda; }
