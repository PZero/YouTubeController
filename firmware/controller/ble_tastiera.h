// Tastiera BLE HID con la libreria BLE del core esp32 3.x (backend NimBLE).
#pragma once
#include <Arduino.h>

void bleInizia();
// Da chiamare a ogni loop: trasforma gli eventi del task BLE in righe di log.
// Restituisce +1 appena connesso, -1 appena disconnesso, 0 altrimenti.
int bleAggiorna();
bool bleCollegato();
// Pressione (modificatore + tasto insieme) e subito rilascio.
// 1 inviato, 2 inviato forzato (link cifrato ma sottoscrizione non vista), 0 non collegato,
// -1 collegato ma non cifrato e non sottoscritto, -2 errore di notifica.
int bleInviaTasto(uint8_t modificatore, uint8_t usage);
// Livello batteria (0-100) per il widget Batterie di iPadOS.
void bleBatteria(uint8_t percento);
// Avvio in modalita' rete (OTA / portale): il BLE non viene inizializzato.
void bleNonAvviare();
bool bleSospesa();  // true se il BLE non e' attivo
