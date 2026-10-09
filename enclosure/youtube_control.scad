// ======================================================================
//  YOUTUBE CONTROL  -  case stampabile in 3D (OpenSCAD)
// ======================================================================
//  PEZZI:
//   1  body      scocca 105x70 (3:2), piano superiore inclinato, spigoli arrotondati, finestre/condotti di
//                raffreddamento, fori manopola e pulsante, torrette viti, presa USB-C di ricarica sul retro
//   2  lid       fondo, entra nella scocca e si avvita (4x M3); interfaccia FISSA per il portaschede
//                (4 fori svasati + fori per spillo RST/BOOT)
//   3  sled      portaschede intercambiabile (file portaschede.scad): ESP32-S3 SuperMini capovolta,
//                modulo TP4056, portabatteria 18650 stampato. Si avvita al fondo dal basso (4x M3)
//   4  panel x2  pannelli laterali a feritoie, si incastrano a scatto
//   5  knob      manopola zigrinata (stile ottone), sede a pressione per albero zigrinato 18 denti
//   6  collar    anello decorativo attorno alla manopola
//   7  cap       cappuccio del pulsante PBS-110 (calzato sul tasto blu, copre il dado)
//   8  test_ring anelli di prova della sede zigrinata (3 giochi diversi), da stampare per primi
//
//  COMPONENTI PREVISTI (quote in dimensioni.md)
//   - encoder EC11E (bussola M7x0.75, albero 6 mm zigrinato 18 denti, 20 mm dal piano di appoggio)
//   - pulsante da pannello PBS-110 (foro 7, dado sul lato esterno, nascosto dal cappuccio)
//   - ESP32-S3 SuperMini, modulo TP4056 USB-C, cella 18650 + contatti a molla/piastrina
//   - 8x viti M3x8 svasate autofilettanti (4 fondo->scocca, 4 fondo->portaschede)
//   - 4x viti M2x5 autofilettanti (TP4056)
//
//  mode  = "print"     -> piatti di stampa (plate = 1/2/3, 0 = tutti affiancati, solo anteprima)
//          "assembly"  -> tutto montato (controllo incastri)
//          "exploded"  -> vista esplosa
//  part  = "all" oppure un singolo pezzo (per esportare l'STL separato; ignora "plate")
//  show_electronics: modelli semplificati dei componenti, SOLO in assembly/exploded (mai nei piatti)
// ======================================================================

mode          = "print";     // "print" | "assembly" | "exploded"
plate         = 1;           // 1 = scocca | 2 = fondo + portaschede + pannelli | 3 = manopola, anello, cappuccio, test | 0 = tutti
part          = "all";       // "all" | "body" | "lid" | "sled" | "panel" | "knob" | "collar" | "cap" | "test_ring"
section_view  = false;       // sezione (solo assembly/exploded)
cut_x         = 0;           // piano di sezione (si toglie il lato X > cut_x)
section_shell = false;       // true: la sezione taglia solo scocca e pannelli (interno visibile)
show_electronics = true;     // componenti (solo assembly/exploded)
engrave_text  = false;       // scritte incise sulla faccia superiore
button_glyph  = false;       // simbolo play/pause inciso sul tasto
fnt           = "Liberation Sans:style=Bold";

$fn = 48;

// colori di anteprima (= filamenti proposti per i piatti)
c_body = "#34373c";          // piatto 1: scocca (grafite)
c_base = "#c4c8cc";          // piatto 2: fondo, portaschede, pannelli (grigio chiaro)
c_acc  = "#c99a2e";          // piatto 3: manopola, anello, cappuccio (ottone)

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
nut_recess_d = 13;  nut_recess_h = 1.2;
enc_end    = (enc_bush - wall) + enc_shaft;      // fine albero sopra la faccia superiore
bore_depth = enc_end - knob_gap + 0.5;
knob_h     = bore_depth + 2.5;

// anello decorativo (collar)
ring_ri = 17.3;  ring_ro = 20.5;  ring_h = 1.4;
pin_r = 18.9;  pin_d_c = 2.2;  pin_len = 2.0;
pin_hole_d = 2.5;  pin_hole_depth = 2.2;

// anelli di prova
tr_d = 12;  tr_h = knurl_len + 2;  tr_pitch = 15;

// ----------------------------------------------------------------------
//  PULSANTE PLAY/PAUSE  (PBS-110 da pannello + cappuccio stampato)
//  quote nel sistema del piano superiore: z=0 faccia superiore, z<0 verso l'interno
// ----------------------------------------------------------------------
B          = [-10, -33];   // centro tasto (coordinate sul piano inclinato)
btn_hole   = 7.2;          // foro pannello (7.0 nominale + gioco FDM)
btn_cb_d   = 13;           // lamatura esterna per dado + rondella
btn_cb_h   = 1.2;          // profondita' lamatura (restano wall-btn_cb_h = 1.8 sotto il dado)
btn_nut_af = 9.5;          // dado: chiave (da misurare)
btn_nut_t  = 2.0;  btn_washer_t = 0.5;
btn_key_d  = 6.5;          // diametro tasto blu (da misurare)
btn_key_above = 4.5;       // sporgenza tasto sopra il dado (da misurare)
btn_key_fit = 0.10;        // interferenza cappuccio/tasto (foro = btn_key_d - fit)
btn_travel = 1.0;          // corsa del tasto
btn_body_d = 9.5;  btn_below = 20;   // ingombro sotto il pannello (corpo + terminali + fili)
cap_head_d = 16.0;
cap_gap    = 0.5;          // margine oltre la corsa (bordo cappuccio / faccia, cavita' / dado)
cap_top_t  = 1.6;
z_nut_top  = -btn_cb_h + btn_washer_t + btn_nut_t;
z_key_top  = z_nut_top + btn_key_above;
cap_z0     = btn_travel + cap_gap;                       // bordo inferiore del cappuccio (a riposo)
cap_cav_d  = btn_nut_af/cos(30) + 1.2;                   // cavita' sopra il dado
cap_cav_h  = max(0.6, z_nut_top + btn_travel + cap_gap - cap_z0);
cap_h      = z_key_top + cap_top_t - cap_z0;
z_ceil     = -wall;

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
            // manopola: foro encoder + 4 fori per i perni dell'anello
            translate([K.x, K.y, -wall-1]) cylinder(d=enc_hole, h=wall+2);
            for (a=[45:90:315])
                translate([K.x+pin_r*cos(a), K.y+pin_r*sin(a), -pin_hole_depth])
                    cylinder(d=pin_hole_d, h=pin_hole_depth+1, $fn=24);

            // pulsante PBS-110: foro passante + lamatura per il dado + anello inciso
            translate([B.x, B.y, -wall-1]) cylinder(d=btn_hole, h=wall+2);
            if (btn_cb_h > 0)
                translate([B.x, B.y, -btn_cb_h]) cylinder(d=btn_cb_d, h=btn_cb_h+1, $fn=64);
            translate([B.x, B.y, -0.6]) difference() {
                cylinder(d=24.4, h=1);
                translate([0,0,-0.1]) cylinder(d=22.8, h=1.2);
            }

            // scritte
            if (engrave_text)
                translate([0,0,-0.4]) linear_extrude(0.5) top_text();
        }

        // --- presa cavo sul retro
        translate([usb_x, BL/2+1, usb_z]) rotate([90,0,0])
            linear_extrude(wall+3) rr2d(usb_w, usb_h, usb_r);
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
    translate([B.x,    B.y+14.5]) text("SELECT",     size=2.6, halign="center", valign="center", font=fnt);
    translate([B.x+14.5, B.y])    text("PLAY/PAUSE", size=2.4, halign="left",   valign="center", font=fnt);
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
        translate([0,0,-0.01]) cylinder(d=bush_clear, h=enc_bush - wall - knob_gap + 0.6, $fn=48);
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
//  6) CAPPUCCIO PULSANTE (z=0 = bordo inferiore; calza sul tasto blu del PBS-110)
// ======================================================================
module cap() {
    difference() {
        rotate_extrude($fn=96)
            polygon([[0,0],[cap_head_d/2,0],[cap_head_d/2,cap_h-0.8],
                     [cap_head_d/2-0.8,cap_h],[0,cap_h]]);
        // cavita' sopra dado e rondella
        translate([0,0,-0.01]) cylinder(d=cap_cav_d, h=cap_cav_h+0.01, $fn=64);
        // sede del tasto (a pressione)
        translate([0,0,cap_cav_h-0.01]) cylinder(d=btn_key_d-btn_key_fit, h=z_key_top-cap_z0-cap_cav_h+0.01, $fn=48);
        translate([0,0,cap_h-0.4]) linear_extrude(0.5) {
            difference() { circle(r=6.05, $fn=96); circle(r=5.55, $fn=96); }
            if (button_glyph) {
                polygon([[-5.2*0.5-1.6,-2.6],[-5.2*0.5-1.6,2.6],[-0.2,0]]);
                translate([1.0,-2.6]) square([1.1,5.2]);
                translate([3.0,-2.6]) square([1.1,5.2]);
            }
        }
    }
}

// ======================================================================
//  PIATTI DI STAMPA (A1 mini: 180x180, ogni piatto centrato e <= 170x170)
// ======================================================================
function plate_on(n) = (part != "all" || plate == 0 || plate == n);

// piatto 1: scocca, piano superiore sul piatto (nessun supporto: lamatura e fori con piccoli ponti)
module plate1() {
    show("body") translate([0, -3.6, 0]) rotate([180,0,0]) rotate([-tilt,0,0]) translate([0,0,-z0]) body();
}

// piatto 2: fondo (faccia esterna sotto), portaschede (piastra sotto), 2 pannelli (faccia esterna sotto)
module plate2() {
    show("lid")   translate([-35, 20, 0]) lid();
    show("sled")  translate([ 35, 20, -lid_t]) sled();
    show("panel") {
        translate([-35, -68, 0]) panel_local();
        translate([ 35, -68, 0]) panel_local();
    }
}

// piatto 3 (colore accento): manopola e cappuccio capovolti, anello capovolto, anelli di prova
module plate3() {
    show("knob")      translate([-25, 18, knob_h]) rotate([180,0,0]) knob();
    show("collar")    translate([ 25, 18, ring_h]) rotate([180,0,0]) collar();
    show("cap")       translate([-25,-22, cap_h]) rotate([180,0,0]) cap();
    show("test_ring") translate([  5,-22, 0]) test_ring();
}

module print_layout() {
    if (plate_on(1)) translate([plate==0 && part=="all" ? -190 : 0, 0, 0]) color(c_body) plate1();
    if (plate_on(2)) color(c_base) plate2();
    if (plate_on(3)) translate([plate==0 && part=="all" ? 190 : 0, 0, 0]) color(c_acc) plate3();
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
            color(c_acc) show("collar") translate([K.x,K.y,0.8*ex]) collar();
            color(c_acc) show("cap")    translate([B.x,B.y,cap_z0+1.2*ex]) cap();
        }
        if (show_electronics && part=="all") {
            translate([0,0,e_body]) top_frame() {
                translate([K.x,K.y,-3.2*ex]) encoder_model(ex > 0);
                translate([B.x,B.y,-3.2*ex]) button_model(ex > 0);
            }
            translate([0,0,e_sled]) sled_electronics();
            translate([0,0,e_lid]) screws_model(ex);
        }
    }
}

if (mode == "print") print_layout();
else if (mode == "assembly") assembly(0);
else if (mode == "exploded") assembly(25);
