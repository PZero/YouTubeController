// Configurazione del controller: pin, tempi e soglie in un solo posto.
#pragma once
#include <Arduino.h>

// Versione del firmware. In GitHub Actions si potra' passare -DFW_VERSION="x.y.z" dal tag della Release.
#ifndef FW_VERSION
#define FW_VERSION "0.1.2"
#endif

// ---- Pin (vedi firmware/README.md, "GPIO assegnati") ----
const int PIN_ENC_A = 4;
const int PIN_ENC_B = 5;
const int PIN_PULSANTE = 7;       // switch integrato dell'encoder, a GND
const int PIN_ANELLO = 2;         // DI dell'anello (330 ohm in serie)
const int PIN_ANELLO_ALIM = 9;    // comando interruttore anello (Q2/Q1); sul banco non collegato
const int PIN_VIB = 6;            // IN del modulo vibrazione

// ---- Anello ----
const int NUM_LED = 16;
const uint8_t LUMINOSITA = 40;              // su 255
const unsigned long PERIODO_ANELLO = 20;    // ms tra due aggiornamenti
const unsigned long ANELLO_SPEGNI_DOPO = 2000;  // ms a nero prima di togliere l'alimentazione
const bool LED_ANTIORARIO = true;           // LED numerati in senso antiorario visti dall'alto

// ---- Vibrazione: impulsi a piena potenza (sotto ~30 ms o al 60% il motore non parte) ----
const uint8_t VIB_DUTY = 255;               // sempre piena potenza
const unsigned long VIB_MIN_MS = 60;        // impulsi piu' corti vengono allungati a 60 ms
const bool VIB_SU_SCATTO = true;            // vibrazione a ogni scatto (richiesta dell'utente)
const unsigned long VIB_SCATTO = 60;        // ms per scatto
const unsigned long VIB_PAUSA_SCATTI = 110; // ms minimi tra due impulsi da scatto (giro veloce)
const bool VIB_SU_PRESSIONE = true;         // impulso alla pressione del pulsante, come test_comandi
const unsigned long VIB_PULSANTE = 60;

// ---- Pulsante e gesti (ms) ----
const unsigned long DEBOUNCE_MS = 30;
const unsigned long SOGLIA_MEDIA = 700;     // < 0,7 s breve
const unsigned long SOGLIA_ZONA_MORTA = 2000;  // 0,7-2 s media, 2-10 s nulla
const unsigned long SOGLIA_LUNGA = 10000;   // >= 10 s standby
const int SCATTI_GESTO = 5;                 // premuto + 5 scatti = OTA / azzera WiFi

// ---- Velocita' della manopola (scatti/s) ----
const float VEL_MEDIA = 5.0f;               // da lento a medio
const float VEL_VELOCE = 12.0f;             // da medio a veloce
const float ISTERESI = 0.8f;                // si scende sotto soglia*0,8 per 2 scatti
const unsigned long PAUSA_RESET_VEL = 300;  // primo scatto dopo una pausa = lento

// ---- Coda dei tasti (simula la cadenza BLE) ----
const int CODA_MAX = 40;
const unsigned long CADENZA_TASTI = 33;     // ms minimi tra due tasti

// ---- BLE ----
#define BLE_NOME "YouTube Controller"
const uint8_t BLE_BATTERIA_SIMULATA = 100;  // batteria scollegata: livello fisso

// ---- Rete ----
// Password della rete di configurazione: NON e' un segreto (e' pubblica nel repository).
// Serve solo a non far collegare per sbaglio dispositivi di passaggio; si puo' sostituire
// con una propria salvata in NVS (chiave "ap_pass") dalla pagina di configurazione.
#define AP_PASSWORD_DEFAULT "ytcontroller"
const unsigned long WIFI_TIMEOUT = 20000;     // connessione al WiFi di casa
const unsigned long MODO_TIMEOUT = 300000;    // 5 min senza attivita' -> uscita da OTA / portale
#define OTA_URL_JSON "https://github.com/PZero/YouTubeController/releases/latest/download/firmware.json"
#define OTA_URL_BIN  "https://github.com/PZero/YouTubeController/releases/latest/download/firmware.bin"
#define MDNS_NOME "ytcontroller"

// ---- Batteria ----
// Sul banco la batteria e' scollegata e il partitore su GPIO1 non c'e': controllo disattivato.
const bool CONTROLLO_BATTERIA = false;
const int PIN_BATTERIA = 1;
const float VBAT_MIN_OTA = 3.7f;
