// Ingressi: encoder in interrupt, pulsante con antirimbalzo, livello di velocita'.
#pragma once
#include <Arduino.h>

void ingressiInizia();

// Posizione assoluta contata dall'interrupt (scatti).
int32_t encoderPosizione();
uint32_t encoderNonValide();

// Pulsante: chiamare a ogni giro di loop. Restituisce +1 alla pressione stabile,
// -1 al rilascio stabile, 0 altrimenti. durataMs valido al rilascio.
int pulsanteAggiorna(unsigned long adesso, unsigned long &durataMs);
bool pulsantePremuto();
unsigned long pulsanteInizio();

// Velocita': da chiamare a ogni scatto (dir = +1/-1). Restituisce il livello 1/2/3.
int velocitaScatto(int dir, unsigned long adesso);
float velocitaUltima();  // scatti/s medi (per il log)
