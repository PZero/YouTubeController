// WiFi di casa (credenziali solo in NVS), rete di configurazione con portale captive, OTA.
// Il WiFi e' spento nell'uso normale: si accende solo con i gesti (pulsante + 5 scatti).
#pragma once
#include <Arduino.h>

enum StatoRete : uint8_t { R_SPENTA, R_CONNESSIONE, R_OTA, R_PORTALE };

void reteInizia();
void reteAggiorna(unsigned long adesso);
StatoRete reteStato();
bool reteAttiva();          // OTA o portale in corso: i gesti normali sono sospesi
void reteAttivita();        // azzera il timeout di 5 min

void reteEntraOta();        // gesto premuto + 5 scatti avanti
void reteAzzeraWifi();      // gesto premuto + 5 scatti indietro
void reteEsci(const char *motivo);  // uscita: riavvio pulito (BLE riparte)
