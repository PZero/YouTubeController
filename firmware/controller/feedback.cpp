#include "feedback.h"
#include "config.h"
#include <Adafruit_NeoPixel.h>

static Adafruit_NeoPixel anello(NUM_LED, PIN_ANELLO, NEO_GRB + NEO_KHZ800);

static Effetto attuale = E_NESSUNO, fondo = E_NESSUNO;
static unsigned long inizio = 0, ultimoShow = 0, ultimoAcceso = 0;
static long sciaPos = 0;
static int sciaDir = 1, sciaLiv = 1, progresso = 0;
static bool alimentato = false, forza = true;

// posizione in senso orario (0 = LED di riferimento) -> indice fisico
static int led(long p) {
  int i = ((p % NUM_LED) + NUM_LED) % NUM_LED;
  return LED_ANTIORARIO ? NUM_LED - 1 - i : i;
}

static uint32_t col(uint8_t r, uint8_t g, uint8_t b, float k = 1.0f) {
  if (k < 0) k = 0;
  if (k > 1) k = 1;
  return anello.Color(r * k, g * k, b * k);
}

static void alimentazione(bool on) {
  if (on == alimentato) return;
  alimentato = on;
  if (on) {
    digitalWrite(PIN_ANELLO_ALIM, HIGH);
    delay(5);  // carica del bulk e reset dei WS2812B
  } else {
    // il dato e' gia' basso: livello di riposo dell'RMT dopo l'ultimo show() nero
    digitalWrite(PIN_ANELLO_ALIM, LOW);
  }
}

void feedbackInizia() {
  pinMode(PIN_ANELLO_ALIM, OUTPUT);
  digitalWrite(PIN_ANELLO_ALIM, LOW);
  pinMode(PIN_VIB, OUTPUT);
  digitalWrite(PIN_VIB, LOW);
  if (!ledcAttach(PIN_VIB, 20000, 8)) Serial.println("ERRORE vibrazione: ledcAttach non riuscito");  // 20 kHz
  ledcWrite(PIN_VIB, 0);
  anello.begin();
  anello.setBrightness(LUMINOSITA);
  alimentazione(true);
  anello.clear();
  anello.show();
}

static bool temporaneo(Effetto e) { return e >= E_SCIA && e <= E_USCITA; }

void effetto(Effetto e) {
  attuale = e;
  inizio = millis();
  forza = true;
}

void sfondo(Effetto e) {
  fondo = e;
  if (!temporaneo(attuale)) effetto(e);
}

void effettoFondo() { effetto(fondo); }

void effettoScia(long posizione, int dir, int livello) {
  sciaPos = posizione;
  sciaDir = dir;
  sciaLiv = livello;
  effetto(E_SCIA);
}

void effettoProgresso(int p) {
  progresso = p;
  if (attuale != E_PROGRESSO) effetto(E_PROGRESSO);
  forza = true;
}

void feedbackForza() {
  forza = true;
  feedbackAggiorna(millis());
}

// Disegna l'effetto attuale; restituisce false quando un effetto temporaneo e' finito.
static bool disegna(unsigned long t) {
  anello.clear();
  switch (attuale) {
    case E_NESSUNO:
    case E_ZONA_MORTA:
      break;
    case E_SCIA: {
      if (t >= 300) return false;
      float k = 1.0f - t / 300.0f;
      uint8_t r, g, b;
      if (sciaLiv >= 3) { r = 255; g = 90; b = 0; }        // veloce: arancio
      else if (sciaLiv == 2) { r = 255; g = 200; b = 0; }  // medio: giallo
      else { r = 0; g = 200; b = 255; }                    // lento: ciano
      const float scala[4] = {1.0f, 0.4f, 0.15f, 0.05f};
      for (int j = 0; j < 4; j++) anello.setPixelColor(led(sciaPos - j * sciaDir), col(r, g, b, k * scala[j]));
      break;
    }
    case E_LAMPO:
      if (t >= 80) return false;
      anello.fill(col(120, 120, 120));
      break;
    case E_GIRO_AMBRA: {
      if (t >= 400) return false;
      int n = 1 + t * NUM_LED / 400;
      for (int i = 0; i < n && i < NUM_LED; i++) anello.setPixelColor(led(i), col(255, 120, 0));
      break;
    }
    case E_STANDBY:
      if (t >= 600) return false;
      anello.fill(col(160, 0, 0, 1.0f - t / 600.0f));
      break;
    case E_VERDE:
      if (t >= 1000) return false;
      anello.fill(col(0, 200, 0));
      break;
    case E_ERRORE:
      if (t >= 1200) return false;
      if ((t / 200) % 2 == 0) anello.fill(col(200, 0, 0));
      break;
    case E_SVUOTA_ROSSO: {
      if (t >= 600) return false;
      int n = NUM_LED - t * NUM_LED / 600;  // si svuota in senso antiorario
      for (int i = 0; i < n; i++) anello.setPixelColor(led(i), col(200, 0, 0));
      break;
    }
    case E_BLE_CONN:
      if (t >= 300) return false;
      anello.fill(col(0, 40, 255));
      break;
    case E_BLE_DISC:
      if (t >= 600) return false;
      if ((t / 150) % 2 == 0) anello.fill(col(0, 20, 120));
      break;
    case E_BLE_ATTESA:
      if (t >= 60000) return false;
      anello.setPixelColor(led(t * NUM_LED / 2000), col(0, 40, 255));
      break;
    case E_USCITA:
      if (t >= 600) return false;
      if ((t / 150) % 2 == 0) anello.fill(col(80, 80, 80));
      break;
    case E_AMBRA4:
      for (int i = 0; i < NUM_LED; i += 4) anello.setPixelColor(led(i), col(255, 120, 0));
      break;
    case E_RIEMPI_ROSSO: {
      long ms = (long)t;  // t = tempo da quando si e' entrati nella zona 2-10 s
      int n = ms * NUM_LED / (SOGLIA_LUNGA - SOGLIA_ZONA_MORTA);
      for (int i = 0; i < n && i < NUM_LED; i++) anello.setPixelColor(led(i), col(120, 0, 0));
      break;
    }
    case E_VIOLA:
      anello.fill(col(150, 0, 255));
      break;
    case E_OTA_CONN: {
      float k = 0.25f + 0.75f * (0.5f + 0.5f * sinf(t * 2 * PI / 1500.0f));
      anello.fill(col(150, 0, 255, k));
      break;
    }
    case E_OTA_PRONTO:
      anello.fill(col(150, 0, 255, 0.2f));
      anello.setPixelColor(led(t * NUM_LED / 2000), col(255, 255, 255));
      break;
    case E_PORTALE:
      anello.fill((t / 1000) % 2 == 0 ? col(150, 0, 255) : col(100, 100, 100));
      break;
    case E_PROGRESSO: {
      int n = (progresso * NUM_LED + 50) / 100;
      for (int i = 0; i < NUM_LED; i++) anello.setPixelColor(led(i), i < n ? col(150, 0, 255) : col(15, 0, 25));
      break;
    }
  }
  return true;
}

static bool animato(Effetto e) {
  return e != E_NESSUNO && e != E_ZONA_MORTA && e != E_AMBRA4 && e != E_VIOLA && e != E_PROGRESSO;
}

static unsigned long vibFine = 0, vibAcceso = 0, vibSpento = 0;
static int vibResto = 0;
static bool vibOn = false;

void vibra(unsigned long ms) {
  vibraSerie(1, ms, 0);
}

static void vibAccendi() {
  ledcWrite(PIN_VIB, VIB_DUTY);
  vibOn = true;
  Serial.printf("VIB %lu\n", vibAcceso);
}

void vibraSerie(int n, unsigned long acceso, unsigned long spento) {
  if (acceso < VIB_MIN_MS) acceso = VIB_MIN_MS;  // sotto ~60 ms il motore non parte o non si sente
  vibResto = n - 1;
  vibAcceso = acceso;
  vibSpento = spento;
  vibAccendi();
  vibFine = millis() + acceso;
}

void feedbackAggiorna(unsigned long adesso) {
  // Vibrazione
  if ((long)(adesso - vibFine) >= 0) {
    if (vibOn) {
      ledcWrite(PIN_VIB, 0);
      vibOn = false;
      vibFine = adesso + vibSpento;
    } else if (vibResto > 0) {
      vibResto--;
      vibAccendi();
      vibFine = adesso + vibAcceso;
    }
  }

  // Anello
  if (!forza && (!animato(attuale) || adesso - ultimoShow < PERIODO_ANELLO)) {
    if (attuale == E_NESSUNO && alimentato && adesso - ultimoAcceso > ANELLO_SPEGNI_DOPO) alimentazione(false);
    return;
  }
  forza = false;
  ultimoShow = adesso;
  if (!disegna(adesso - inizio)) {
    attuale = fondo;
    inizio = adesso;
    disegna(0);
  }
  bool nero = true;
  for (int i = 0; i < NUM_LED && nero; i++) nero = anello.getPixelColor(i) == 0;
  if (nero) {
    if (alimentato) anello.show();
  } else {
    alimentazione(true);
    anello.show();
    ultimoAcceso = adesso;
  }
}
