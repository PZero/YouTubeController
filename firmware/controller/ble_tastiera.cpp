#include "ble_tastiera.h"
#include "config.h"
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEHIDDevice.h>
#include <BLESecurity.h>

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
static BLEHIDDevice *hid = nullptr;
static BLECharacteristic *ingresso = nullptr;
static volatile bool collegato = false;
static volatile int eventoConn = 0;  // +1 connesso, -1 disconnesso (dal task BLE)
static bool sospesa = false;

class CallbackServer : public BLEServerCallbacks {
  void onConnect(BLEServer *) override {
    collegato = true;
    eventoConn = 1;
  }
  void onDisconnect(BLEServer *) override {
    collegato = false;
    eventoConn = -1;
  }
};

class CallbackSicurezza : public BLESecurityCallbacks {
  bool onSecurityRequest() override { return true; }
  uint32_t onPassKeyRequest() override { return 0; }
  void onPassKeyNotify(uint32_t) override {}
  bool onConfirmPIN(uint32_t) override { return true; }
#if defined(CONFIG_BLUEDROID_ENABLED)
  void onAuthenticationComplete(esp_ble_auth_cmpl_t) override {}
#elif defined(CONFIG_NIMBLE_ENABLED)
  void onAuthenticationComplete(ble_gap_conn_desc *) override {}
#endif
};

void bleInizia() {
  BLEDevice::init(BLE_NOME);
  // "Just Works" con bonding: nessun PIN, l'iPad si ricollega da solo dopo un riavvio.
  BLESecurity *sicurezza = new BLESecurity();
  sicurezza->setCapability(ESP_IO_CAP_NONE);
  sicurezza->setAuthenticationMode(true, false, true);
  BLEDevice::setSecurityCallbacks(new CallbackSicurezza());

  server = BLEDevice::createServer();
  server->setCallbacks(new CallbackServer());
  server->advertiseOnDisconnect(true);

  hid = new BLEHIDDevice(server);
  hid->manufacturer()->setValue("PZero");
  hid->pnp(0x02, 0x303A, 0x4001, 0x0100);  // origine USB, VID Espressif
  hid->hidInfo(0x00, 0x01);
  hid->reportMap((uint8_t *)REPORT_MAP, sizeof(REPORT_MAP));
  ingresso = hid->inputReport(1);
  hid->outputReport(1);
  hid->setBatteryLevel(BLE_BATTERIA_SIMULATA);
  hid->startServices();

  BLEAdvertising *pub = BLEDevice::getAdvertising();
  pub->setAppearance(0x03C1);  // HID Keyboard
  pub->addServiceUUID(hid->hidService()->getUUID());
  pub->setScanResponse(true);
  BLEDevice::startAdvertising();
  Serial.printf("BLE PUBBLICITA %s\n", BLE_NOME);
}

int bleAggiorna() {
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

bool bleInviaTasto(uint8_t mod, uint8_t usage) {
  if (!bleCollegato() || !ingresso) return false;
  uint8_t r[8] = {mod, 0, usage, 0, 0, 0, 0, 0};
  ingresso->setValue(r, sizeof(r));
  ingresso->notify();
  uint8_t zero[8] = {0};
  ingresso->setValue(zero, sizeof(zero));
  ingresso->notify();
  return true;
}

void bleBatteria(uint8_t p) {
  if (hid) hid->setBatteryLevel(p);
}

void bleSospendi() {
  if (sospesa || !server) return;
  sospesa = true;
  server->advertiseOnDisconnect(false);
  BLEDevice::stopAdvertising();
  for (auto &p : server->getPeerDevices(false)) server->disconnect(p.first);
  Serial.println("BLE SOSPESO (WiFi attivo; si riprende al riavvio)");
}

bool bleSospesa() { return sospesa; }
