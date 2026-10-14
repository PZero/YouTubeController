// Riscontro all'utente: anello WS2812B e vibrazione, non bloccanti.
#pragma once
#include <Arduino.h>

enum Effetto : uint8_t {
  E_NESSUNO,      // nero (poi alimentazione anello tolta)
  // temporanei: finiscono da soli e tornano allo sfondo
  E_SCIA,         // scia di 4 LED nel verso della manopola, colore per livello, 300 ms
  E_LAMPO,        // lampo bianco tenue 80 ms (pressione breve)
  E_GIRO_AMBRA,   // giro ambra 400 ms (loop A-B)
  E_STANDBY,      // rosso pieno che si dissolve 600 ms
  E_VERDE,        // verde pieno 1 s (OTA riuscito)
  E_ERRORE,       // rosso lampeggiante 3 volte
  E_SVUOTA_ROSSO, // rosso che si svuota in senso antiorario (azzera WiFi)
  E_BLE_CONN,     // lampo blu 300 ms
  E_BLE_DISC,     // 2 lampi blu tenui
  E_BLE_ATTESA,   // 1 LED blu che gira (1 giro / 2 s), si spegne dopo 60 s
  E_USCITA,       // 2 lampi bianchi tenui (uscita da OTA / portale)
  // persistenti: restano finche' non vengono sostituiti
  E_AMBRA4,       // 4 LED ambra (soglia 0,7 s)
  E_ZONA_MORTA,   // anello spento (soglia 2 s)
  E_RIEMPI_ROSSO, // da 2 a 10 s si riempie di rosso in senso orario
  E_VIOLA,        // viola fisso (ingresso in aggiornamento)
  E_OTA_CONN,     // viola che pulsa (connessione al WiFi di casa)
  E_OTA_PRONTO,   // viola tenue + 1 LED bianco che gira (pagina OTA pronta)
  E_PORTALE,      // viola e bianco alternati lenti (rete di configurazione aperta)
  E_PROGRESSO,    // barra viola: LED accesi = % (parametro)
};

void feedbackInizia();
void feedbackAggiorna(unsigned long adesso);
// Effetto in primo piano. Gli effetti temporanei tornano poi allo sfondo.
void effetto(Effetto e);
void effettoScia(long posizione, int dir, int livello);
void effettoProgresso(int percento);
// Sfondo (stato della modalita'): mostrato quando non c'e' un effetto temporaneo.
void sfondo(Effetto e);
// Interrompe l'effetto in primo piano e torna allo sfondo.
void effettoFondo();
// Forza un aggiornamento immediato (da usare nei cicli bloccanti, es. download).
void feedbackForza();

void vibra(unsigned long ms);
void vibraSerie(int n, unsigned long acceso, unsigned long spento);
