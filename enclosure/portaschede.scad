// ======================================================================
//  PORTASCHEDE ("sled")  -  incluso da youtube_control.scad (NON autonomo:
//  usa i parametri comuni di scocca/fondo). Esportazione: part="sled".
// ======================================================================
//  Modulo intercambiabile avvitato al fondo dal basso (4 viti M3x8 svasate
//  autofilettanti nelle torrette sled_scr). Coordinate = quelle della scocca
//  (X larghezza, Y lunghezza, +Y retro, z=0 faccia esterna del fondo):
//  la piastra va da z = lid_t a z = lid_t + sled_t.
//
//   - CORSIA SINISTRA LIBERA E PIANA per il "pacco" elettronico (millefori 8 x 20 con la SuperMini saldata sopra,
//     isolata con guaina/kapton): NON e' fissata (decisione 2026-10-15, V1); la corsia lo contiene con 3 nervature
//     basse (1 davanti, 2 dietro) e con la parete della culla / il condotto del pannello sinistro sui lati
//   - modulo TP4056 USB-C su 4 colonnine (viti M2), USB-C allineata alla presa sul retro
//   - culla per cella 18650 con sedi per contatti a piastrina/molla, fori fili
//   - tasca "parcheggio" del connettore volante 2 x 5 (codino della millefori <-> cablaggio della scocca)
// ======================================================================

sled_c      = 0.25;    // gioco perimetrale in piu' rispetto al fondo
post_clr    = 0.5;     // gioco attorno alle torrette angolari della scocca
sled_boss_d = 7;
sled_boss_top = 9;     // quota assoluta della cima delle torrette viti (vite M3x8 dal basso)
sp_top      = lid_t + sled_t;          // faccia superiore della piastra

// ---------------- ESP32-S3 SuperMini (quote: dimensioni.md) ----------------
// La scheda e' saldata sulla millefori (modello in componenti.scad); qui restano le sole quote.
sm_l    = 23.5;  sm_w = 18;
sm_t    = 1.0;             // spessore PCB (da misurare)
sm_rst  = [8.6, 4.45];     // centro tasto RST (X,Y) nel riferimento Nologo, lato componenti (+-0.3)
sm_boot = [8.6, 13.5];     // centro tasto BOOT
sm_usb_w = 8.94;  sm_usb_l = 7.35;  sm_usb_h = 3.2;
sm_usb_out = 3.5;          // sporgenza USB-C oltre il PCB: 27,0 totali misurati dall'utente (2026-10-11); 1.2 se il PCB fosse piu' lungo

// ---------------- Modulo TP4056 USB-C (quote incerte: misurare) ----------------
tp_l = 28;  tp_w = 17.3;  tp_t = 1.2;
tp_usb_out = 0.8;          // sporgenza USB-C oltre il PCB
tp_usb_zc  = 1.6;          // centro USB-C sopra la faccia superiore del PCB
tp_hole_e  = [2.2, 2.2];   // centro fori dai bordi (lungo X modulo, lungo Y modulo)
tp_pilot   = 1.6;          // foro pilota vite M2 autofilettante
tp_so_d    = 4.2;          // colonnine
tp_y1 = BL/2 - wall - 0.3 - tp_usb_out;    // bordo PCB lato USB (USB-C a 0.3 dalla parete)
tp_zb = usb_z - tp_usb_zc - tp_t;          // faccia inferiore PCB
tp_holes = [for (sx=[-1,1], e=[tp_hole_e.x, tp_l - tp_hole_e.x])
            [usb_x + sx*(tp_w/2 - tp_hole_e.y), tp_y1 - e]];

// ---------------- Cella 18650 ----------------
bat_d     = 18.6;          // 18.5-18.6 (fino a ~19 con involucro)
bat_len   = 65;            // 65 non protetta; protette 67-70: aumentare (verificato fino a 70)
bat_clr   = 0.4;           // gioco radiale
bat_lift  = 1.0;           // fondo culla sotto la cella
bat_allow = 5;             // spazio assiale per molla compressa + piastrina
bat_x     = 11.6;          // asse cella
bat_y0    = -47;           // estremo anteriore della culla
bat_wall  = 1.2;           // pareti laterali
bat_end_t = 3.2;           // testate (contengono la sede del contatto)
// contatti standard a piastrina/molla per 18650 (da misurare)
ct_w = 11;  ct_h = 12;  ct_t = 0.6;  ct_win = 7;  ct_lip = 0.8;
bat_wire_d = 2.6;          // foro filo nelle testate
tie_w = 4.5;  tie_d = 1.5; // fascetta (ritegno cella): una sola, nel tratto dietro la millefori
tie_y = 21.6;              // centro della fascetta (dietro la corsia del pacco, che arriva a Y 19,1; TP4056 da 20,4 ma a X <= -3,35)
bat_r   = bat_d/2 + bat_clr;
bat_lin = bat_len + bat_allow;
bat_lc  = bat_lin + 2*bat_end_t;
bat_zc  = sp_top + bat_lift + bat_d/2;
bat_xo  = bat_r + bat_wall;                // semilarghezza esterna culla
bat_xl  = bat_x - bat_xo;                  // faccia sinistra della culla (0.7)
bat_y1  = bat_y0 + bat_lc;                 // faccia posteriore della testata posteriore
bat_head_top = bat_zc + ct_h/2 + 0.5;      // quota della cima delle testate

// ---------------- Pacco elettronico libero nella corsia sinistra ----------------
// Millefori unica 8 x 20 (22,54 x 60) con la SuperMini saldata sopra (strip maschio): firmware/millefori/README.md.
// V1: niente fissaggi (torrette, fermi, battute rimossi), il pacco e' avvolto in guaina/kapton e appoggia sulla piastra.
// Sistema millefori (solo per il modello di anteprima e gli inviluppi): x verso destra (A = lato sinistro intatto),
// y verso il retro (riga 1 = lato USB-C della SuperMini), lato componenti in alto.
mf_on     = true;
mf_w      = 22.54;  mf_l = 60;  mf_t = 1.6;       // 8 colonne tagliate a meta' passo x 20 righe
mf_pitch  = 2.54;
mf_a1     = [3.49, 5.87];                         // centro del foro A1
mf_sold   = 1.8;                                  // lato saldature (piedini a ~1, fili 30 AWG)
mf_comp   = 11.5;                                 // altezza massima componenti (elettrolitici 5 x 11)
mf_strip_h = 2.5;                                 // plastica della strip maschio della SuperMini
mf_sm_x   = 22.65;  mf_sm_y = 4.28;               // angolo del PCB della SuperMini (x massimo, y minimo) sulla millefori
mf_hole_d = 3.2;  mf_holes = [[2.0, 2.0], [2.0, 58.0]];   // fori M3 originali (non usati: solo per il modello)
mf_head_d = 5.5;  mf_head_h = 1.7;

// corsia: tra il condotto del pannello sinistro (a X = -23) e la parete sinistra della culla (X = 0,7);
// davanti una nervatura, dietro due (spazio libero tra le nervature = lunghezza del pacco + 1,8)
ln_x0 = -(BW/2 - wall - duct_len);                // faccia del condotto del pannello sinistro (-23)
ln_x1 = bat_xl;                                   // parete sinistra della culla (0,7)
ln_y0 = -42.0;  ln_y1 = 20.0;                     // facce interne delle nervature (davanti: dietro la torretta angolare della scocca, a X -26,68 / Y -44,18; dietro: davanti al TP4056, bordo a Y 20,4)
ln_w  = ln_x1 - ln_x0;  ln_l = ln_y1 - ln_y0;     // 23,7 x 62,0
rib_h = 5;  rib_t = 0.8;   // altezza 5: la ribalta posteriore resta sotto il PCB del TP4056 (Z 11,2)                          // nervature basse di contenimento
rib_front = [-20, -3];                            // intervallo X della nervatura anteriore
rib_rear  = [[-20, -14], [-8, -2]];               // intervalli X delle 2 nervature posteriori
// ingombro del pacco (con guaina): 22,8 x 60,2; la parte alta (componenti) parte a 2,1 dal bordo sinistro, la fascia a sinistra
// e' solo PCB + saldature (i denti dei bracci dei pannelli entrano fino a X = -21,25 tra Z 14,6 e 21,8, Y -26,0...-23,1)
pk_w = 22.8;  pk_l = 60.2;  pk_h = 15;  pk_lo_h = 5;  pk_lo_w = 2.1;
pk_dx = 0;  pk_dy = 0;                            // spostamento di prova rispetto alla posizione centrata (+-0,45 / +-0,9 al massimo)
pk_x0 = ln_x0 + (ln_w - pk_w)/2 + pk_dx;
pk_y0 = ln_y0 + (ln_l - pk_l)/2 + pk_dy;
// posizione di riferimento della millefori dentro la guaina (solo anteprima/inviluppi)
mf_x0 = pk_x0 + (pk_w - mf_w)/2;
mf_y0 = pk_y0 + (pk_l - mf_l)/2;
mf_zb = sp_top + mf_sold + 0.2;                   // faccia inferiore del PCB (appoggia sulle saldature)
mf_zt = mf_zb + mf_t;
function mf_row_y(r) = mf_y0 + mf_a1.y + (r - 1)*mf_pitch;

// ---------------- Tasca "parcheggio" del connettore volante 2 x 5 ----------------
// Codino (9 fili dalla millefori, femmina Dupont 2x5) + cablaggio della scocca (maschio 2x5): la coppia, in piedi
// (spina ~12.7 x 5.1 x ~25), sta in una tasca a U dietro la culla, dove scendono anche i fili dell'anello.
cn_w = 12.7;  cn_d = 5.1;  cn_h = 25;             // ingombro della coppia innestata (stima; fili esclusi)
cn_c = [0.2, 0.1];                                // gioco per lato (X, Y)
cn_x0 = 7.0;                                      // bordo sinistro interno
cn_y0 = 33.0;                                     // bordo anteriore interno (lascia 3.6 dietro la testata della culla per il filo +)
cn_t  = 1.2;  cn_wall_h = 8.5;                    // pareti e altezza
cn_xi = [cn_x0, cn_x0 + cn_w + 2*cn_c.x];
cn_yi = [cn_y0, cn_y0 + cn_d + 2*cn_c.y];

// ----------------------------------------------------------------------
module sled_plate2d() {
    difference() {
        rr2d(BW-2*wall-2*lid_tol-2*sled_c, BL-2*wall-2*lid_tol-2*sled_c, Rp-wall-lid_tol-sled_c);
        for (sx=[-1,1], sy=[-1,1]) translate([sx*px, sy*py]) circle(r=post_r+post_clr);
    }
}

module sled() {
    difference() {
        union() {
            translate([0,0,lid_t]) linear_extrude(sled_t) sled_plate2d();
            // torrette viti dal fondo
            for (p = sled_scr) translate([p.x, p.y, lid_t]) cylinder(d=sled_boss_d, h=sled_boss_top - lid_t, $fn=40);
            // TP4056: colonnine
            for (h = tp_holes) translate([h.x, h.y, sp_top - 0.01]) cylinder(d=tp_so_d, h=tp_zb - sp_top + 0.01, $fn=32);
            // culla 18650
            bat_cradle_solid();
            if (mf_on) { lane_ribs(); cn_pocket(); }
        }
        // fori pilota viti fondo (dal basso)
        for (p = sled_scr) translate([p.x, p.y, lid_t - 0.01]) cylinder(d=pilot_d, h=sled_boss_top - lid_t - 0.8, $fn=24);
        // fori pilota TP4056
        for (h = tp_holes) translate([h.x, h.y, sp_top]) cylinder(d=tp_pilot, h=tp_zb, $fn=20);
        if (mf_on) cn_cuts();
        bat_cradle_cuts();
        // spazio per i bracci a scatto dei pannelli laterali (toccavano la culla 18650)
        arm_clear();
        // gioco attorno alle torrette angolari della scocca (a tutta altezza)
        for (sx=[-1,1], sy=[-1,1]) translate([sx*px, sy*py, lid_t - 1]) cylinder(r=post_r+post_clr, h=60);
    }
}

// ingombro dei bracci a scatto dei pannelli (+ arm_clr), nel sistema del pannello (vedi end_arm)
arm_clr = 0.4;
module arm_clear() on_walls() for (sg = [1, -1]) {
    vhi = vtop(sg);  aw = min(arm_w, vhi - vlo() - 2);  vc = (vlo() + vhi)/2;
    u0 = uw - arm_gap;  lze = wall + duct_len + catch_gap + barb_ramp;
    translate([sg > 0 ? u0 - arm_t - arm_clr : -(u0 + barb_h + arm_clr), vc - aw/2 - arm_clr, tp])
        cube([arm_t + barb_h + 2*arm_clr, aw + 2*arm_clr, lze - tp + arm_clr]);
}

// ---------------- nervature di contenimento della corsia (NON fissaggi) ----------------
module lane_ribs() {
    translate([rib_front[0], ln_y0 - rib_t, sp_top - 0.01]) cube([rib_front[1] - rib_front[0], rib_t, rib_h + 0.01]);
    for (r = rib_rear) translate([r[0], ln_y1, sp_top - 0.01]) cube([r[1] - r[0], rib_t, rib_h + 0.01]);
}

// ---------------- tasca del connettore volante ----------------
module cn_pocket() {
    ztop = sp_top + cn_wall_h;
    translate([cn_xi[0] - cn_t, cn_yi[0] - cn_t, sp_top - 0.01]) difference() {
        cube([cn_xi[1] - cn_xi[0] + 2*cn_t, cn_yi[1] - cn_yi[0] + 2*cn_t, ztop - sp_top + 0.01]);
        translate([cn_t, cn_t, 0.02]) cube([cn_xi[1] - cn_xi[0], cn_yi[1] - cn_yi[0], 50]);
    }
}
module cn_cuts() {
    // tacca nella parete sinistra, a livello della piastra: ci passa il mazzo di fili che arriva dalla millefori
    translate([cn_xi[0] - cn_t - 1, (cn_yi[0] + cn_yi[1])/2 - 4, sp_top]) cube([cn_t + 2, 8, 3.5]);
}

// ---------------- culla 18650 ----------------
module bat_cradle_solid() {
    // pareti laterali e fondo fino all'asse della cella
    translate([bat_x - bat_xo, bat_y0, sp_top - 0.01]) cube([2*bat_xo, bat_lc, bat_zc - sp_top + 0.01]);
    // testate piu' alte per i contatti
    for (y = [bat_y0, bat_y0 + bat_lc - bat_end_t])
        translate([bat_x - bat_xo, y, sp_top - 0.01]) cube([2*bat_xo, bat_end_t, bat_zc + ct_h/2 + 0.5 - sp_top]);
}

module bat_cradle_cuts() {
    yi0 = bat_y0 + bat_end_t;  yi1 = yi0 + bat_lin;
    // alloggio cella
    translate([bat_x, yi0, bat_zc]) rotate([-90,0,0]) cylinder(r=bat_r, h=bat_lin, $fn=96);
    translate([bat_x - bat_r, yi0, bat_zc]) cube([2*bat_r, bat_lin, bat_d]);
    for (k = [0, 1]) {
        yin = k == 0 ? yi0 : yi1;              // faccia interna della testata
        sg  = k == 0 ? -1 : 1;                 // verso l'esterno
        // sede piastrina: fessura nella testata, aperta in alto
        translate([bat_x - (ct_w+0.4)/2, yin + sg*ct_lip - (k == 0 ? ct_t + 0.3 : 0), sp_top + 0.6])
            cube([ct_w + 0.4, ct_t + 0.3, 30]);
        // finestra verso la cella (molla / bottone)
        translate([bat_x - ct_win/2, min(yin, yin + sg*(ct_lip + 0.1)), bat_zc - ct_win/2])
            cube([ct_win, ct_lip + 0.1, 30]);
        // foro filo, dalla fessura verso l'esterno
        translate([bat_x, yin + sg*ct_lip, sp_top + 0.6 + bat_wire_d/2]) rotate([-90*sg,0,0])
            rotate([0,0,0]) cylinder(d=bat_wire_d, h=bat_end_t, $fn=20);
    }
    // passaggio per la fascetta (sotto la cella e attraverso le pareti), nel tratto dietro la millefori
    translate([bat_x - bat_xo - 1, tie_y - tie_w/2, sp_top - tie_d])
        cube([2*bat_xo + 2, tie_w, tie_d + bat_lift + 0.5]);
}
