// ======================================================================
//  PORTASCHEDE ("sled")  -  incluso da youtube_control.scad (NON autonomo:
//  usa i parametri comuni di scocca/fondo). Esportazione: part="sled".
// ======================================================================
//  Modulo intercambiabile avvitato al fondo dal basso (4 viti M3x8 svasate
//  autofilettanti nelle torrette sled_scr). Coordinate = quelle della scocca
//  (X larghezza, Y lunghezza, +Y retro, z=0 faccia esterna del fondo):
//  la piastra va da z = lid_t a z = lid_t + sled_t.
//
//   - ESP32-S3 SuperMini capovolta (componenti verso il fondo), tenuta da
//     2 labbri fissi sul lato antenna e 2 ganci a scatto sul lato USB-C;
//     tubetti guida per lo spillo sotto RST (e BOOT) allineati ai fori del fondo
//   - modulo TP4056 USB-C su 4 colonnine (viti M2), USB-C allineata alla presa sul retro
//   - culla per cella 18650 con sedi per contatti a piastrina/molla, fori fili, passaggi fascette
// ======================================================================

sled_c      = 0.25;    // gioco perimetrale in piu' rispetto al fondo
post_clr    = 0.5;     // gioco attorno alle torrette angolari della scocca
sled_boss_d = 7;
sled_boss_top = 9;     // quota assoluta della cima delle torrette viti (vite M3x8 dal basso)
sp_top      = lid_t + sled_t;          // faccia superiore della piastra

// ---------------- ESP32-S3 SuperMini (quote: dimensioni.md) ----------------
sm_l    = 23.5;  sm_w = 18;
sm_t    = 1.0;             // spessore PCB (da misurare)
sm_rst  = [8.6, 4.45];     // centro tasto RST (X,Y) nel riferimento Nologo, lato componenti (+-0.3)
sm_boot = [8.6, 13.5];     // centro tasto BOOT
sm_usb_w = 8.94;  sm_usb_l = 7.35;  sm_usb_h = 3.2;  sm_usb_out = 1.2;   // USB-C (sporgenza 1.2-2.2: misurare)
sm_gap  = 5.0;             // faccia componenti (verso il basso) sopra la piastra
sm_c    = 0.2;             // gioco PCB / incastri
sm_end  = 2.5;             // lunghezza degli incastri lungo i lati corti (fuori dalla USB-C e dai pin)
sm_ledge = 0.7;            // appoggio sotto il PCB (prima dei pad dei pin, X<0.84)
sm_clip_t = 0.8;           // spessore ganci flessibili (lato USB); PLA: deformazione ~1.3 % (era ~2.1 %)
sm_barb = 0.4;             // dente dei ganci
sm_lip  = 0.6;             // labbro fisso (lato antenna)
// origine (angolo lato USB / fila 5V) in coordinate scocca: il tasto RST cade su rst_xy
// scheda capovolta: X scheda -> +Y scocca, Y scheda -> +X scocca
sm_o    = [rst_xy.x - sm_rst.y, rst_xy.y - sm_rst.x];
sm_zf   = sp_top + sm_gap;     // faccia componenti
sm_zb   = sm_zf + sm_t;        // retro (verso l'alto)
tube_od = 3.4;  tube_id = 1.6;  tube_clr = 1.6;   // tubetto guida spillo (cima sotto i componenti SMD)
plug_ch = 1.2;             // canalino nella piastra davanti alla USB-C (spina del cavo per il primo flash)

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
tie_w = 4.5;  tie_d = 1.5; // fascette (alternativa ai contatti / ritegno cella)
bat_r   = bat_d/2 + bat_clr;
bat_lin = bat_len + bat_allow;
bat_lc  = bat_lin + 2*bat_end_t;
bat_zc  = sp_top + bat_lift + bat_d/2;
bat_xo  = bat_r + bat_wall;                // semilarghezza esterna culla
bat_y1  = bat_y0 + bat_lc;                 // faccia posteriore della testata posteriore
bat_head_top = bat_zc + ct_h/2 + 0.5;      // quota della cima delle testate

// ---------------- Modulo vibrazione (dimensioni.md: 21 x 23 x 5 con motore) ----------------
// Dal 2026-10-14 il modulo e' sotto la faccia superiore della scocca (youtube_control.scad, vt_*): qui restano
// solo le quote vib_w/h/t e la variante sul portaschede (vib_on = false), che fissa anche la posizione della millefori.
// In piedi dietro la culla 18650: il retro piatto del PCB appoggia sulla testata posteriore della culla
// (accoppiamento rigido culla -> piastra -> fondo -> scocca), lato motore verso il retro, premuto da
// nervature schiacciabili. Lato dei pin (21) in alto: pad dei fili accessibili. Nessuna vite.
// La zona e' a >25 mm dall'antenna della SuperMini.
vib_on  = false;           // SCARTATO 2026-10-14: il modulo vibrazione sta ora sotto la faccia superiore (vt_*)
vib_w   = vt_w;  vib_h = vt_h;  vib_t = vt_t;     // lato pin (orizzontale, in alto), altezza, spessore max (A)
vib_c   = 0.2;             // gioco per lato in larghezza; gioco in spessore prima delle nervature
vib_rib = 0.35;            // nervature schiacciabili sul lato motore (interferenza = vib_rib - vib_c = 0.15, PLA)
vib_rib_x = [-7.5, -2.5, 2.5, 7.5];   // posizione nervature (posizione del motore sul PCB non nota)
vib_x   = 9.2;             // centro in X: parete destra a ~0.3 dai bracci a scatto dei pannelli (X=21.25)
vib_z0  = 11.0;            // appoggio del bordo inferiore (sotto: tunnel per il filo + della cella, Z 5.8-11)
vib_hold = 12.0;           // altezza delle pareti sopra l'appoggio
vib_wall = 1.0;  vib_back = 1.2;   // pareti laterali / parete posteriore
vib_ledge = 2.0;           // larghezza appoggi sotto gli angoli del PCB
vib_top_contact = false;   // ALTERNATIVA: la parete posteriore sale fino a toccare la faccia superiore
vib_top_gap = 0.2;         //   (vibrazione trasmessa anche direttamente al coperchio); gioco residuo
vib_y0  = bat_y1;                              // faccia del PCB (retro piatto) = testata della culla
vib_y1  = vib_y0 + vib_t + vib_c;              // faccia interna della parete posteriore
vib_xi  = [vib_x - vib_w/2 - vib_c, vib_x + vib_w/2 + vib_c];   // facce interne delle pareti laterali

// ---------------- Schedina millefori di interfaccia (dimensioni.md: ~30 x 20, affid. C) ----------------
// In piedi (20 in X, 30 in Z) dietro al modulo vibrazione, in 2 guide a slitta: si infila dall'alto.
// Lato componenti verso il davanti (verso il modulo vibrazione), lato saldature verso la parete posteriore.
mf_on   = true;
mf_w    = 20;  mf_h = 30;  mf_t = 1.6;          // larghezza (X), altezza (Z), spessore PCB (C)
mf_sold = 2.0;             // sporgenza saldature sul retro (C)
mf_comp = 6.5;             // ingombro componenti sul davanti: elettrolitico 100uF COricato (Ø5-6.3);
                           // parti piu' alte (testata JST, ~10) solo nella fascia alta (Z > mf_hi_z)
mf_g_c  = 0.25;            // gioco della scanalatura (spessore e fondo)
mf_eng  = 1.2;             // impegno del bordo della schedina nella guida
mf_post_t = 1.2;           // spessore guida oltre la scanalatura
mf_x0   = -0.5;            // bordo sinistro della schedina
mf_z0   = 10.0;            // bordo inferiore (sopra le torrette delle viti, Z 9)
mf_post_h = 16;            // altezza guide sopra mf_z0
mf_y0   = vib_y1 + vib_back + 0.3 + mf_comp;   // faccia componenti del PCB
mf_hi_z = vib_z0 + vib_h + 0.5;                // sopra questa quota i componenti possono sporgere ~10

// ----------------------------------------------------------------------
module sled_plate2d() {
    difference() {
        rr2d(BW-2*wall-2*lid_tol-2*sled_c, BL-2*wall-2*lid_tol-2*sled_c, Rp-wall-lid_tol-sled_c);
        for (sx=[-1,1], sy=[-1,1]) translate([sx*px, sy*py]) circle(r=post_r+post_clr);
    }
}

// mappa coordinate scheda (X,Y,Z lato componenti) -> scocca, scheda capovolta
module sm_frame() multmatrix([[0,1,0,sm_o.x],[1,0,0,sm_o.y],[0,0,-1,sm_zf],[0,0,0,1]]) children();

// incastri della SuperMini (in coordinate scheda: X lungo, Y largo, Z<0 = sopra il retro)
module sm_holder() {
    hz = sm_gap;                                     // dalla piastra alla faccia componenti
    for (ya = [0, sm_w - sm_end]) {
        // lato USB (X=0): appoggio + gancio flessibile con dente
        translate([-0.01, ya, 0.01]) cube([sm_ledge, sm_end, hz]);          // appoggio (Z da 0 a +hz, verso la piastra)
        translate([-sm_c - sm_clip_t, ya, -sm_t - 1.4]) cube([sm_clip_t, sm_end, hz + sm_t + 1.4]);
        translate([-sm_c, ya + sm_end, -sm_t - 0.1]) rotate([90,0,0])
            linear_extrude(sm_end) polygon([[0,0],[sm_barb+sm_c,0],[0,-1.3]]);
        // lato antenna (X=sm_l): appoggio + labbro fisso + guida laterale
        translate([sm_l - sm_ledge, ya, 0.01]) cube([sm_ledge + 0.01, sm_end, hz]);
        translate([sm_l + sm_c, ya, -sm_t - 1.1]) cube([1.4, sm_end, hz + sm_t + 1.1]);
        translate([sm_l + sm_c - sm_lip - sm_c, ya, -sm_t - 1.1]) cube([sm_lip + sm_c + 0.01, sm_end, 1.0]);
    }
    // guide laterali (solo vicino al lato antenna, oltre i pad)
    for (s = [[-sm_c - 1.2, 0], [sm_w + sm_c, 1]])
        translate([sm_l - 0.6, s[0], -sm_t - 1.1]) cube([0.6 + sm_c + 1.4, 1.2, hz + sm_t + 1.1]);
}

module sled() {
    difference() {
        union() {
            translate([0,0,lid_t]) linear_extrude(sled_t) sled_plate2d();
            // torrette viti dal fondo
            for (p = sled_scr) translate([p.x, p.y, lid_t]) cylinder(d=sled_boss_d, h=sled_boss_top - lid_t, $fn=40);
            // SuperMini
            sm_frame() sm_holder();
            // tubetti guida spillo
            for (p = boot_hole ? [rst_xy, boot_xy] : [rst_xy])
                translate([p.x, p.y, sp_top - 0.01]) cylinder(d=tube_od, h=sm_gap - tube_clr + 0.01, $fn=32);
            // TP4056: colonnine
            for (h = tp_holes) translate([h.x, h.y, sp_top - 0.01]) cylinder(d=tp_so_d, h=tp_zb - sp_top + 0.01, $fn=32);
            // culla 18650
            bat_cradle_solid();
            if (vib_on) vib_holder();
            if (mf_on)  mf_guides();
        }
        if (vib_on) vib_cuts();
        // fori pilota viti fondo (dal basso)
        for (p = sled_scr) translate([p.x, p.y, lid_t - 0.01]) cylinder(d=pilot_d, h=sled_boss_top - lid_t - 0.8, $fn=24);
        // fori spillo con imbocco svasato
        for (p = boot_hole ? [rst_xy, boot_xy] : [rst_xy]) translate([p.x, p.y, 0]) {
            cylinder(d=tube_id, h=sm_zf, $fn=24);
            translate([0,0,lid_t - 0.01]) cylinder(d1=3.6, d2=tube_id, h=1.4, $fn=32);
        }
        // fori pilota TP4056
        for (h = tp_holes) translate([h.x, h.y, sp_top]) cylinder(d=tp_pilot, h=tp_zb, $fn=20);
        // canalino per la spina USB-C della SuperMini (primo flash con il fondo estratto)
        translate([sm_o.x + sm_end + 0.3, -BL, sp_top - plug_ch])
            cube([sm_w - 2*sm_end - 0.6, BL + sm_o.y - 0.5, plug_ch + 0.01]);
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

// ---------------- sede modulo vibrazione ----------------
module vib_holder() {
    ztop = vib_z0 + vib_hold;
    // pareti laterali (dalla piastra) e parete posteriore
    for (xs = [[vib_xi[0] - vib_wall, vib_xi[0]], [vib_xi[1], vib_xi[1] + vib_wall]])
        translate([xs[0], vib_y0 - 0.01, sp_top - 0.01]) cube([vib_wall, vib_y1 - vib_y0 + vib_back + 0.01, ztop - sp_top]);
    translate([vib_xi[0] - vib_wall, vib_y1, sp_top - 0.01]) cube([vib_xi[1] - vib_xi[0] + 2*vib_wall, vib_back, ztop - sp_top]);
    // alternativa: parete posteriore fino alla faccia superiore (taglio inclinato come il piano)
    if (vib_top_contact)
        intersection() {
            translate([vib_xi[0] - vib_wall, vib_y1, ztop - 0.01]) cube([vib_xi[1] - vib_xi[0] + 2*vib_wall, vib_back, 60]);
            top_frame() translate([-BW, -BL, -wall - vib_top_gap - 100]) cube([2*BW, 2*BL, 100]);
        }
    // appoggi sotto gli angoli del PCB
    for (s = [0, 1]) translate([s == 0 ? vib_xi[0] - 0.01 : vib_xi[1] - vib_ledge + 0.01, vib_y0 - 0.01, vib_z0 - 1.2])
        cube([vib_ledge, vib_y1 - vib_y0 + 0.02, 1.2]);
    // nervature schiacciabili sul lato motore
    for (dx = vib_rib_x) translate([vib_x + dx - 0.6, vib_y1 - vib_rib, vib_z0 + 1]) cube([1.2, vib_rib + 0.01, vib_hold - 1]);
}
module vib_cuts() {
    // finestra nella parete sinistra: il filo + della cella esce dalla testata e corre verso il TP4056
    translate([vib_xi[0] - vib_wall - 1, vib_y0 + 0.01, sp_top]) cube([vib_wall + 2, vib_y1 - vib_y0 - 0.02, vib_z0 - 1.2 - sp_top - 0.6]);
}

// ---------------- guide schedina millefori ----------------
module mf_guides() {
    gw = mf_t + 2*mf_g_c;                      // larghezza scanalatura
    yd = mf_y0 - mf_g_c - mf_post_t;           // fronte delle guide
    dp = gw + 2*mf_post_t;                     // profondita' guide (Y)
    for (s = [0, 1]) {
        xo = s == 0 ? mf_x0 - mf_g_c - mf_post_t : mf_x0 + mf_w - mf_eng;   // bordo sinistro della guida
        wx = mf_post_t + mf_g_c + mf_eng;
        difference() {
            translate([xo, yd, sp_top - 0.01]) cube([wx, dp, mf_z0 + mf_post_h - sp_top]);
            // scanalatura (chiusa in basso a mf_z0: appoggio della schedina)
            translate([s == 0 ? mf_x0 - mf_g_c : mf_x0 + mf_w - mf_eng - 1, mf_y0 - mf_g_c, mf_z0])
                cube([mf_eng + mf_g_c + 1, gw, 40]);
            // invito in cima
            translate([xo - 1, mf_y0 + mf_t/2, mf_z0 + mf_post_h]) rotate([45,0,0]) cube([wx + 2, 1.2, 1.2], center=true);
        }
    }
    // traversino tra le due guide sotto la schedina (irrigidisce, appoggio continuo)
    translate([mf_x0, mf_y0 - mf_g_c - mf_post_t, sp_top - 0.01]) cube([mf_w, gw + 2*mf_post_t, 1.6]);
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
    // passaggi per 2 fascette (sotto la cella e attraverso le pareti)
    for (f = [0.3, 0.7])
        translate([bat_x - bat_xo - 1, bat_y0 + f*bat_lc - tie_w/2, sp_top - tie_d])
            cube([2*bat_xo + 2, tie_w, tie_d + bat_lift + 0.5]);
}
