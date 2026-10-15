// Sospensione: deep sleep con risveglio dallo switch dell'encoder (GPIO7, ext1 attivo basso).
#pragma once
#include <Arduino.h>

// Da chiamare all'inizio di setup(), prima di anello e BLE. Se il chip si e' svegliato dal
// pulsante, verifica che resti premuto RISVEGLIO_CONFERMA ms; se no torna subito in deep sleep
// (non ritorna). Restituisce true se il risveglio e' confermato (pulsante ancora premuto).
bool sospensioneRisveglio();

// Spegnimento: vibrazione lunga, anello nero, BLE disconnesso, attesa del rilascio del
// pulsante, pin mantenuti bassi, deep sleep. Non ritorna.
void sospendiOra(const char *motivo);
