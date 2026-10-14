# Test dei comandi (prototipo su breadboard)

Sketch di prova per encoder EC11E (20 impulsi / 20 scatti), pulsante integrato, anello WS2812B 16 LED e modulo vibrazione, più una pagina web che mostra gli eventi in tempo reale.

Collegamenti: vedi l'intestazione di `test_comandi.ino` (A = GPIO4, B = GPIO5, pulsante = GPIO7, anello DI = GPIO2, vibrazione IN = GPIO6).

Compilazione e caricamento (batteria scollegata):

```
arduino-cli compile --upload -p COM3 --fqbn "esp32:esp32:esp32s3:CDCOnBoot=cdc" firmware/test_comandi
```

Librerie: core `esp32:esp32` 3.x, `Adafruit NeoPixel`.

Monitor: aprire `monitor.html` in Chrome o Edge (Web Serial), "Collega ESP32". Chiudere la pagina prima di ricaricare il firmware: tiene occupata la porta.

Risultati della prova (2026-10-14):
- Encoder: 20 scatti/giro, 4 transizioni per scatto, riposo su A=B=1; orario = avanti; nessuna transizione non valida. Lettura in interrupt (con polling e anello aggiornato a ogni scatto si bloccava girando veloce).
- Anello: LED numerati in senso antiorario visti dall'alto (indice invertito nel firmware).
- Vibrazione: con impulsi da 12 ms al 60% il motore non parte; servono impulsi a piena potenza da 30-60 ms. Sensazione debole con il modulo libero: va fissato rigidamente alla scocca.
