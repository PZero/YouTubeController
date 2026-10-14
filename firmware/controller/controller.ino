// YouTube Controller - firmware v0 (ESP32-S3 SuperMini)
// Encoder EC11E (A=GPIO4, B=GPIO5) + switch integrato (GPIO7), anello WS2812B 16 LED (GPIO2),
// vibrazione (GPIO6), tastiera BLE HID, WiFi/portale/OTA attivati dai gesti.
// Log su seriale USB: una riga per evento, prefissi stabili (vedi README.md in questa cartella).

#include "config.h"
#include "ingressi.h"
#include "feedback.h"
#include "tasti.h"
#include "ble_tastiera.h"
#include "rete.h"
#include <esp_ota_ops.h>

// Rollback OTA: la nuova immagine resta "in prova" finche' loop() non la convalida.
bool verifyRollbackLater() { return true; }

static const unsigned long CONVALIDA_DOPO = 10000;
static bool inProva = false;

// ---- Stato del gesto in corso (una pressione) ----
static bool rotatoInPressione = false;  // qualunque scatto annulla breve/media/lunga
static bool gestoFatto = false;         // gesto gia' eseguito: il rilascio viene ignorato
static int versoScatti = 0, contaScatti = 0;
static int fase = 0;                    // 0 <0,7 s, 1 0,7-2 s, 2 2-10 s, 3 lunga eseguita

static int32_t posizione = 0;
static unsigned long ultimoVivo = 0;

static void gesto(const char *nome, const char *extra = "") {
  Serial.printf("GESTO %s%s%s\n", nome, *extra ? " " : "", extra);
}

static void scatto(int dir, unsigned long adesso) {
  posizione += dir;
  if (reteAttiva()) reteAttivita();

  if (pulsantePremuto()) {
    Serial.printf("ENC %+d %ld 0 0\n", dir, (long)posizione);
    if (!rotatoInPressione && fase >= 1) effettoFondo();  // via ambra / rosso
    rotatoInPressione = true;
    if (gestoFatto) return;
    if (dir == versoScatti) contaScatti++;
    else { versoScatti = dir; contaScatti = 1; }
    if (contaScatti >= SCATTI_GESTO) {
      gestoFatto = true;
      if (dir > 0) { gesto("OTA"); reteEntraOta(); }
      else { gesto("RESET_WIFI"); reteAzzeraWifi(); }
    }
    return;
  }

  int liv = velocitaScatto(dir, adesso);
  Serial.printf("ENC %+d %ld %d %.1f\n", dir, (long)posizione, liv, velocitaUltima());
  if (reteAttiva()) return;  // in OTA / portale la manopola non invia tasti
  tastiAccoda(tastoFreccia(dir, liv));
  effettoScia(posizione, dir, liv);
  if (VIB_SU_SCATTO) vibra(40);
}

static void pressione() {
  rotatoInPressione = false;
  gestoFatto = false;
  versoScatti = 0;
  contaScatti = 0;
  fase = 0;
  Serial.println("BTN 1");
  if (reteAttiva()) reteAttivita();
}

static void rilascio(unsigned long durata) {
  Serial.printf("BTN 0 %lu\n", durata);
  if (gestoFatto) return;
  if (rotatoInPressione) { gesto("ANNULLATO", "rotazione"); return; }

  if (reteAttiva()) {
    // in OTA / portale: pressione breve = uscita (riavvio)
    if (durata < SOGLIA_MEDIA) { gesto("BREVE", "uscita"); reteEsci("pulsante"); }
    else gesto("ANNULLATO", "modo_rete");
    return;
  }

  if (durata < SOGLIA_MEDIA) {
    gesto("BREVE");
    tastiAccoda(T_SPAZIO);
    effetto(E_LAMPO);
  } else if (durata < SOGLIA_ZONA_MORTA) {
    gesto("MEDIA");
    tastiAccoda(T_L);
    effetto(E_GIRO_AMBRA);
    vibra(60);
  } else {
    gesto("ANNULLATO", "zona_morta");
    effettoFondo();
  }
}

// Soglie raggiunte con il pulsante ancora premuto e nessuna rotazione
static void pulsanteTenuto(unsigned long adesso) {
  if (!pulsantePremuto() || rotatoInPressione || gestoFatto || reteAttiva()) return;
  unsigned long d = adesso - pulsanteInizio();
  if (fase < 1 && d >= SOGLIA_MEDIA) {
    fase = 1;
    effetto(E_AMBRA4);
    vibra(30);
  }
  if (fase < 2 && d >= SOGLIA_ZONA_MORTA) {
    fase = 2;
    effetto(E_RIEMPI_ROSSO);
  }
  if (fase < 3 && d >= SOGLIA_LUNGA) {
    fase = 3;
    gestoFatto = true;
    gesto("LUNGA");
    Serial.println("INFO STANDBY (simulato): deep sleep disattivato nel prototipo, F14 non inviato");
    effetto(E_STANDBY);
    vibra(300);
  }
}

static const char *motivoReset() {
  switch (esp_reset_reason()) {
    case ESP_RST_POWERON: return "accensione";
    case ESP_RST_SW: return "software";
    case ESP_RST_PANIC: return "errore";
    case ESP_RST_INT_WDT: case ESP_RST_TASK_WDT: case ESP_RST_WDT: return "watchdog";
    case ESP_RST_BROWNOUT: return "brownout";
    case ESP_RST_DEEPSLEEP: return "deepsleep";
    case ESP_RST_USB: return "usb";
    default: return "altro";
  }
}

void setup() {
  pinMode(PIN_ANELLO_ALIM, OUTPUT);
  digitalWrite(PIN_ANELLO_ALIM, LOW);  // anello spento prima di tutto
  pinMode(PIN_VIB, OUTPUT);
  digitalWrite(PIN_VIB, LOW);          // motore fermo
  Serial.setTxTimeoutMs(0);            // senza monitor collegato la seriale non deve bloccare
  Serial.begin(115200);
  delay(300);

  const esp_partition_t *p = esp_ota_get_running_partition();
  esp_ota_img_states_t st;
  inProva = esp_ota_get_state_partition(p, &st) == ESP_OK && st == ESP_OTA_IMG_PENDING_VERIFY;
  Serial.printf("INFO YTController %s app=%s reset=%s%s\n", FW_VERSION, p ? p->label : "?", motivoReset(),
                inProva ? " IN_PROVA" : "");

  feedbackInizia();
  ingressiInizia();
  reteInizia();
  bleInizia();
  sfondo(E_NESSUNO);
  effetto(E_BLE_ATTESA);
  Serial.println("INFO pronto");
}

void loop() {
  unsigned long adesso = millis();

  int32_t nuova = encoderPosizione();
  while (posizione != nuova) scatto(nuova > posizione ? 1 : -1, adesso);

  unsigned long durata;
  int ev = pulsanteAggiorna(adesso, durata);
  if (ev > 0) pressione();
  else if (ev < 0) rilascio(durata);
  pulsanteTenuto(adesso);

  int b = bleAggiorna();
  if (b > 0) { effetto(E_BLE_CONN); vibra(50); }
  else if (b < 0 && !bleSospesa()) effetto(E_BLE_DISC);

  tastiAggiorna(adesso);
  reteAggiorna(adesso);
  feedbackAggiorna(millis());

  if (inProva && adesso > CONVALIDA_DOPO) {
    inProva = false;
    esp_ota_mark_app_valid_cancel_rollback();
    Serial.println("OTA CONVALIDATA");
  }

  if (adesso - ultimoVivo >= 5000) {
    ultimoVivo = adesso;
    Serial.printf("VIVO %lu %lu %u %s\n", adesso / 1000, (unsigned long)encoderNonValide(),
                  (unsigned)(ESP.getFreeHeap() / 1024), bleCollegato() ? "BLE_CONNESSO" : (bleSospesa() ? "BLE_SOSPESO" : "BLE_PUBBLICITA"));
  }

  delay(1);
}
