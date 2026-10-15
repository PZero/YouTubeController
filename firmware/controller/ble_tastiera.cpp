#include "ble_tastiera.h"
#include "config.h"
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLESecurity.h>
#include <host/ble_store.h>
#include <host/ble_gap.h>
#include <host/ble_gatt.h>
#include <host/ble_hs_mbuf.h>

// Report map: tastiera standard (8 byte: modificatori, riservato, 6 tasti) con Report ID 1,
// piu' report di uscita per i LED (richiesto da alcuni host, ignorato).
static const uint8_t REPORT_MAP[] = {
  0x05, 0x01,        // Usage Page (Generic Desktop)
  0x09, 0x06,        // Usage (Keyboard)
  0xA1, 0x01,        // Collection (Application)
  0x85, 0x01,        //   Report ID (1)
  0x05, 0x07,        //   Usage Page (Keyboard/Keypad)
  0x19, 0xE0,        //   Usage Minimum (Left Control)
  0x29, 0xE7,        //   Usage Maximum (Right GUI)
  0x15, 0x00,        //   Logical Minimum (0)
  0x25, 0x01,        //   Logical Maximum (1)
  0x75, 0x01,        //   Report Size (1)
  0x95, 0x08,        //   Report Count (8)
  0x81, 0x02,        //   Input (Data, Variable, Absolute): modificatori
  0x95, 0x01,        //   Report Count (1)
  0x75, 0x08,        //   Report Size (8)
  0x81, 0x01,        //   Input (Constant): riservato
  0x95, 0x05,        //   Report Count (5)
  0x75, 0x01,        //   Report Size (1)
  0x05, 0x08,        //   Usage Page (LEDs)
  0x19, 0x01,        //   Usage Minimum (Num Lock)
  0x29, 0x05,        //   Usage Maximum (Kana)
  0x91, 0x02,        //   Output (Data, Variable, Absolute): LED
  0x95, 0x01,        //   Report Count (1)
  0x75, 0x03,        //   Report Size (3)
  0x91, 0x01,        //   Output (Constant): padding
  0x95, 0x06,        //   Report Count (6)
  0x75, 0x08,        //   Report Size (8)
  0x15, 0x00,        //   Logical Minimum (0)
  0x25, 0x73,        //   Logical Maximum (0x73, fino a F24)
  0x05, 0x07,        //   Usage Page (Keyboard/Keypad)
  0x19, 0x00,        //   Usage Minimum (0)
  0x29, 0x73,        //   Usage Maximum (0x73)
  0x81, 0x00,        //   Input (Data, Array): tasti
  0xC0               // End Collection
};

static BLEServer *server = nullptr;
static BLECharacteristic *ingresso = nullptr;
static BLECharacteristic *batteria = nullptr;
static volatile bool collegato = false;
static volatile bool sottoscritto = false;   // l'iPad ha abilitato le notifiche dell'Input Report
static volatile int eventoConn = 0;          // +1 connesso, -1 disconnesso (dal task BLE)
static volatile int eventoNotifiche = -1;    // ultimo valore CCCD da loggare (-1 = nessuno)
static volatile int eventoSicurezza = 0;     // 1 ok, 2 errore
static volatile int sicurezzaStato = 0, sicurezzaCifrato = 0, sicurezzaBond = 0;
static bool sospesa = false;
static volatile uint16_t connHandle = 0xFFFF;
static volatile bool cifrato = false;
// Ultimo evento SUBSCRIBE visto dal listener GAP (qualsiasi attributo), da loggare nel loop
static volatile int subHandle = -1, subNotify = 0, subReason = 0;
static ble_gap_event_listener ascoltatore;

// Listener GAP indipendente dalla libreria: vede tutte le sottoscrizioni (CCCD) e la cifratura.
static int eventoGap(struct ble_gap_event *ev, void *) {
  switch (ev->type) {
    case BLE_GAP_EVENT_CONNECT:
      if (ev->connect.status == 0) connHandle = ev->connect.conn_handle;
      break;
    case BLE_GAP_EVENT_DISCONNECT:
      connHandle = 0xFFFF;
      cifrato = false;
      break;
    case BLE_GAP_EVENT_ENC_CHANGE:
      if (ev->enc_change.status == 0) cifrato = true;
      break;
    case BLE_GAP_EVENT_SUBSCRIBE:
      subNotify = ev->subscribe.cur_notify;
      subReason = ev->subscribe.reason;
      subHandle = ev->subscribe.attr_handle;
      if (ingresso && ev->subscribe.attr_handle == ingresso->getHandle()) sottoscritto = ev->subscribe.cur_notify;
      break;
  }
  return 0;
}

class CallbackServer : public BLEServerCallbacks {
  void onConnect(BLEServer *) override {
    collegato = true;
    eventoConn = 1;
  }
  void onDisconnect(BLEServer *) override {
    collegato = false;
    sottoscritto = false;
    eventoConn = -1;
  }
};

class CallbackIngresso : public BLECharacteristicCallbacks {
  void onSubscribe(BLECharacteristic *, ble_gap_conn_desc *, uint16_t valore) override {
    sottoscritto = (valore & 0x0001) != 0;
    eventoNotifiche = valore;
  }
};

class CallbackSicurezza : public BLESecurityCallbacks {
  bool onSecurityRequest() override { return true; }
  uint32_t onPassKeyRequest() override { return 0; }
  void onPassKeyNotify(uint32_t) override {}
  bool onConfirmPIN(uint32_t) override { return true; }
  void onAuthenticationComplete(ble_gap_conn_desc *) override {}
  void onAuthenticationComplete(ble_gap_conn_desc *desc, int status) override {
    sicurezzaStato = status;
    sicurezzaCifrato = desc ? desc->sec_state.encrypted : 0;
    sicurezzaBond = desc ? desc->sec_state.bonded : 0;
    eventoSicurezza = status == 0 ? 1 : 2;
  }
};

static void riferimentoReport(BLECharacteristic *c, uint8_t id, uint8_t tipo) {
  BLEDescriptor *d = new BLEDescriptor(BLEUUID((uint16_t)0x2908));
  // NimBLE: serve BLE_ATT_F_READ oltre a READ_ENC, altrimenti il descrittore non e' leggibile
  // e iOS non sa a quale report appartiene la caratteristica (niente sottoscrizione).
  d->setAccessPermissions(ESP_GATT_PERM_READ | ESP_GATT_PERM_READ_ENCRYPTED);
  uint8_t v[2] = {id, tipo};
  d->setValue(v, 2);
  c->addDescriptor(d);
}

// Servizi HID costruiti a mano (invece di BLEHIDDevice del core) per avere, come
// NimBLEHIDDevice usato da ESP32-BLE-Keyboard di T-vK, i report accessibili solo su
// link cifrato: iOS consegna i tasti solo da una tastiera abbinata e cifrata.
void bleInizia() {
  BLEDevice::init(BLE_NOME);
  ble_gap_event_listener_register(&ascoltatore, eventoGap, nullptr);
  // "Just Works" con bonding e Secure Connections: nessun PIN, ricollegamento automatico.
  BLESecurity *sicurezza = new BLESecurity();
  sicurezza->setCapability(ESP_IO_CAP_NONE);
  sicurezza->setAuthenticationMode(true, false, true);
  // Scambio anche delle chiavi di identita' (IRK): l'iPad usa indirizzi privati che cambiano;
  // senza la sua IRK il bonding salvato non viene riconosciuto e serve riabbinare ogni volta.
  sicurezza->setInitEncryptionKey(ESP_BLE_ENC_KEY_MASK | ESP_BLE_ID_KEY_MASK);
  sicurezza->setRespEncryptionKey(ESP_BLE_ENC_KEY_MASK | ESP_BLE_ID_KEY_MASK);
  BLEDevice::setSecurityCallbacks(new CallbackSicurezza());

  server = BLEDevice::createServer();
  server->setCallbacks(new CallbackServer());
  server->advertiseOnDisconnect(true);

  // Device Information
  BLEService *info = server->createService(BLEUUID((uint16_t)0x180A));
  uint8_t pnp[] = {0x02, 0x3A, 0x30, 0x01, 0x40, 0x00, 0x01};  // USB, VID 0x303A, PID 0x4001, v1.0 (little endian)
  info->createCharacteristic((uint16_t)0x2A50, BLECharacteristic::PROPERTY_READ)->setValue(pnp, sizeof(pnp));
  info->createCharacteristic((uint16_t)0x2A29, BLECharacteristic::PROPERTY_READ)->setValue("PZero");

  // HID
  BLEService *hidSvc = server->createService(BLEUUID((uint16_t)0x1812), 40);
  uint8_t hidInfo[] = {0x11, 0x01, 0x00, 0x02};  // HID 1.11, nessun paese, normally connectable
  hidSvc->createCharacteristic((uint16_t)0x2A4A, BLECharacteristic::PROPERTY_READ)->setValue(hidInfo, sizeof(hidInfo));
  BLECharacteristic *mappa = hidSvc->createCharacteristic((uint16_t)0x2A4B, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_READ_ENC);
  mappa->setValue((uint8_t *)REPORT_MAP, sizeof(REPORT_MAP));
  hidSvc->createCharacteristic((uint16_t)0x2A4C, BLECharacteristic::PROPERTY_WRITE_NR | BLECharacteristic::PROPERTY_WRITE_ENC);
  uint8_t modo[] = {0x01};  // report protocol
  hidSvc->createCharacteristic((uint16_t)0x2A4E, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE_NR | BLECharacteristic::PROPERTY_READ_ENC | BLECharacteristic::PROPERTY_WRITE_ENC)->setValue(modo, 1);
  ingresso = hidSvc->createCharacteristic((uint16_t)0x2A4D, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_READ_ENC);
  ingresso->setCallbacks(new CallbackIngresso());
  riferimentoReport(ingresso, 1, 0x01);
  uint8_t zero[8] = {0};
  ingresso->setValue(zero, sizeof(zero));
  BLECharacteristic *uscita = hidSvc->createCharacteristic((uint16_t)0x2A4D, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR | BLECharacteristic::PROPERTY_READ_ENC | BLECharacteristic::PROPERTY_WRITE_ENC);
  riferimentoReport(uscita, 1, 0x02);

  // Batteria
  BLEService *batSvc = server->createService(BLEUUID((uint16_t)0x180F));
  batteria = batSvc->createCharacteristic((uint16_t)0x2A19, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
  uint8_t liv = BLE_BATTERIA_SIMULATA;
  batteria->setValue(&liv, 1);

  info->start();
  hidSvc->start();
  batSvc->start();
  server->start();

  BLEAdvertising *pub = BLEDevice::getAdvertising();
  pub->setAppearance(0x03C1);  // HID Keyboard
  pub->addServiceUUID(hidSvc->getUUID());
  pub->setScanResponse(true);
  BLEDevice::startAdvertising();
  int bond = 0;
  ble_store_util_count(BLE_STORE_OBJ_TYPE_PEER_SEC, &bond);
  Serial.printf("BLE INDIRIZZO %s pubblico, bond salvati %d\n", BLEDevice::getAddress().toString().c_str(), bond);
  Serial.printf("BLE PUBBLICITA %s\n", BLE_NOME);
}

int bleAggiorna() {
  int h = subHandle;
  if (h >= 0) {
    subHandle = -1;
    Serial.printf("BLE SOTTOSCRIZIONE handle=%d notifiche=%d motivo=%d (input_report=%u)\n", h, subNotify, subReason, ingresso ? ingresso->getHandle() : 0);
  }
  int n = eventoNotifiche;
  if (n >= 0) {
    eventoNotifiche = -1;
    Serial.printf("BLE NOTIFICHE %s %d\n", (n & 1) ? "on" : "off", n);
  }
  int s = eventoSicurezza;
  if (s) {
    eventoSicurezza = 0;
    if (s == 1) Serial.printf("BLE SICUREZZA ok cifrato=%d bond=%d\n", sicurezzaCifrato, sicurezzaBond);
    else Serial.printf("BLE SICUREZZA errore %d\n", sicurezzaStato);
  }
  int e = eventoConn;
  if (e == 0) return 0;
  eventoConn = 0;
  if (e > 0) {
    Serial.println("BLE CONNESSO");
  } else {
    Serial.println("BLE DISCONNESSO");
    if (!sospesa) Serial.printf("BLE PUBBLICITA %s\n", BLE_NOME);
  }
  return e;
}

bool bleCollegato() { return collegato && !sospesa; }

int bleInviaTasto(uint8_t mod, uint8_t usage) {
  if (!bleCollegato() || !ingresso) return 0;
  uint8_t r[8] = {mod, 0, usage, 0, 0, 0, 0, 0};
  uint8_t zero[8] = {0};
  if (!sottoscritto) {
    // Diagnostica: notifica inviata comunque (direttamente con NimBLE) se il link e' cifrato
    if (!cifrato || connHandle == 0xFFFF) return -1;
    ingresso->setValue(r, sizeof(r));
    int rc1 = ble_gatts_notify_custom(connHandle, ingresso->getHandle(), ble_hs_mbuf_from_flat(r, sizeof(r)));
    ingresso->setValue(zero, sizeof(zero));
    int rc2 = ble_gatts_notify_custom(connHandle, ingresso->getHandle(), ble_hs_mbuf_from_flat(zero, sizeof(zero)));
    return (rc1 == 0 && rc2 == 0) ? 2 : -2;
  }
  ingresso->setValue(r, sizeof(r));
  ingresso->notify();
  ingresso->setValue(zero, sizeof(zero));
  ingresso->notify();
  return 1;
}

void bleBatteria(uint8_t p) {
  if (!batteria) return;
  batteria->setValue(&p, 1);
  if (collegato) batteria->notify();
}

// BLE e WiFi non convivono: con NimBLE inizializzato la scansione WiFi manda in panic
// l'S3 (Interrupt WDT). Le modalita' rete partono quindi da un riavvio senza BLE.
void bleNonAvviare() {
  sospesa = true;
  Serial.println("BLE SOSPESO modalita_rete (riparte al prossimo riavvio)");
}

bool bleSospesa() { return sospesa || !server; }
