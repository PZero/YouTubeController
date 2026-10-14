// ======================================================================
//  YOUTUBE CONTROL  -  case stampabile in 3D (OpenSCAD)
// ======================================================================
//  PEZZI:
//   1  body      scocca 105x70 (3:2), piano superiore inclinato, spigoli arrotondati, finestre/condotti di
//                raffreddamento, foro manopola, sede RIGIDA del modulo vibrazione sotto la faccia superiore,
//                torrette viti, presa USB-C di ricarica sul retro
//   2  lid       fondo, entra nella scocca e si avvita (4x M3); interfaccia FISSA per il portaschede
//                (4 fori svasati + fori per spillo RST/BOOT)
//   3  sled      portaschede intercambiabile (file portaschede.scad): ESP32-S3 SuperMini capovolta,
//                modulo TP4056, portabatteria 18650 stampato. Si avvita al fondo dal basso (4x M3)
//   4  panel x2  pannelli laterali a feritoie, si incastrano a scatto
//   5  knob      manopola zigrinata (stile ottone), sede a pressione per albero zigrinato 18 denti
//   6  collar    anello decorativo attorno alla manopola (solo se led_ring = false)
//   6b diffuser  corona traslucida sopra l'anello LED (filamento bianco; inserto a scatto o multi-materiale)
//   8  test_ring anelli di prova della sede zigrinata (3 giochi diversi), da stampare per primi
//
//  COMPONENTI PREVISTI (quote in dimensioni.md)
//   - encoder EC11E (bussola M7x0.75, albero 6 mm zigrinato 18 denti, 20 mm dal piano di appoggio)
//   - (pulsante PBS-110 ELIMINATO il 2026-10-14: play/pausa e gesti col pulsante integrato dell'encoder)
//   - ESP32-S3 SuperMini, modulo TP4056 USB-C, cella 18650 + contatti a molla/piastrina
//   - 8x viti M3x8 svasate autofilettanti (4 fondo->scocca, 4 fondo->portaschede)
//   - 4x viti M2x5 autofilettanti (TP4056)
//   - anello LED WS2812B 16 LED (sotto la faccia superiore, a scatto); modulo vibrazione (sotto la faccia
//     superiore, davanti all'anello, a incastro sulla scocca); schedina millefori (sul portaschede)
//
//  mode  = "print"     -> piatti di stampa (plate = 1/2/3, 0 = tutti affiancati, solo anteprima)
//          "assembly"  -> tutto montato (controllo incastri)
//          "exploded"  -> vista esplosa
//  part  = "all" oppure un singolo pezzo (per esportare l'STL separato; ignora "plate")
//  show_electronics: modelli semplificati dei componenti, SOLO in assembly/exploded (mai nei piatti)
// ======================================================================

mode          = "print";     // "print" | "assembly" | "exploded"
plate         = 1;           // 1 = scocca | 2 = fondo + portaschede | 3 = manopola + 2 pannelli | 4 = diffusore | 5 = prova tolleranze | 0 = tutti
part          = "all";       // "all" | "body" | "lid" | "sled" | "panel" | "knob" | "collar" | "diffuser" | "test_ring" | "test_tile"
section_view  = false;       // sezione (solo assembly/exploded)
cut_x         = 0;           // piano di sezione (si toglie il lato X > cut_x)
section_shell = false;       // true: la sezione taglia solo scocca e pannelli (interno visibile)
show_electronics = true;     // componenti (solo assembly/exploded)
engrave_text  = false;       // scritte incise sulla faccia superiore
fnt           = "Liberation Sans:style=Bold";

$fn = 48;

// colori di anteprima (= filamenti proposti per i piatti)
c_body = "#1c1c1e";          // piatti 1-2: scocca, fondo, portaschede (PLA NERO)
c_base = "#1c1c1e";
c_acc  = "#b87333";          // piatto 3: manopola + pannelli (PLA RAME)

// piatto di stampa (Bambu Lab A1 mini)
bed      = 180;
bed_marg = 5;

// ----------------------------------------------------------------------
//  PARAMETRI SCOCCA
// ----------------------------------------------------------------------
BW   = 70;      // larghezza (asse X)   - rapporto 3:2 con la lunghezza
BL   = 105;     // lunghezza/profondita' (asse Y, +Y = retro)
tilt = 10;      // inclinazione del piano superiore (alto dietro, basso davanti)
z0   = 43;      // quota del piano superiore a Y=0
Rp   = 12;      // raggio spigoli verticali
Rt   = 7;       // raggio raccordo bordo superiore (misurato sul piano inclinato)
wall = 3.0;     // spessore pareti e piano superiore (perpendicolare al piano)

// fondo
lid_t   = 3.0;
lid_tol = 0.25;       // gioco del fondo nella scocca
post_off = 5.2;       // distanza torretta dal centro dello spigolo interno
post_r   = 4.2;
pilot_d  = 2.6;       // foro pilota M3 autofilettante
pilot_depth = 12;
csk_d1 = 6.4;  csk_d2 = 3.4;  csk_h = 1.7;   // svasatura viti M3 a testa piana

// ----------------------------------------------------------------------
//  INTERFACCIA FONDO <-> PORTASCHEDE (fissa: vedi dimensioni.md)
// ----------------------------------------------------------------------
sled_t    = 2.8;                                     // spessore piastra portaschede (sopra il fondo)
sled_scr  = [[-27,-35], [27,-35], [-12,43], [12,43]]; // 4 viti M3 dal basso (centri, coordinate X,Y)
rst_xy    = [-16.55, -9.4];                          // foro spillo tasto RST della SuperMini
boot_xy   = [ -7.55, -9.4];                          // foro spillo tasto BOOT (facoltativo)
boot_hole = true;
pin_d     = 1.8;                                     // foro spillo (graffetta ~1 mm)
pin_cone  = 4.0;                                     // imbocco svasato dal basso

// ----------------------------------------------------------------------
//  PANNELLI LATERALI (raffreddamento) - sagoma a trapezio arrotondato:
//  bordo inferiore orizzontale, bordo superiore parallelo al piano inclinato
// ----------------------------------------------------------------------
pb  = 6;              // quota (Z) del bordo inferiore del pannello
pc_y = 4;             // posizione del centro del pannello lungo Y
PL  = 64;             // lunghezza del pannello
p_top_drop = 9.5;     // distanza verticale tra piano superiore e bordo alto del pannello
p_r = 8;              // raggio angoli della placca
tp  = 1.4;            // spessore placca = profondita' tasca
pocket_c = 0.25;      // gioco placca/tasca
win_inset = 3.0;      // bordo pieno tra placca e finestra passante
duct_w   = 3.0;       // spessore del condotto interno
duct_len = 9.0;       // sporgenza interna del condotto (serve per i denti a scatto)
n_slots  = 6;  slot_pitch = 3.4;  slot_w = 1.8;  slot_margin = 3;   // feritoie parallele alla pendenza
// denti a scatto (uno sul lato anteriore e uno su quello posteriore della finestra)
arm_w = 8;  arm_t = 1.2;  arm_gap = 0.3;
barb_h = 0.9;  barb_ramp = 1.6;  catch_gap = 0.15;

// ----------------------------------------------------------------------
//  MANOPOLA  (encoder EC11E, albero zigrinato)
// ----------------------------------------------------------------------
K          = [0, 14];   // centro manopola (coordinate sul piano inclinato: x, s)
knob_d     = 32;
flutes     = 60;        // zigrinatura esterna
knob_gap   = 1.8;       // distanza base manopola dalla faccia superiore
enc_hole   = 7.3;       // foro bussola encoder M7
enc_bush   = 7;         // lunghezza bussola filettata (da misurare)
enc_shaft_tot = 20;     // albero dal piano di appoggio (da misurare: 20 o 15)
enc_shaft  = enc_shaft_tot - enc_bush;           // albero sopra la bussola
// sede zigrinata a pressione (18 denti); provare prima con test_ring
knurl_n    = 18;        // numero denti
knurl_do   = 6.0;       // diametro esterno zigrinatura (punte)
knurl_di   = 5.3;       // diametro di fondo
knurl_fit  = 0.10;      // gioco radiale della sede (0.05-0.15; il taglio dell'albero recupera)
knurl_len  = 7;         // lunghezza zigrinatura dalla punta (da misurare)
knurl_test = [0.05, 0.10, 0.15];   // giochi provati dal test_ring
shaft_clear = 6.3;      // tratto liscio dell'albero
bush_clear  = 7.8;      // passaggio bussola M7 dentro la manopola
// spinta assiale (pulsante integrato EC11E, ~6 N, corsa 0.5 +-0.3): la manopola poggia sulla punta dell'albero
// (fondo del foro = punta, nessun gioco) e dado + rondella non devono toccare la manopola a fine corsa
enc_nut_t = 2.0;  enc_washer_t = 0.5;   // dado M7 e rondella (da misurare)
enc_travel = 0.8;                       // corsa massima del pulsante (0.5 +0.3)
bore_slack = 0.0;                       // 0 = il fondo del foro tocca la punta dell'albero
nut_recess_d = 13;
nut_recess_h = enc_nut_t + enc_washer_t - knob_gap + enc_travel + 0.5;   // = 2.0: 0.5 di margine a fine corsa
enc_end    = (enc_bush - wall) + enc_shaft;      // fine albero sopra la faccia superiore
bore_depth = enc_end - knob_gap + bore_slack;
knob_h     = bore_depth + 3.0;

// anello decorativo (collar): usato solo se led_ring = false (al suo posto c'e' il diffusore luminoso)
ring_ri = 17.3;  ring_ro = 20.5;  ring_h = 1.4;
pin_r = 18.9;  pin_d_c = 2.2;  pin_len = 2.0;
pin_hole_d = 2.5;  pin_hole_depth = 2.2;

// anelli di prova
tr_d = 12;  tr_h = knurl_len + 2;  tr_pitch = 15;

// ----------------------------------------------------------------------
//  MODULO VIBRAZIONE SULLA FACCIA SUPERIORE (sede rigida, 2026-10-14)
//  Dal test su breadboard la vibrazione si sente poco se il modulo e' libero: ora il PCB (21 x 23) sta
//  con il retro piatto CONTRO la faccia interna della scocca, davanti all'anello LED (zona liberata dal
//  pulsante PBS-110), tenuto da 2 guide con nervature di pinzatura + 2 ganci a scatto sul piano.
//  Motore e componenti verso l'interno (max 5 sotto la faccia); lato dei pin (21) verso l'encoder,
//  con una tacca per i 3 fili. Si infila dal davanti (scivola lungo la pendenza) a scocca capovolta.
//  Quote nel sistema del piano superiore (z=0 faccia esterna, z=-wall faccia interna, x, s).
// ----------------------------------------------------------------------
vt_w = 21.0;  vt_h = 23.0;  vt_t = 5.0;   // modulo: lato pin (x), altezza (s), spessore max PCB + motore (dimensioni.md, calibro utente, A)
vt_on     = true;
vt_back   = -11.0;     // s della faccia del muretto di battuta (lato encoder); anello + ganci a s > -9.7
vt_pcb_t  = 1.6;       // spessore PCB del modulo: DA MISURARE (se piu' sottile: goccia di colla/biadesivo sottile)
vt_gc     = 0.2;       // gioco PCB / pareti (x) e battuta (s)
vt_gz     = 0.2;       // gioco verticale PCB / labbri (prima delle nervature)
vt_pinch  = 0.15;      // interferenza delle nervature di pinzatura (il PCB e' premuto contro la faccia, PLA)
vt_lip_t  = 1.0;       // spessore dei labbri
vt_lip_e  = 1.0;       // quanto il labbro copre il bordo del PCB (componenti a >1.0 dal bordo: da verificare)
vt_wall   = 1.2;       // spessore pareti laterali e battuta
vt_tab_l  = 6.0;       // lunghezza di ogni labbro (2 per lato: uno davanti, uno dietro)
vt_notch_w = 8.0;      // tacca per i fili nella battuta
// ganci a scatto sul piano (flettono in x): 0.8 x L, dente che tiene il bordo anteriore del PCB
vt_arm_t  = 0.8;  vt_arm_l = 8.0;  vt_barb = 0.6;  vt_barb_l = 1.5;  vt_arm_gap = 0.3;
vt_root   = 1.5;       // blocco di radice del gancio

vt_xi  = vt_w/2 + vt_gc;                 // faccia interna delle pareti (|x|)
vt_sb  = vt_back - vt_wall - vt_gc;       // bordo lato pin del PCB
vt_sf  = vt_sb - vt_h;                   // bordo anteriore del PCB
vt_z1  = -wall;                           // faccia interna della scocca
vt_zp  = vt_z1 - vt_pcb_t;                // faccia inferiore del PCB (a contatto con la faccia)
vt_zl  = vt_zp - vt_gz;                   // faccia superiore dei labbri
vt_zb  = vt_zl - vt_lip_t;                // fondo di pareti e labbri

// ----------------------------------------------------------------------
//  ANELLO LED WS2812B 16 LED + DIFFUSORE (quote: dimensioni.md)
//  Eccezione alla regola modulare: l'anello sta sotto la faccia superiore della scocca,
//  coassiale all'encoder; i fili scendono al portaschede con un connettore JST-PH staccabile.
//  Quote nel sistema del piano superiore (z=0 faccia superiore, z<0 verso l'interno), centro = K.
// ----------------------------------------------------------------------
led_ring   = true;          // false = torna l'anello decorativo (collar) senza luce
diff_mode  = "insert";      // "insert" = diffusore separato a scatto (qualsiasi stampante)
                            // "mmu"    = diffusore stampato insieme alla scocca con AMS lite (cambio filamento)
lr_do   = 45.0;             // diametro esterno PCB (A, calibro utente)
lr_di   = 33.0;             // diametro interno PCB (A)
lr_t    = 3.0;              // spessore totale PCB + LED (A)
lr_pcb_t = 1.6;             // spessore del solo PCB: DA MISURARE (serve solo alle battute superiori)
lr_n    = 16;               // LED 5050
lr_led  = 5.0;              // lato LED 5050 (B, package standard)
lr_led_r = 19.5;            // raggio dei LED (B: raggio medio, da foto)
lr_pad_r = 19.5;  lr_pad_arc = 60;  lr_solder = 1.0;   // piazzole sul retro: raggio, arco, sporgenza saldature (B)
lr_pad_ang = 30;            // direzione del centro dell'arco piazzole (piano superiore: 0 = +X, 90 = verso il retro)
                            // -> verso destra-retro, sopra la cella: i fili scendono a lato della schedina millefori
                            //    senza passare sopra la sua testata JST
lr_air  = 1.0;              // aria tra la cima dei LED e la faccia interna (distanza LED-diffusore = lr_air + wall - diff_t)
lr_c    = 0.25;             // gioco radiale PCB / ganci
// ganci a scatto (4) e battute (4), alternati, fuori dall'arco delle piazzole
lr_clips = 4;  lr_clip_a0 = lr_pad_ang + 45;
lr_clip_w = 3.0;  lr_clip_t = 0.8;       // larghezza e spessore del braccio flessibile (PLA: 2 perimetri)
lr_barb = 0.3;                           // sovrapposizione del dente sotto il PCB
lr_clip_root = 2.0;                      // il braccio nasce in una tasca profonda fino a 2 dalla faccia superiore:
                                         // lunghezza libera ~5.1 -> deformazione 1.5*t*barb/L^2 ~ 1.4 % (PLA <= 1.5 %)
lr_pocket_c = 0.5;                       // gioco della tasca verso l'esterno (spazio per la flessione)
lr_barb_c = 0.1;  lr_barb_ramp = 1.5;    // gioco verticale del dente, altezza rampa
lr_stop = 0.4;  lr_stop_w = 2.5;         // battuta superiore: sovrapposizione sul bordo esterno del PCB
// diffusore (corona traslucida nella faccia superiore)
diff_ri  = knob_d/2 + 0.6;  // raggio interno (appena fuori dalla manopola)
diff_ro  = 22.4;            // raggio esterno (LED fino a ~22)
diff_t   = 1.0;             // spessore del diffusore "insert" (0.8-1.2; resta wall-diff_t = 2 di ponti)
diff_c   = 0.05;            // gioco radiale per lato dell'inserto (0 = pressione)
diff_snap = 0.15;           // sottosquadro sul bordo esterno: l'inserto entra a scatto dall'alto
diff_brg_n = 4;  diff_brg_w = 3.0;   // ponti che reggono il disco centrale con l'encoder (solo "insert"), allineati ai ganci; 3.0 per la spinta del pulsante (2026-10-14)
c_diff = "#eef0ee";         // colore anteprima (PLA bianco)

// presa cavo (USB-C del TP4056) sul retro.
// usb_x spostato da +14 a -12: lato opposto al portabatteria e 1.8 mm di distanza dalla torretta
usb_x = -12;  usb_z = 14;  usb_w = 13;  usb_h = 7;  usb_r = 3;

// posizioni torrette fondo
px = BW/2 - Rp + post_off*cos(45);
py = BL/2 - Rp + post_off*sin(45);

include <portaschede.scad>
include <componenti.scad>

// ======================================================================
//  UTILITA'
// ======================================================================
module rr2d(w, h, r) {
    hull() for (sx=[-1,1], sy=[-1,1])
        translate([sx*(w/2-r), sy*(h/2-r)]) circle(r=r);
}

// quota del piano superiore alla posizione Y
function zpl(y) = z0 + tan(tilt)*y;

// sistema locale del piano superiore inclinato: origine sul piano a Y=0,
// x = larghezza, y = lungo la pendenza, z = normale al piano
module top_frame() translate([0,0,z0]) rotate([tilt,0,0]) children();

// profilo zigrinato a stella (sede albero encoder), gioco radiale "fit"
module knurl2d(fit) {
    polygon([for (i=[0:2*knurl_n-1])
        let(r = (i%2==0 ? knurl_do/2 : knurl_di/2) + fit, a = i*180/knurl_n) [r*cos(a), r*sin(a)]]);
}

// scocca con pareti verticali e piano superiore inclinato.
// cylr = raggio degli spigoli, minor = raggio del raccordo superiore.
module rbox_t(cylr, minor, zb) {
    major = Rp - Rt;
    hull() for (sx=[-1,1], sy=[-1,1]) {
        cx = sx*(BW/2-Rp);  cy = sy*(BL/2-Rp);
        Ty = cy - Rt*sin(tilt);
        Cz = zpl(Ty) - Rt*cos(tilt);
        translate([cx, cy, zb]) cylinder(r=cylr, h=Cz - cylr*sin(tilt) - zb - 0.01);
        translate([cx, cy, Cz]) rotate([tilt,0,0]) rotate_extrude()
            intersection() {
                translate([major,0]) circle(r=minor);
                square([major+minor, minor]);
            }
    }
}

// ---- sagoma del pannello (coordinate locali: u lungo Y, v = quota sopra il bordo inferiore)
function Hu(u) = zpl(pc_y + u) - p_top_drop - pb;      // altezza della placca alla posizione u
Hm = (Hu(-PL/2) + Hu(PL/2))/2;                           // altezza media
rw = p_r - win_inset;                                    // raggio angoli della finestra
uw = PL/2 - win_inset;                                   // semilunghezza della finestra

module plate2d()  offset(r=p_r) offset(delta=-p_r)
    polygon([[-PL/2,0],[PL/2,0],[PL/2,Hu(PL/2)],[-PL/2,Hu(-PL/2)]]);
module window2d() offset(delta=-win_inset) plate2d();

// sistema locale del pannello: x=u (lungo Y), y=v (lungo Z),
// z=0 faccia esterna, z>0 verso l'interno della scocca
module to_wall() multmatrix([[0,0,-1,BW/2],[1,0,0,pc_y],[0,1,0,pb],[0,0,0,1]]) children();
module on_walls() { to_wall() children(); mirror([1,0,0]) to_wall() children(); }

module show(p) { if (part=="all" || part==p) children(); }

// ======================================================================
//  1) SCOCCA
// ======================================================================
module body() {
  union() {
    difference() {
        union() {
            difference() {
                rbox_t(Rp, Rt, 0);
                rbox_t(Rp-wall, Rt-wall, -0.01);
            }
            // torrette per le viti del fondo (arrivano fino al piano superiore inclinato)
            for (sx=[-1,1], sy=[-1,1])
                translate([sx*px, sy*py, lid_t]) difference() {
                    cylinder(r=post_r, h=zpl(sy*py) - wall/cos(tilt) + 0.3 - lid_t);
                    translate([0,0,-0.01]) cylinder(d=pilot_d, h=pilot_depth, $fn=24);
                }
            // condotti interni attorno alle finestre
            on_walls() translate([0,0,tp])
                linear_extrude(wall + duct_len - tp)
                    offset(r=duct_w) window2d();
            // battute dell'anello LED (i bracci a scatto si aggiungono dopo le tasche)
            if (led_ring) top_frame() translate([K.x, K.y, 0]) lr_stops();
        }

        // --- finestre pannelli: tasca esterna + foro passante
        on_walls() {
            translate([0,0,-1]) linear_extrude(tp+1)
                offset(r=pocket_c) plate2d();
            translate([0,0,-1]) linear_extrude(wall+duct_len+2)
                window2d();
        }

        // --- lavorazioni sul piano superiore inclinato (tutte perpendicolari al piano)
        top_frame() {
            // manopola: foro encoder + (diffusore dell'anello LED | 4 fori per i perni dell'anello decorativo)
            translate([K.x, K.y, -wall-1]) cylinder(d=enc_hole, h=wall+2);
            if (led_ring) translate([K.x, K.y, 0]) { diffuser_cut(); lr_pockets(); }
            else for (a=[45:90:315])
                translate([K.x+pin_r*cos(a), K.y+pin_r*sin(a), -pin_hole_depth])
                    cylinder(d=pin_hole_d, h=pin_hole_depth+1, $fn=24);

            // scritte
            if (engrave_text)
                translate([0,0,-0.4]) linear_extrude(0.5) top_text();
        }

        // --- presa cavo sul retro
        translate([usb_x, BL/2+1, usb_z]) rotate([90,0,0])
            linear_extrude(wall+3) rr2d(usb_w, usb_h, usb_r);
    }
    // bracci a scatto dell'anello LED (radicati nel fondo delle tasche)
    if (led_ring) top_frame() translate([K.x, K.y, 0]) lr_arms();
    // sede rigida del modulo vibrazione
    if (vt_on) top_frame() vt_nest();
  }
}

module arc_text(s, r, size, a0, c) {
    n = len(s);
    dth = size*0.80/r*180/PI;
    for (i=[0:n-1]) {
        a = a0 + ((n-1)/2 - i)*dth;
        translate([c.x + r*cos(a), c.y + r*sin(a)]) rotate(a-90)
            text(s[i], size=size, halign="center", valign="baseline", font=fnt);
    }
}

// NB: "YOYO CONTROL" e "SELECT" sono da rivedere (decide l'utente)
module top_text() {
    arc_text("YOYO CONTROL", 23.4, 2.6, 90, K);
    translate([K.x+6,  K.y-23.5]) text("<< SEEK >>", size=2.6, halign="center", valign="center", font=fnt);
    translate([0, -27]) text("PUSH = PLAY / PAUSE", size=2.6, halign="center", valign="center", font=fnt);
}

// ======================================================================
//  2) FONDO  (z=0 faccia esterna)
// ======================================================================
module csk_hole(x, y) translate([x, y, 0]) {
    translate([0,0,-0.01]) cylinder(d=csk_d2, h=lid_t+0.02, $fn=32);
    translate([0,0,-0.01]) cylinder(d1=csk_d1, d2=csk_d2, h=csk_h, $fn=32);   // svasatura
}

module pin_hole(p, label) translate([p.x, p.y, 0]) {
    translate([0,0,-0.01]) cylinder(d=pin_d, h=lid_t+0.02, $fn=24);
    translate([0,0,-0.01]) cylinder(d1=pin_cone, d2=pin_d, h=1.2, $fn=32);    // imbocco
    // scritta sul lato esterno (specchiata: si legge guardando il fondo)
    translate([0, -4.2, -0.01]) linear_extrude(0.41) mirror([1,0,0])
        text(label, size=2.4, halign="center", valign="center", font=fnt);
}

module lid() {
    difference() {
        linear_extrude(lid_t)
            rr2d(BW-2*wall-2*lid_tol, BL-2*wall-2*lid_tol, Rp-wall-lid_tol);
        for (sx=[-1,1], sy=[-1,1]) csk_hole(sx*px, sy*py);        // viti scocca
        for (p = sled_scr) csk_hole(p.x, p.y);                     // viti portaschede
        pin_hole(rst_xy, "RST");
        if (boot_hole) pin_hole(boot_xy, "BOOT");
    }
}

// ======================================================================
//  3) PANNELLO LATERALE (placca a feritoie + 2 bracci con dente a scatto)
// ======================================================================
module slots2d() {
    // feritoie parallele al bordo superiore (pendenza = tilt), ritagliate dal contorno della finestra
    Ht0 = Hm - win_inset/cos(tilt);               // bordo alto della finestra a u=0
    for (j=[0:n_slots-1])
        offset(r=0.8) offset(delta=-0.8)
        intersection() {
            offset(delta=-slot_margin) window2d();
            translate([0, Ht0]) rotate(tilt)
                translate([-100, -(slot_margin + slot_w/2 + j*slot_pitch) - slot_w/2]) square([200, slot_w]);
        }
}

// tratto rettilineo (verticale) del bordo anteriore/posteriore della finestra
// sgn=+1 lato posteriore (angolo alto 90-tilt), sgn=-1 lato anteriore (angolo alto 90+tilt)
function vtop(sgn) = Hm + sgn*uw*tan(tilt) - win_inset/cos(tilt) - rw/tan((90 - sgn*tilt)/2);
function vlo() = win_inset + rw;

module end_arm(sgn) {          // braccio a scatto sul bordo verticale della finestra (lato +u, ribaltato per -u)
    vhi = vtop(sgn);
    aw  = min(arm_w, vhi - vlo() - 2);
    vc  = (vlo() + vhi)/2;
    u0  = uw - arm_gap;                    // faccia esterna del braccio
    lzd = wall + duct_len;                 // fine del condotto
    lzc = lzd + catch_gap;                 // faccia di arresto del dente
    lze = lzc + barb_ramp;                 // punta
    multmatrix([[1,0,0,0],[0,0,1,vc-aw/2],[0,1,0,0],[0,0,0,1]])
        linear_extrude(aw)
            polygon([[u0-arm_t, tp-0.01], [u0, tp-0.01], [u0, lzc],
                     [u0+barb_h, lzc], [u0, lze], [u0-arm_t, lze]]);
}

module panel_local() {
    difference() {
        linear_extrude(tp) plate2d();
        translate([0,0,-0.01]) linear_extrude(tp+0.02) slots2d();
    }
    end_arm(+1);                       // lato posteriore (+u)
    mirror([1,0,0]) end_arm(-1);       // lato anteriore (-u)
}

// ======================================================================
//  4) MANOPOLA  (z=0 = base della manopola)
// ======================================================================
module knob() {
    Rk = knob_d/2;
    tip = enc_end - knob_gap;                       // punta dell'albero
    kz0 = tip - knurl_len + 0.5;                    // inizio sede zigrinata
    difference() {
        intersection() {
            linear_extrude(knob_h)
                difference() {
                    circle(r=Rk, $fn=180);
                    for (i=[0:flutes-1]) rotate(i*360/flutes)
                        translate([Rk,0]) circle(d=1.0, $fn=12);
                }
            rotate_extrude($fn=120)
                polygon([[0,0],[Rk-0.7,0],[Rk,0.7],[Rk,knob_h-1.4],[Rk-1.4,knob_h],[0,knob_h]]);
        }
        // sede albero: tratto liscio + tratto zigrinato a pressione
        translate([0,0,-0.01]) cylinder(d=shaft_clear, h=kz0 + 0.02, $fn=32);
        translate([0,0,kz0]) linear_extrude(bore_depth - kz0) knurl2d(knurl_fit);
        // alloggio dado encoder + passaggio bussola
        translate([0,0,-0.01]) cylinder(d=nut_recess_d, h=nut_recess_h, $fn=64);
        translate([0,0,-0.01]) cylinder(d=bush_clear, h=enc_bush - wall - knob_gap + enc_travel + 0.6, $fn=48);   // passaggio bussola: libero anche a fine corsa del pulsante
        // incisioni sul top: anelli concentrici + indicatore
        translate([0,0,knob_h-0.4]) linear_extrude(0.5) {
            for (r=[5,8.5,12]) difference() { circle(r=r+0.25); circle(r=r-0.25); }
            translate([-0.6, 12.8]) square([1.2, 2.6]);
        }
    }
}

// anelli di prova della sede zigrinata: 1, 2, 3 tacche = knurl_test[0], [1], [2]
module test_ring() {
    n = len(knurl_test);
    difference() {
        union() {
            for (i=[0:n-1]) translate([i*tr_pitch,0,0]) cylinder(d=tr_d, h=tr_h, $fn=64);
            translate([0,-1.5,0]) cube([(n-1)*tr_pitch, 3, 2]);
        }
        for (i=[0:n-1]) translate([i*tr_pitch,0,0]) {
            translate([0,0,-0.01]) linear_extrude(tr_h+0.02) knurl2d(knurl_test[i]);
            for (j=[0:i]) rotate(90 + (j - i/2)*20)
                translate([tr_d/2, 0, tr_h/2+1]) cube([1.2, 0.9, tr_h], center=true);
        }
    }
}

// ======================================================================
//  5) ANELLO DECORATIVO ATTORNO ALLA MANOPOLA (z=0 = faccia superiore)
// ======================================================================
module collar() {
    rotate_extrude($fn=120)
        polygon([[ring_ri,0],[ring_ro,0],[ring_ro,ring_h-0.5],[ring_ro-0.5,ring_h],
                 [ring_ri+0.5,ring_h],[ring_ri,ring_h-0.5]]);
    for (a=[45:90:315])
        translate([pin_r*cos(a), pin_r*sin(a), -pin_len]) cylinder(d=pin_d_c, h=pin_len+0.1, $fn=24);
}

// ======================================================================
//  5b) ANELLO LED: diffusore e sedi (sistema del piano superiore, origine sull'asse K, z=0 faccia superiore)
// ======================================================================
lr_nb = -wall - lr_air - lr_t;          // faccia inferiore del PCB dell'anello
lr_nt = lr_nb + lr_pcb_t;               // faccia superiore del PCB (battute)
lr_rb = lr_do/2 + lr_c;                 // faccia interna dei bracci a scatto

// profilo dell'inserto (r, z): sottosquadro sul bordo esterno in basso
function diff_prof(c) = [[diff_ri + c, -diff_t], [diff_ro + diff_snap - c, -diff_t],
                         [diff_ro - c, -diff_t*0.35], [diff_ro - c, 0], [diff_ri + c, 0]];

module diffuser_cut() {
    if (diff_mode == "mmu")
        translate([0,0,-wall-1]) difference() {
            cylinder(r=diff_ro, h=wall+2, $fn=120);
            translate([0,0,-1]) cylinder(r=diff_ri, h=wall+4, $fn=120);
        }
    else {
        // sede dell'inserto (dalla faccia superiore) ...
        rotate_extrude($fn=120) polygon([[diff_ri, -diff_t], [diff_ro + diff_snap, -diff_t],
                                         [diff_ro, -diff_t*0.35], [diff_ro, 1], [diff_ri, 1]]);
        // ... e finestre verso i LED, interrotte dai ponti che reggono il disco centrale
        difference() {
            translate([0,0,-wall-1]) difference() {
                cylinder(r=diff_ro, h=wall+1-diff_t+0.01, $fn=120);
                translate([0,0,-1]) cylinder(r=diff_ri, h=wall+4, $fn=120);
            }
            for (i=[0:diff_brg_n-1]) rotate(lr_clip_a0 + i*360/diff_brg_n)
                translate([diff_ri - 1, -diff_brg_w/2, -wall-2]) cube([diff_ro - diff_ri + 2, diff_brg_w, wall+2]);
        }
    }
}

// diffusore (z=0 faccia superiore della scocca). "insert": anello a scatto; "mmu": riempie esattamente la corona
module diffuser() {
    if (diff_mode == "mmu")
        translate([0,0,-wall]) difference() {
            cylinder(r=diff_ro, h=wall, $fn=120);
            translate([0,0,-1]) cylinder(r=diff_ri, h=wall+2, $fn=120);
        }
    else rotate_extrude($fn=120) polygon(diff_prof(diff_c));
}

// 4 bracci a scatto (dente sotto il PCB) + 4 battute (sopra il bordo esterno del PCB), alternati
module lr_pockets() for (i=[0:lr_clips-1]) rotate(lr_clip_a0 + i*360/lr_clips)
    translate([lr_rb, -lr_clip_w/2 - 0.3, -wall - 1]) cube([lr_clip_t + lr_pocket_c, lr_clip_w + 0.6, wall + 1 - lr_clip_root]);
module lr_arms() {
    ntip = lr_nb - lr_barb_c - lr_barb_ramp;
    for (i=[0:lr_clips-1]) rotate(lr_clip_a0 + i*360/lr_clips) {
        // braccio flessibile, radicato nel fondo della tasca
        translate([lr_rb, -lr_clip_w/2, ntip]) cube([lr_clip_t, lr_clip_w, -lr_clip_root - ntip + 0.01]);
        // dente con rampa d'invito
        translate([0, lr_clip_w/2, 0]) rotate([90,0,0]) linear_extrude(lr_clip_w)
            polygon([[lr_rb + 0.01, lr_nb - lr_barb_c], [lr_do/2 - lr_barb, lr_nb - lr_barb_c], [lr_rb + 0.01, ntip]]);
    }
}
module lr_stops() {
    for (i=[0:lr_clips-1]) rotate(lr_clip_a0 + (i + 0.5)*360/lr_clips)
        translate([lr_do/2 - lr_stop, -lr_stop_w/2, lr_nt]) cube([lr_stop + lr_c + 1.0, lr_stop_w, -wall - lr_nt + 0.01]);
}

// ======================================================================
//  6) SEDE MODULO VIBRAZIONE (sistema del piano superiore; solo materiale AGGIUNTO alla scocca)
// ======================================================================
module vt_nest() {
    xo = vt_xi + vt_wall;
    // pareti laterali e battuta (con tacca fili: lascia 1.0 di materiale sotto la faccia)
    for (sx = [-1, 1]) translate([sx > 0 ? vt_xi : -xo, vt_sf, vt_zb]) cube([vt_wall, vt_back - vt_sf, vt_z1 - vt_zb + 0.01]);
    difference() {
        translate([-xo, vt_back - vt_wall, vt_zb]) cube([2*xo, vt_wall, vt_z1 - vt_zb + 0.01]);
        translate([-vt_notch_w/2, vt_back - vt_wall - 1, vt_zb - 1]) cube([vt_notch_w, vt_wall + 2, vt_z1 - 1.0 - vt_zb + 1]);
    }
    // labbri sotto i bordi del PCB (2 per lato) con rampa d'invito che pinza il PCB contro la faccia
    for (sx = [-1, 1], s0 = [vt_sb - 1 - vt_tab_l, vt_sf + 1]) {
        xa = vt_w/2 - vt_lip_e;
        translate([sx > 0 ? xa : -xo, s0, vt_zb]) cube([xo - xa, vt_tab_l, vt_lip_t]);
        // nervatura (rampa) sulla faccia superiore del labbro: sale di vt_gz + vt_pinch
        translate([sx > 0 ? xa : -(vt_w/2), s0, 0]) rotate([90,0,90]) linear_extrude(vt_lip_e)
            polygon([[0, vt_zl - 0.01], [1.5, vt_zl + vt_gz + vt_pinch], [vt_tab_l, vt_zl + vt_gz + vt_pinch], [vt_tab_l, vt_zl - 0.01]]);
    }
    // ganci a scatto sul piano (davanti al PCB), uno per lato
    for (m = [0, 1]) mirror([m, 0, 0]) {
        tip = vt_sf - vt_arm_gap;                 // faccia di arresto del dente
        a0 = tip - vt_arm_l;
        translate([vt_xi, a0, vt_zb]) cube([vt_arm_t, vt_arm_l, vt_z1 - vt_zb + 0.01]);                       // braccio
        translate([vt_xi, a0 - vt_root, vt_zb]) cube([vt_arm_t + 1.2, vt_root + 0.01, vt_z1 - vt_zb + 0.01]);  // radice
        translate([0, 0, vt_zb]) linear_extrude(vt_z1 - vt_zb + 0.01)                                         // dente (rampa verso -s)
            polygon([[vt_xi + 0.01, tip], [vt_xi - vt_barb, tip], [vt_xi + 0.01, tip - vt_barb_l]]);
    }
}

// ======================================================================
//  PIATTI DI STAMPA (A1 mini: 180x180, ogni piatto centrato e <= 170x170)
// ======================================================================
function plate_on(n) = (part != "all" || plate == 0 || plate == n);

// piatto 1: scocca, piano superiore sul piatto (nessun supporto: lamatura e fori con piccoli ponti)
// con diff_mode="mmu" il diffusore va esportato a parte (part="diffuser") con la STESSA trasformazione:
// in Bambu Studio si caricano i due STL come parti di un unico oggetto e si assegna il filamento bianco.
module plate1_frame() translate([0, -3.6, 0]) rotate([180,0,0]) rotate([-tilt,0,0]) translate([0,0,-z0]) children();
module plate1() {
    show("body") plate1_frame() body();
    if (led_ring && diff_mode == "mmu")
        show("diffuser") color(c_diff) plate1_frame() top_frame() translate([K.x, K.y, 0]) diffuser();
}

// piatto 2 (NERO): fondo (faccia esterna sotto) e portaschede (piastra sotto)
module plate2() {
    show("lid")   translate([-35, 0, 0]) lid();
    show("sled")  translate([ 35, 0, -lid_t]) sled();
}

// piatto 3 (RAME, accento): manopola capovolta e 2 pannelli laterali (faccia esterna sotto)
module plate3() {
    show("knob")      translate([0, 28, knob_h]) rotate([180,0,0]) knob();
    if (!led_ring) show("collar") translate([ 50, 28, ring_h]) rotate([180,0,0]) collar();
    show("panel") {
        translate([-35, -40, 0]) panel_local();
        translate([ 35, -40, 0]) panel_local();
    }
}

// piatto 4 (PLA BIANCO, solo per il diffusore): diffusore "insert", faccia a vista sul piatto
module plate4() {
    if (led_ring && diff_mode == "insert")
        show("diffuser") rotate([180,0,0]) diffuser();
}

// tassello di prova: porzione della faccia superiore attorno all'encoder con sede del diffusore,
// ponti, ganci e battute dell'anello LED (per provare scatto dell'anello e del diffusore prima della scocca).
// Stampato come la scocca: faccia superiore sul piatto.
tile_r = 26;  tile_depth = 10;
module test_tile() {
    rotate([180,0,0]) intersection() {
        translate([-K.x, -K.y, 0]) rotate([-tilt,0,0]) translate([0,0,-z0]) body();
        translate([0,0,-tile_depth]) cylinder(r=tile_r, h=tile_depth + 0.01, $fn=120);
        translate([-(BW/2 - wall - duct_len - 0.05), -50, -50]) cube([2*(BW/2 - wall - duct_len - 0.05), 100, 100]);  // fuori dai condotti dei pannelli
    }
}

// piatto 5 "prova" (tolleranze): anelli di prova della sede zigrinata, diffusore, tassello con sede anello LED
module plate5() {
    show("test_ring") translate([-50, -45, 0]) test_ring();
    show("diffuser")  translate([ 50, -45, 0]) rotate([180,0,0]) diffuser();
    show("test_tile") translate([  0,  25, 0]) test_tile();
}

module print_layout() {
    if (plate == 5) plate5();                    // solo esplicito (non nel 0 = tutti)
    if (plate_on(1)) translate([plate==0 && part=="all" ? -190 : 0, 0, 0]) color(c_body) plate1();
    if (plate_on(2)) color(c_base) plate2();
    if (plate_on(3)) translate([plate==0 && part=="all" ? 190 : 0, 0, 0]) color(c_acc) plate3();
    if (plate_on(4)) translate([0, plate==0 && part=="all" ? 125 : 0, 0]) color(c_diff) plate4();
}

// ======================================================================
//  ASSEMBLY / ESPLOSO
// ======================================================================
module clip(shell=false) {
    if (section_view && (shell || !section_shell))
        difference() { union() children(); translate([cut_x,-100,-100]) cube([80,200,260]); }   // volume contenuto: anteprima corretta anche da vicino
    else children();
}

module assembly(ex) {
    e_body = 2.6*ex;  e_lid = -1.9*ex;  e_sled = -0.9*ex;
    clip(true) {
        color(c_body) show("body") translate([0,0,e_body]) body();
        color(c_base) show("panel") on_walls() translate([0,0,-1.6*ex]) panel_local();
    }
    clip() {
        color(c_base) show("lid")  translate([0,0,e_lid]) lid();
        color(c_base) show("sled") translate([0,0,e_sled]) sled();
        translate([0,0,e_body]) top_frame() {
            color(c_acc) show("knob")   translate([K.x,K.y,knob_gap+1.6*ex]) knob();
            if (!led_ring) color(c_acc) show("collar") translate([K.x,K.y,0.8*ex]) collar();
            if (led_ring) color(c_diff) show("diffuser") translate([K.x,K.y,0.8*ex]) diffuser();
        }
        if (show_electronics && part=="all") {
            translate([0,0,e_body]) top_frame() {
                translate([K.x,K.y,-3.2*ex]) encoder_model(ex > 0);
                if (vt_on) translate([0,0,-1.6*ex]) vib_top_model();
                if (led_ring) translate([K.x,K.y,-2.4*ex]) led_ring_model();
            }
            translate([0,0,e_sled]) sled_electronics();
            translate([0,0,e_lid]) screws_model(ex);
        }
    }
}

if (mode == "print") print_layout();
else if (mode == "assembly") assembly(0);
else if (mode == "exploded") assembly(25);
