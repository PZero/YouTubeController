# Dimensioni condivise

Unica fonte di verità per le misure fisiche. La aggiorna `elettronica-firmware` quando sceglie un componente; la legge `design-3d` per il modello. Misure in millimetri.

| Elemento | Larghezza | Profondità | Altezza | Note (fori, connettori, albero) |
|----------|-----------|------------|---------|---------------------------------|
| Scheda (ESP32-S3 SuperMini) | 18 | 22,5 (fonti: 22,52 / 23,5 / 24) | PCB ~1,0 (stima) + componenti ~3,2 sopra (USB-C, stima) = ~4,5 totale senza header; con header maschi +8,5 sotto | USB-C sul lato corto da 18 mm, centrato in larghezza, sporgenza ~0,5-1 mm (stima); antenna ceramica sul lato corto opposto (tenere ≥5 mm da viti/metallo/encoder, niente piano metallico sopra); pulsanti BOOT e RST sulla faccia superiore (accessibili per il reset/flash); LED RGB sopra; sul retro pad GPIO14-48 ed eventuali pad batteria B+/B- (lasciare spazio per i fili). Pin passo 2,54 mm. **Misure da verificare col calibro all'arrivo** |
| Encoder | da definire | | | |
| Pulsante | da definire | | | |
| Batteria | da definire | | | |
