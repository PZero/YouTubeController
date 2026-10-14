// Tasti da inviare all'iPad via BLE HID, con log "TASTO <nome> INVIATO|NON_COLLEGATO <in coda>".
#pragma once
#include <Arduino.h>

enum Tasto : uint8_t {
  T_SPAZIO, T_L,
  T_SINISTRA, T_DESTRA,
  T_SHIFT_SINISTRA, T_SHIFT_DESTRA,
  T_ALT_SINISTRA, T_ALT_DESTRA,
  T_F13, T_F14, T_F15, T_F16,
};

const char *tastoNome(Tasto t);
// Modificatore e usage HID (mappa in firmware/README.md e app/js/keymap.js).
void tastoHid(Tasto t, uint8_t &modificatore, uint8_t &usage);

// Freccia per una rotazione: dir +1 avanti / -1 indietro, livello 1/2/3.
Tasto tastoFreccia(int dir, int livello);

// Coda con cadenza minima: un cambio di verso cancella le frecce opposte in coda.
void tastiAccoda(Tasto t);
void tastiAggiorna(unsigned long adesso);
void tastiSvuota();
// Invio immediato senza coda (F13/F15 prima di sospendere il BLE).
void tastoInvia(Tasto t);
int tastiInCoda();
