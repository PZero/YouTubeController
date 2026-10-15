#include "sospensione.h"
#include "config.h"
#include "feedback.h"
#include "ble_tastiera.h"
#include <esp_sleep.h>
#include <driver/rtc_io.h>
#include <driver/gpio.h>

static const gpio_num_t PIN_HOLD[] = {(gpio_num_t)PIN_ANELLO, (gpio_num_t)PIN_VIB, (gpio_num_t)PIN_ANELLO_ALIM};

static void liberaPin() {
  for (gpio_num_t p : PIN_HOLD) gpio_hold_dis(p);
  gpio_deep_sleep_hold_dis();
}

static void dormi() {
  // dato anello e motore bassi, mantenuti durante il deep sleep
  for (gpio_num_t p : PIN_HOLD) {
    pinMode(p, OUTPUT);
    digitalWrite(p, LOW);
    gpio_hold_en(p);
  }
  gpio_deep_sleep_hold_en();
  // risveglio: switch dell'encoder a GND, pull-up RTC attivo durante il sonno
  esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_ON);
  rtc_gpio_pullup_en((gpio_num_t)PIN_PULSANTE);
  rtc_gpio_pulldown_dis((gpio_num_t)PIN_PULSANTE);
  esp_sleep_enable_ext1_wakeup(1ULL << PIN_PULSANTE, ESP_EXT1_WAKEUP_ANY_LOW);
  Serial.flush();
  delay(30);
  esp_deep_sleep_start();
}

bool sospensioneRisveglio() {
  bool daPulsante = esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_EXT1;
  if (!daPulsante) {
    liberaPin();
    return false;
  }
  rtc_gpio_deinit((gpio_num_t)PIN_PULSANTE);
  pinMode(PIN_PULSANTE, INPUT_PULLUP);
  unsigned long rilasciatoDa = 0;
  while (millis() < RISVEGLIO_CONFERMA) {
    if (digitalRead(PIN_PULSANTE) == HIGH) {
      if (!rilasciatoDa) rilasciatoDa = millis();
      else if (millis() - rilasciatoDa > 50) {
        Serial.println("SOSPENSIONE RISVEGLIO_ANNULLATO");
        dormi();  // pin ancora mantenuti: anello spento, motore fermo, nessun BLE
      }
    } else {
      rilasciatoDa = 0;
    }
    delay(5);
  }
  liberaPin();
  Serial.println("SOSPENSIONE RISVEGLIO");
  return true;
}

void sospendiOra(const char *motivo) {
  Serial.printf("SOSPENSIONE ORA %s\n", motivo);
  feedbackSpegniTutto();
  vibra(300);
  unsigned long t = millis();
  while (millis() - t < 330) {
    feedbackAggiorna(millis());
    delay(5);
  }
  feedbackSpegniTutto();
  bleSpegni();
  if (digitalRead(PIN_PULSANTE) == LOW) {
    Serial.println("SOSPENSIONE ATTESA_RILASCIO");
    while (digitalRead(PIN_PULSANTE) == LOW) delay(10);
    delay(100);  // rimbalzi: un livello basso farebbe ripartire subito il chip
  }
  ledcDetach(PIN_VIB);
  dormi();
}
