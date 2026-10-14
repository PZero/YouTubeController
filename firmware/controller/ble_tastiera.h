// Tastiera BLE HID con la libreria BLE del core esp32 3.x (backend NimBLE).
#pragma once
#include <Arduino.h>

void bleInizia();
// Da chiamare a ogni loop: trasforma gli eventi del task BLE in righe di log.
// Restituisce +1 appena connesso, -1 appena disconnesso, 0 altrimenti.
int bleAggiorna();
bool bleCollegato();
// Pressione (modificatore + tasto insieme) e subito rilascio. false se non collegato.
bool bleInviaTasto(uint8_t modificatore, uint8_t usage);
// Livello batteria (0-100) per il widget Batterie di iPadOS.
void bleBatteria(uint8_t percento);
// Sospende la tastiera (scollega l'iPad e ferma la pubblicita'): usata in OTA / portale.
void bleSospendi();
bool bleSospesa();
