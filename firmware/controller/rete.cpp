#include "rete.h"
#include "config.h"
#include "feedback.h"
#include "tasti.h"
#include "ble_tastiera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <DNSServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <Update.h>
#include <HTTPClient.h>
#include <NetworkClientSecure.h>
#include <mbedtls/sha256.h>

static WebServer server(80);
static DNSServer dns;
static Preferences prefs;
static StatoRete stato = R_SPENTA;
static bool serverAvviato = false, dnsAvviato = false;
static unsigned long ultimaAttivita = 0, inizioConnessione = 0;
static unsigned long azioneTra = 0;       // azione differita (per far arrivare la risposta HTTP)
static enum { A_NESSUNA, A_CONNETTI, A_PORTALE, A_RIAVVIO, A_ESCI, A_GITHUB } azione = A_NESSUNA;
static String reti;                        // <option> della scansione
static String nomeAp;
static size_t caricamentoTotale = 0;
static int caricamentoUltimoPct = -1;

static const IPAddress IP_AP(192, 168, 4, 1);

// ---------------- NVS ----------------
static String leggi(const char *chiave) {
  prefs.begin("ytc", true);
  String v = prefs.getString(chiave, "");
  prefs.end();
  return v;
}
static void scrivi(const char *chiave, const String &v) {
  prefs.begin("ytc", false);
  prefs.putString(chiave, v);
  prefs.end();
}
static void cancellaWifi() {
  prefs.begin("ytc", false);
  prefs.remove("ssid");
  prefs.remove("pass");
  prefs.end();
}
static String passwordAp() {
  String p = leggi("ap_pass");
  return p.length() >= 8 ? p : String(AP_PASSWORD_DEFAULT);
}

static void programma(decltype(azione) a, unsigned long ritardo) {
  azione = a;
  azioneTra = millis() + ritardo;
}

// ---------------- Pagine ----------------
static String esc(const String &s) {
  String o;
  for (char c : s) {
    if (c == '&') o += "&amp;";
    else if (c == '<') o += "&lt;";
    else if (c == '>') o += "&gt;";
    else if (c == '"') o += "&quot;";
    else o += c;
  }
  return o;
}

static const char CSS[] PROGMEM = R"(<meta name="viewport" content="width=device-width,initial-scale=1"><style>
:root{--bg:#f6f7f9;--card:#fff;--text:#1d2430;--muted:#6b7380;--line:#dde1e7;--accent:#2563eb;--err:#c62828}
@media(prefers-color-scheme:dark){:root{--bg:#12151b;--card:#1b2029;--text:#e6e9ef;--muted:#8b93a1;--line:#2c333f;--accent:#5b8cff;--err:#ff6b6b}}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.45 system-ui,sans-serif}
main{max-width:520px;margin:0 auto;padding:20px 16px}h1{font-size:20px;margin:0 0 4px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:14px 0}
.m{color:var(--muted);font-size:14px}label{display:block;margin:10px 0 4px;font-size:14px;color:var(--muted)}
input,select,button{font:inherit;width:100%;box-sizing:border-box;padding:10px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--text)}
button{background:var(--accent);border-color:var(--accent);color:#fff;margin-top:12px;cursor:pointer}
button.sec{background:var(--card);color:var(--text);border-color:var(--line)}button.err{background:var(--err);border-color:var(--err)}
a{color:var(--accent)}</style>)";

static void invia(const String &titolo, const String &corpo, int codice = 200) {
  String h = "<!doctype html><html lang=it><head><meta charset=utf-8><title>" + titolo + "</title>";
  h += FPSTR(CSS);
  h += "</head><body><main><h1>" + titolo + "</h1>" + corpo + "</main></body></html>";
  server.send(codice, "text/html; charset=utf-8", h);
}

static void scansiona() {
  int n = WiFi.scanNetworks(false, false);
  reti = "";
  for (int i = 0; i < n; i++) {
    String s = WiFi.SSID(i);
    if (s.length() == 0 || reti.indexOf(">" + esc(s) + " (") >= 0) continue;
    reti += "<option value=\"" + esc(s) + "\">" + esc(s) + " (" + WiFi.RSSI(i) + " dBm)</option>";
  }
  WiFi.scanDelete();
  Serial.printf("PORTALE SCANSIONE %d\n", n < 0 ? 0 : n);
}

static void paginaPrincipale() {
  reteAttivita();
  if (server.hasArg("scan")) scansiona();
  String ssid = leggi("ssid");
  bool sta = WiFi.status() == WL_CONNECTED;
  String c = "<p class=m>Firmware " FW_VERSION " &middot; ";
  c += stato == R_PORTALE ? "rete di configurazione" : "modalit&agrave; aggiornamento";
  c += "</p><div class=card><b>WiFi di casa</b><p class=m>";
  c += ssid.length() ? "Configurato: " + esc(ssid) : String("Non configurato");
  if (sta) c += "<br>Collegato, IP " + WiFi.localIP().toString();
  c += "</p><form method=post action=/salva>";
  if (stato == R_PORTALE) {
    c += "<label>Reti trovate (<a href=/?scan=1>aggiorna</a>)</label><select onchange=\"ssid.value=this.value\"><option value=''>scegli...</option>" + reti + "</select>";
  }
  c += "<label>Nome rete (SSID)</label><input name=ssid id=ssid value=\"" + esc(ssid) + "\" required>";
  c += "<label>Password</label><input name=pass type=password autocomplete=off>";
  c += "<button>Salva e collega</button></form>";
  c += "<form method=post action=/dimentica><button class=err>Dimentica WiFi</button></form></div>";

  c += "<div class=card><b>Aggiornamento</b>";
  if (sta) c += "<form method=post action=/github><button>Cerca aggiornamento su GitHub</button></form>";
  else c += "<p class=m>L'aggiornamento da GitHub richiede il WiFi di casa.</p>";
  c += "<p><a href=/update>Carica un file .bin dal computer</a></p></div>";

  c += "<div class=card><b>Rete di configurazione</b><p class=m>Nome: " + esc(nomeAp) + "</p>";
  c += "<form method=post action=/appass><label>Nuova password (minimo 8 caratteri)</label>";
  c += "<input name=p type=password minlength=8 autocomplete=off><button class=sec>Cambia password</button></form></div>";
  c += "<form method=post action=/esci><button class=sec>Esci (riavvia il controller)</button></form>";
  invia("YouTube Controller", c);
}

static void paginaSalva() {
  reteAttivita();
  String ssid = server.arg("ssid");
  ssid.trim();
  if (ssid.length() == 0 || ssid.length() > 32 || server.arg("pass").length() > 63) {
    invia("Errore", "<p>Nome rete o password non validi.</p><p><a href=/>Indietro</a></p>", 400);
    return;
  }
  scrivi("ssid", ssid);
  scrivi("pass", server.arg("pass"));  // mai nei log
  Serial.printf("WIFI SALVATO %s\n", ssid.c_str());
  invia("Salvato", "<p>Il controller ora chiude questa rete e si collega a <b>" + esc(ssid) +
                       "</b>. Se riesce, la pagina di aggiornamento sar&agrave; su <b>http://" MDNS_NOME ".local/</b> "
                       "(o sull'IP indicato nel monitor seriale). Se non riesce, questa rete si riapre.</p>");
  programma(A_CONNETTI, 1500);
}

static void paginaDimentica() {
  reteAttivita();
  cancellaWifi();
  Serial.println("WIFI AZZERATO pagina");
  invia("WiFi dimenticato", "<p>Credenziali cancellate.</p><p><a href=/>Indietro</a></p>");
  if (stato != R_PORTALE) programma(A_PORTALE, 1500);
}

static void paginaApPass() {
  reteAttivita();
  String p = server.arg("p");
  if (p.length() < 8 || p.length() > 63) {
    invia("Errore", "<p>La password deve avere da 8 a 63 caratteri.</p><p><a href=/>Indietro</a></p>", 400);
    return;
  }
  scrivi("ap_pass", p);
  Serial.println("PORTALE PASSWORD_AP CAMBIATA");
  invia("Password cambiata", "<p>Vale dalla prossima apertura della rete di configurazione.</p><p><a href=/>Indietro</a></p>");
}

static void paginaGithub() {
  reteAttivita();
  invia("Controllo aggiornamenti", "<p>Controllo in corso: guarda l'anello o il monitor seriale. "
                                   "Se c'&egrave; una versione nuova il controller si aggiorna e si riavvia.</p><p><a href=/>Indietro</a></p>");
  programma(A_GITHUB, 500);
}

static void paginaEsci() {
  invia("Uscita", "<p>Il controller si riavvia.</p>");
  programma(A_ESCI, 800);
}

static void paginaUpdate() {
  reteAttivita();
  invia("Carica firmware",
        "<div class=card><p class=m>File <b>.bin</b> compilato per questa scheda (stesse partizioni). "
        "Firmware attuale " FW_VERSION ".</p><form method=post action=/update enctype=multipart/form-data>"
        "<input type=file name=f accept=.bin required><button>Carica e installa</button></form></div><p><a href=/>Indietro</a></p>");
}

static void caricamentoFine() {
  if (Update.hasError()) {
    Serial.printf("OTA ERRORE caricamento %s\n", Update.errorString());
    effetto(E_ERRORE);
    vibra(300);
    invia("Errore", String("<p>Aggiornamento non riuscito: ") + Update.errorString() + "</p><p><a href=/update>Riprova</a></p>", 500);
    return;
  }
  Serial.println("OTA RIUSCITO caricamento, riavvio");
  effetto(E_VERDE);
  vibraSerie(2, 80, 120);
  invia("Aggiornato", "<p>Firmware installato, il controller si riavvia.</p>");
  programma(A_RIAVVIO, 1200);
}

static void caricamentoDati() {
  HTTPUpload &u = server.upload();
  reteAttivita();
  if (u.status == UPLOAD_FILE_START) {
    caricamentoTotale = server.clientContentLength();
    caricamentoUltimoPct = -1;
    Serial.printf("OTA CARICAMENTO_INIZIO %u %s\n", (unsigned)caricamentoTotale, u.filename.c_str());
    if (!Update.begin(UPDATE_SIZE_UNKNOWN)) Serial.printf("OTA ERRORE %s\n", Update.errorString());
    effettoProgresso(0);
  } else if (u.status == UPLOAD_FILE_WRITE) {
    if (Update.isRunning() && Update.write(u.buf, u.currentSize) != u.currentSize) Serial.printf("OTA ERRORE scrittura %s\n", Update.errorString());
    if (caricamentoTotale > 0) {
      int pct = (int)((uint64_t)u.totalSize * 100 / caricamentoTotale);
      if (pct / 5 != caricamentoUltimoPct / 5) {
        caricamentoUltimoPct = pct;
        Serial.printf("OTA CARICAMENTO %d\n", pct);
        effettoProgresso(pct);
        feedbackForza();
      }
    }
  } else if (u.status == UPLOAD_FILE_END) {
    if (Update.end(true)) Serial.printf("OTA CARICATO %u\n", (unsigned)u.totalSize);
    else Serial.printf("OTA ERRORE fine %s\n", Update.errorString());
  } else if (u.status == UPLOAD_FILE_ABORTED) {
    Update.abort();
    Serial.println("OTA ERRORE caricamento interrotto");
  }
}

static void nonTrovata() {
  if (stato == R_PORTALE) {
    // portale captive: qualunque indirizzo porta alla pagina di configurazione
    server.sendHeader("Location", "http://192.168.4.1/", true);
    server.send(302, "text/plain", "");
    return;
  }
  server.send(404, "text/plain", "Non trovato");
}

static void avviaServer() {
  if (serverAvviato) return;
  server.on("/", HTTP_GET, paginaPrincipale);
  server.on("/salva", HTTP_POST, paginaSalva);
  server.on("/dimentica", HTTP_POST, paginaDimentica);
  server.on("/appass", HTTP_POST, paginaApPass);
  server.on("/github", HTTP_POST, paginaGithub);
  server.on("/esci", HTTP_POST, paginaEsci);
  server.on("/update", HTTP_GET, paginaUpdate);
  server.on("/update", HTTP_POST, caricamentoFine, caricamentoDati);
  server.onNotFound(nonTrovata);
  server.begin();
  serverAvviato = true;
}

// ---------------- Stati ----------------
static void apriPortale(const char *motivo) {
  if (dnsAvviato) { dns.stop(); dnsAvviato = false; }
  WiFi.disconnect(true);
  WiFi.mode(WIFI_AP_STA);
  scansiona();
  WiFi.softAPConfig(IP_AP, IP_AP, IPAddress(255, 255, 255, 0));
  if (!WiFi.softAP(nomeAp.c_str(), passwordAp().c_str())) {
    Serial.println("ERRORE PORTALE avvio rete non riuscito");
    effetto(E_ERRORE);
    return;
  }
  dns.setErrorReplyCode(DNSReplyCode::NoError);
  dnsAvviato = dns.start(53, "*", IP_AP);
  avviaServer();
  stato = R_PORTALE;
  reteAttivita();
  sfondo(E_PORTALE);
  Serial.printf("PORTALE APERTO http://192.168.4.1/ %s %s\n", motivo, nomeAp.c_str());
}

static void connetti() {
  String ssid = leggi("ssid");
  if (ssid.length() == 0) {
    Serial.println("WIFI NON_CONFIGURATO");
    apriPortale("non_configurato");
    return;
  }
  if (dnsAvviato) { dns.stop(); dnsAvviato = false; }
  if (stato == R_PORTALE) {
    WiFi.softAPdisconnect(true);
    Serial.println("PORTALE CHIUSO connessione");
  }
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid.c_str(), leggi("pass").c_str());
  stato = R_CONNESSIONE;
  inizioConnessione = millis();
  reteAttivita();
  sfondo(E_OTA_CONN);
  Serial.printf("WIFI CONNESSIONE %s\n", ssid.c_str());
}

// ---------------- GitHub Release ----------------
static String campoJson(const String &j, const char *chiave) {
  int i = j.indexOf(String("\"") + chiave + "\"");
  if (i < 0) return "";
  i = j.indexOf(':', i);
  if (i < 0) return "";
  i++;
  while (i < (int)j.length() && (j[i] == ' ' || j[i] == '"')) i++;
  int f = i;
  while (f < (int)j.length() && j[f] != '"' && j[f] != ',' && j[f] != '}' && j[f] != ' ') f++;
  return j.substring(i, f);
}

static long numeroVersione(const String &v) {
  long a = 0, b = 0, c = 0;
  sscanf(v.c_str() + (v.startsWith("v") ? 1 : 0), "%ld.%ld.%ld", &a, &b, &c);
  return a * 1000000L + b * 1000L + c;
}

static void erroreOta(const char *msg) {
  Serial.printf("OTA ERRORE %s\n", msg);
  effetto(E_ERRORE);
  vibra(300);
}

static void controllaGithub() {
  Serial.println("OTA CONTROLLO " OTA_URL_JSON);
  sfondo(E_OTA_CONN);
  feedbackForza();
  NetworkClientSecure cli;
  cli.useBuiltinCACertBundle();
  HTTPClient h;
  h.setFollowRedirects(HTTPC_FORCE_FOLLOW_REDIRECTS);
  h.setUserAgent("YTController/" FW_VERSION);
  h.setConnectTimeout(15000);
  h.setTimeout(15000);
  if (!h.begin(cli, OTA_URL_JSON)) { erroreOta("url_json"); sfondo(E_OTA_PRONTO); return; }
  int cod = h.GET();
  if (cod != 200) {
    char m[48];
    snprintf(m, sizeof(m), "json_http %d%s", cod, cod == 404 ? " nessuna_release" : "");
    h.end();
    erroreOta(m);
    sfondo(E_OTA_PRONTO);
    return;
  }
  String j = h.getString();
  h.end();
  String vers = campoJson(j, "version");
  long dim = campoJson(j, "size").toInt();
  String sha = campoJson(j, "sha256");
  sha.toLowerCase();
  Serial.printf("OTA VERSIONE %s %s\n", vers.c_str(), FW_VERSION);
  if (vers.length() == 0 || dim <= 0 || sha.length() != 64) { erroreOta("json_non_valido"); sfondo(E_OTA_PRONTO); return; }
  if (numeroVersione(vers) <= numeroVersione(FW_VERSION)) {
    Serial.println("OTA NESSUN_AGGIORNAMENTO");
    vibraSerie(1, 60, 0);
    sfondo(E_OTA_PRONTO);
    return;
  }

  // Scaricamento in streaming nello slot libero, con verifica di dimensione e SHA-256
  if (!h.begin(cli, OTA_URL_BIN)) { erroreOta("url_bin"); sfondo(E_OTA_PRONTO); return; }
  cod = h.GET();
  if (cod != 200) { h.end(); erroreOta("bin_http"); sfondo(E_OTA_PRONTO); return; }
  int len = h.getSize();
  if (len > 0 && len != dim) { h.end(); erroreOta("dimensione_diversa"); sfondo(E_OTA_PRONTO); return; }
  if (!Update.begin(dim)) { h.end(); erroreOta(Update.errorString()); sfondo(E_OTA_PRONTO); return; }
  NetworkClient *s = h.getStreamPtr();
  mbedtls_sha256_context ctx;
  mbedtls_sha256_init(&ctx);
  mbedtls_sha256_starts(&ctx, 0);
  static uint8_t buf[4096];
  long letti = 0;
  int ultimoPct = -1;
  unsigned long t0 = millis(), ultimoDato = millis();
  effettoProgresso(0);
  while (letti < dim) {
    if (millis() - ultimoDato > 15000 || millis() - t0 > 180000) break;
    size_t disp = s->available();
    if (!disp) {
      if (!s->connected()) break;
      delay(2);
      continue;
    }
    int n = s->read(buf, min(disp, sizeof(buf)));
    if (n <= 0) continue;
    ultimoDato = millis();
    mbedtls_sha256_update(&ctx, buf, n);
    if (Update.write(buf, n) != (size_t)n) break;
    letti += n;
    int pct = letti * 100 / dim;
    if (pct / 5 != ultimoPct / 5) {
      ultimoPct = pct;
      Serial.printf("OTA SCARICO %d\n", pct);
      effettoProgresso(pct);
      feedbackForza();
    }
  }
  h.end();
  uint8_t dig[32];
  mbedtls_sha256_finish(&ctx, dig);
  mbedtls_sha256_free(&ctx);
  char hex[65];
  for (int i = 0; i < 32; i++) sprintf(hex + 2 * i, "%02x", dig[i]);
  if (letti != dim) { Update.abort(); erroreOta("scaricamento_incompleto"); sfondo(E_OTA_PRONTO); return; }
  if (sha != hex) { Update.abort(); erroreOta("sha256_diverso"); sfondo(E_OTA_PRONTO); return; }
  if (!Update.end(true)) { erroreOta(Update.errorString()); sfondo(E_OTA_PRONTO); return; }
  Serial.printf("OTA RIUSCITO %s, riavvio\n", vers.c_str());
  effetto(E_VERDE);
  vibraSerie(2, 80, 120);
  programma(A_RIAVVIO, 1200);
}

// ---------------- API ----------------
void reteInizia() {
  uint64_t mac = ESP.getEfuseMac();  // byte 0 = primo byte del MAC
  char n[24];
  snprintf(n, sizeof(n), "YTController-%02X%02X", (unsigned)((mac >> 32) & 0xFF), (unsigned)((mac >> 40) & 0xFF));
  nomeAp = n;
  String ssid = leggi("ssid");
  Serial.printf("WIFI SPENTO %s\n", ssid.length() ? "configurato" : "non_configurato");
}

StatoRete reteStato() { return stato; }
bool reteAttiva() { return stato != R_SPENTA; }
void reteAttivita() { ultimaAttivita = millis(); }

static bool preparaModo() {
  if (CONTROLLO_BATTERIA) {
    float v = analogReadMilliVolts(PIN_BATTERIA) * 2 / 1000.0f;
    if (v < VBAT_MIN_OTA) {
      Serial.printf("OTA ERRORE batteria %.2f V\n", v);
      effetto(E_ERRORE);
      vibra(300);
      return false;
    }
  }
  return true;
}

void reteEntraOta() {
  if (reteAttiva() || !preparaModo()) return;
  Serial.println("OTA INGRESSO");
  tastoInvia(T_F13);
  bleSospendi();
  sfondo(E_VIOLA);
  effetto(E_VIOLA);
  vibra(300);
  connetti();
}

void reteAzzeraWifi() {
  cancellaWifi();
  Serial.println("WIFI AZZERATO gesto");
  if (!bleSospesa()) tastoInvia(T_F15);
  bleSospendi();
  effetto(E_SVUOTA_ROSSO);
  vibraSerie(3, 60, 100);
  if (stato != R_PORTALE) apriPortale("azzeramento");
}

void reteEsci(const char *motivo) {
  Serial.printf("OTA USCITA %s\n", motivo);
  if (stato == R_PORTALE) Serial.println("PORTALE CHIUSO uscita");
  effetto(E_USCITA);
  vibra(50);
  unsigned long t = millis();
  while (millis() - t < 650) { feedbackAggiorna(millis()); delay(5); }
  Serial.println("INFO riavvio");
  Serial.flush();
  ESP.restart();
}

void reteAggiorna(unsigned long adesso) {
  if (stato == R_SPENTA) return;
  if (dnsAvviato) dns.processNextRequest();
  if (serverAvviato) server.handleClient();

  if (stato == R_CONNESSIONE) {
    if (WiFi.status() == WL_CONNECTED) {
      stato = R_OTA;
      Serial.printf("WIFI CONNESSO %s %d\n", WiFi.localIP().toString().c_str(), WiFi.RSSI());
      if (MDNS.begin(MDNS_NOME)) MDNS.addService("http", "tcp", 80);
      avviaServer();
      sfondo(E_OTA_PRONTO);
      Serial.printf("OTA PRONTO http://%s/ http://" MDNS_NOME ".local/\n", WiFi.localIP().toString().c_str());
      reteAttivita();
      programma(A_GITHUB, 300);  // controllo automatico all'ingresso
    } else if (adesso - inizioConnessione > WIFI_TIMEOUT) {
      Serial.println("WIFI ERRORE timeout");
      apriPortale("wifi_fallito");
    }
  }

  if (azione != A_NESSUNA && (long)(adesso - azioneTra) >= 0) {
    auto a = azione;
    azione = A_NESSUNA;
    switch (a) {
      case A_CONNETTI: connetti(); break;
      case A_PORTALE: apriPortale("wifi_dimenticato"); break;
      case A_GITHUB: if (stato == R_OTA) controllaGithub(); break;
      case A_RIAVVIO: Serial.println("INFO riavvio"); Serial.flush(); ESP.restart(); break;
      case A_ESCI: reteEsci("pagina"); break;
      default: break;
    }
  }

  if (Update.isRunning()) reteAttivita();
  if (adesso - ultimaAttivita > MODO_TIMEOUT) reteEsci("timeout");
}
