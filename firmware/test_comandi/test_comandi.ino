// Test dei comandi: encoder EC11E + pulsante integrato + anello WS2812B 16 LED + vibrazione (ESP32-S3 SuperMini)
// A = GPIO4, B = GPIO5, C = GND; pulsante = GPIO7 e GND (pull-up interni).
// Anello: DI = GPIO2 (330 ohm in serie), alimentazione provvisoria da 5V/GND della scheda.
// Vibrazione: IN = GPIO6, VCC provvisorio da 5V. Impulsi brevi a piena potenza ("kick"):
// a 12 ms e 60% il motore non fa in tempo a partire.
// Encoder letto in interrupt: il conteggio non dipende dall'aggiornamento dell'anello.
// Seriale (USB, 115200): righe leggibili anche da monitor.html (Web Serial)
//   ENC <+1|-1> <posizione> <scatti nel blocco>
//   BTN 1                 pulsante premuto
//   BTN 0 <ms>            pulsante rilasciato dopo <ms>
//   VIVO <s> <errori>     battito ogni 5 s (errori = transizioni non valide)

#include <Adafruit_NeoPixel.h>

const int PIN_A = 4;
const int PIN_B = 5;
const int PIN_SW = 7;
const int PIN_ANELLO = 2;
const int PIN_VIB = 6;
const int NUM_LED = 16;
const uint8_t LUMINOSITA = 40;            // su 255: sicuro anche dalla USB
const unsigned long PERIODO_ANELLO = 20;  // ms tra due aggiornamenti dell'anello
const uint8_t VIB_DUTY = 255;             // piena potenza: impulsi brevi, il motore da 3 V li regge
const unsigned long VIB_SCATTO = 60;      // ms di vibrazione per ogni scatto
const unsigned long VIB_PAUSA_SCATTI = 110;  // ms minimi tra due vibrazioni da scatto (giro veloce)
const unsigned long VIB_PULSANTE = 60;    // ms di vibrazione alla pressione

Adafruit_NeoPixel anello(NUM_LED, PIN_ANELLO, NEO_GRB + NEO_KHZ800);

// Tabella di quadratura: indice = (stato precedente << 2) | stato attuale
const int8_t TABELLA[16] = {0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0};

// Stato dell'encoder, aggiornato solo dall'interrupt
volatile uint8_t statoAB;
volatile int8_t transizioni = 0;
volatile int32_t posizioneIsr = 0;
volatile uint32_t nonValide = 0;

int32_t posizione = 0;  // ultima posizione mostrata
int ultimaDir = 1;

bool swPremuto = false;
bool swLetto = false;
unsigned long swCambio = 0;
unsigned long swInizio = 0;
unsigned long ultimoAnello = 0;
unsigned long ultimoVivo = 0;
bool anelloDaAggiornare = true;
unsigned long vibFine = 0;
unsigned long vibUltimoScatto = 0;
bool vibAccesa = false;

void vibra(unsigned long ms, uint8_t duty = VIB_DUTY) {
  ledcWrite(PIN_VIB, duty);
  vibAccesa = true;
  vibFine = millis() + ms;
}

void IRAM_ATTR isrEncoder() {
  uint8_t ora = (digitalRead(PIN_A) << 1) | digitalRead(PIN_B);
  if (ora == statoAB) return;
  int8_t d = TABELLA[(statoAB << 2) | ora];
  if (d == 0) nonValide++;
  transizioni += d;
  statoAB = ora;
  // Encoder 20 impulsi / 20 scatti: 4 transizioni per scatto, riposo su A=B=1
  if (ora == 3) {
    if (transizioni >= 2) posizioneIsr++;
    else if (transizioni <= -2) posizioneIsr--;
    transizioni = 0;
  }
}

// I LED dell'anello sono numerati in senso antiorario (visti dall'alto): indice invertito
int indiceLed(long pos) {
  return NUM_LED - 1 - ((pos % NUM_LED) + NUM_LED) % NUM_LED;
}

// LED della posizione acceso, i due precedenti come scia; verde avanti, arancio indietro
void mostraPosizione() {
  anello.clear();
  uint8_t r = ultimaDir > 0 ? 0 : 255;
  uint8_t g = ultimaDir > 0 ? 255 : 90;
  uint8_t b = ultimaDir > 0 ? 120 : 0;
  for (int k = 2; k >= 0; k--) {
    int div = 1 << (k * 2);  // 1, 4, 16
    anello.setPixelColor(indiceLed(posizione - k * ultimaDir), r / div, g / div, b / div);
  }
  anello.show();
}

void mostraPulsante() {
  anello.fill(anello.Color(60, 60, 255));
  anello.show();
}

void setup() {
  pinMode(PIN_VIB, OUTPUT);
  digitalWrite(PIN_VIB, LOW);  // motore fermo prima di tutto
  Serial.setTxTimeoutMs(0);  // senza pagina collegata la seriale non deve bloccare
  Serial.begin(115200);
  pinMode(PIN_A, INPUT_PULLUP);
  pinMode(PIN_B, INPUT_PULLUP);
  pinMode(PIN_SW, INPUT_PULLUP);
  anello.begin();
  anello.setBrightness(LUMINOSITA);
  anello.clear();
  anello.show();
  ledcAttach(PIN_VIB, 20000, 8);  // PWM a 20 kHz, non udibile
  ledcWrite(PIN_VIB, 0);
  delay(1000);
  statoAB = (digitalRead(PIN_A) << 1) | digitalRead(PIN_B);
  attachInterrupt(digitalPinToInterrupt(PIN_A), isrEncoder, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_B), isrEncoder, CHANGE);
  Serial.println("INFO Test encoder + anello pronto (interrupt)");
}

void loop() {
  unsigned long adesso = millis();

  // Encoder: legge la posizione contata dall'interrupt
  int32_t nuova = posizioneIsr;
  if (nuova != posizione) {
    int delta = nuova - posizione;
    ultimaDir = delta > 0 ? 1 : -1;
    posizione = nuova;
    Serial.printf("ENC %+d %ld %d\n", ultimaDir, (long)posizione, delta);
    anelloDaAggiornare = true;
    if (!swPremuto && adesso - vibUltimoScatto >= VIB_PAUSA_SCATTI) {
      vibUltimoScatto = adesso;
      vibra(VIB_SCATTO);
    }
  }

  // Pulsante con antirimbalzo 30 ms
  bool letto = digitalRead(PIN_SW) == LOW;
  if (letto != swLetto) {
    swLetto = letto;
    swCambio = adesso;
  }
  if (adesso - swCambio > 30 && swLetto != swPremuto) {
    swPremuto = swLetto;
    if (swPremuto) {
      swInizio = adesso;
      Serial.println("BTN 1");
      vibra(VIB_PULSANTE);
    } else {
      Serial.printf("BTN 0 %lu\n", adesso - swInizio);
    }
    anelloDaAggiornare = true;
  }

  // Anello: al massimo un aggiornamento ogni PERIODO_ANELLO ms
  if (anelloDaAggiornare && adesso - ultimoAnello >= PERIODO_ANELLO) {
    ultimoAnello = adesso;
    anelloDaAggiornare = false;
    if (swPremuto) mostraPulsante();
    else mostraPosizione();
  }

  if (vibAccesa && (long)(millis() - vibFine) >= 0) {
    ledcWrite(PIN_VIB, 0);
    vibAccesa = false;
  }

  if (adesso - ultimoVivo >= 5000) {
    ultimoVivo = adesso;
    Serial.printf("VIVO %lu %lu\n", adesso / 1000, (unsigned long)nonValide);
  }

  delay(1);
}
