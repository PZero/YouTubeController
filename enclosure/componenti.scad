// ======================================================================
//  COMPONENTI  -  modelli SEMPLIFICATI, solo per visualizzazione e controllo
//  interferenze. Inclusi da youtube_control.scad; mai nei piatti di stampa.
// ======================================================================

c_pcb_sm = "#1d2f6b";   c_pcb_tp = "#2a62c9";   c_metal = "#d0d3d6";
c_chip   = "#222222";   c_bat    = "#6b3fa0";   c_green = "#2f7d4a";
c_black  = "#151515";   c_key    = "#1f5fd6";

// encoder EC11E (sistema locale del piano superiore, origine sull'asse alla faccia superiore)
enc_body = [12, 11.6];  enc_body_h = 6.5;  enc_pin_h = 3.5;  enc_pin_x = [-7.5, 7.0];
module encoder_model(exploded=false) {
    zs = -wall;                                        // piano di appoggio = faccia interna
    color(c_metal) {
        translate([0,0,zs]) cylinder(d=7, h=enc_bush, $fn=32);                       // bussola M7
        translate([0,0,zs+enc_bush]) linear_extrude(enc_shaft) knurl2d(0);            // albero zigrinato
        translate([-enc_body.x/2, -enc_body.y/2, zs-enc_body_h+1.5])
            cube([enc_body.x, enc_body.y, enc_body_h-1.5]);                            // calotta metallica
        translate([0,0,exploded ? enc_bush+2 : 0]) difference() {                      // dado M7 + rondella
            cylinder(d=10.4, h=2.0, $fn=6);
            translate([0,0,-1]) cylinder(d=7, h=4);
        }
        for (i=[0:2]) translate([enc_pin_x[0], -2.5+i*2.5, zs-enc_body_h-enc_pin_h])
            cube([0.8, 0.4, enc_pin_h+0.1], center=false);
        for (i=[0:1]) translate([enc_pin_x[1], -2.5+i*5, zs-enc_body_h-enc_pin_h])
            cube([0.8, 0.4, enc_pin_h+0.1]);
    }
    color(c_green) translate([-enc_body.x/2, -enc_body.y/2, zs-enc_body_h]) cube([enc_body.x, enc_body.y, 1.5]);
}
// inviluppo per i controlli: corpo + piedini + fili saldati (+3 mm)
module encoder_env() {
    translate([0,0,-wall]) cylinder(d=7, h=enc_bush);
    translate([0,0,-wall+enc_bush]) cylinder(d=5.2, h=enc_shaft);
    translate([-enc_body.x/2, -enc_body.y/2, -wall-enc_body_h]) cube([enc_body.x, enc_body.y, enc_body_h-0.01]);
    translate([-8.5, -enc_body.y/2, -wall-enc_body_h-enc_pin_h-3]) cube([17, enc_body.y, enc_pin_h+3]);
}

// modulo vibrazione sulla faccia superiore (sistema del piano superiore, origine su x=0, s=0, z=0 faccia esterna)
// PCB con il retro piatto contro la faccia interna; motore e componenti verso l'interno; pin verso l'encoder (+s)
module vib_top_model() {
    color(c_green) translate([-vt_w/2, vt_sf, vt_zp]) cube([vt_w, vt_h, vt_pcb_t]);
    color(c_metal) translate([0, vt_sf + vt_h/2, vt_zp - (vt_t - vt_pcb_t)]) cylinder(d=10, h=vt_t - vt_pcb_t, $fn=40);
    color(c_chip) translate([-8, vt_sb - 6, vt_zp - 1.2]) cube([3, 3, 1.2]);
}
module vib_top_env() translate([-vt_w/2, vt_sf, vt_zp - (vt_t - vt_pcb_t)]) cube([vt_w, vt_h, vt_t]);
module vib_top_pcb() translate([-vt_w/2, vt_sf, vt_zp]) cube([vt_w, vt_h, vt_pcb_t]);   // solo il PCB (senza motore e componenti)

// ESP32-S3 SuperMini (coordinate scheda, Z>0 = lato componenti)
module supermini_model() {
    color(c_pcb_sm) translate([0,0,-sm_t]) linear_extrude(sm_t) rr2d_c(sm_l, sm_w, 1);
    color(c_metal) translate([-sm_usb_out, sm_w/2 - sm_usb_w/2, 0]) cube([sm_usb_l, sm_usb_w, sm_usb_h]);
    color(c_chip) translate([15.3, 9, 0]) rotate(45) translate([-3.5,-3.5,0]) cube([7, 7, 0.9]);
    color("white") translate([21.2, 7.9, 0]) cube([2.2, 7, 1]);                 // antenna ceramica
    color(c_metal) for (p=[sm_rst, sm_boot]) translate([p.x-1.5, p.y-1, 0]) cube([3, 2, 0.6]);
    color("gold") for (i=[0:8], y=[1.38, 16.62]) translate([1.59+i*2.54, y, -sm_t-0.05]) cylinder(d=1.5, h=sm_t+0.1, $fn=12);
}
module rr2d_c(l, w, r) translate([l/2, w/2]) rr2d(l, w, r);

// modulo TP4056 (coordinate scocca)
module tp4056_model() {
    x0 = usb_x - tp_w/2;  y0 = tp_y1 - tp_l;
    difference() {
        color(c_pcb_tp) translate([x0, y0, tp_zb]) cube([tp_w, tp_l, tp_t]);
        for (h = tp_holes) translate([h.x, h.y, tp_zb-1]) cylinder(d=1.8, h=4, $fn=16);
    }
    color(c_metal) translate([usb_x - 4.47, tp_y1 + tp_usb_out - 7.35, tp_zb+tp_t]) cube([8.94, 7.35, 3.2]);
    color(c_chip) translate([usb_x - 2.5, y0 + 8, tp_zb+tp_t]) cube([5, 4, 1.5]);
    color("red")  translate([usb_x + 4.5, y0 + 15, tp_zb+tp_t]) cube([1.6, 0.8, 0.6]);
    color("blue") translate([usb_x + 4.5, y0 + 13, tp_zb+tp_t]) cube([1.6, 0.8, 0.6]);
}

// cella 18650 + contatti (coordinate scocca)
module battery_model() {
    yi0 = bat_y0 + bat_end_t;
    yb  = yi0 + 1.0;                                                  // lato piastrina (polo -)
    color(c_bat) translate([bat_x, yb, bat_zc]) rotate([-90,0,0]) cylinder(d=bat_d, h=bat_len - 1, $fn=64);
    color(c_metal) translate([bat_x, yb + bat_len - 1, bat_zc]) rotate([-90,0,0]) cylinder(d=7, h=1, $fn=32);
    color(c_metal) {
        translate([bat_x - ct_w/2, yi0 - ct_lip - ct_t - 0.15, bat_zc - ct_h/2]) cube([ct_w, ct_t, ct_h]);
        translate([bat_x - ct_w/2, yi0 + bat_lin + ct_lip + 0.15, bat_zc - ct_h/2]) cube([ct_w, ct_t, ct_h]);
        translate([bat_x, yi0 + bat_lin + ct_lip, bat_zc]) rotate([90,0,0])
            cylinder(d1=6.5, d2=4, h=bat_allow - 1 + ct_lip, $fn=24);     // molla (compressa)
    }
}

module sled_electronics() {
    sm_frame() supermini_model();
    tp4056_model();
    battery_model();
    tp_screws_model();
    if (vib_on) vib_model();
    if (mf_on)  mf_model();
}

// anello LED WS2812B 16 LED (sistema del piano superiore, origine sull'asse K, z=0 faccia superiore)
c_led = "#f4f4ec";
module led_ring_model() {
    color(c_black) translate([0,0,lr_nb]) difference() {
        cylinder(d=lr_do, h=lr_pcb_t, $fn=96);
        translate([0,0,-1]) cylinder(d=lr_di, h=lr_pcb_t+2, $fn=96);
    }
    color(c_led) for (i=[0:lr_n-1]) rotate(lr_pad_ang + 180/lr_n + i*360/lr_n)
        translate([lr_led_r - lr_led/2, -lr_led/2, lr_nt]) cube([lr_led, lr_led, lr_t - lr_pcb_t]);
    // piazzole con saldature sporgenti (arco lr_pad_arc) e 3 fili che scendono
    color(c_metal) for (j=[0:5]) rotate(lr_pad_ang - lr_pad_arc/2 + (j+0.5)*lr_pad_arc/6)
        translate([lr_pad_r, 0, lr_nb - lr_solder]) cylinder(d=2, h=lr_solder+0.01, $fn=12);
    for (j=[0:2]) rotate(lr_pad_ang + lr_pad_arc/2 - (j+0.5)*lr_pad_arc/6)
        color(["#202020","#2a7ad8","#d02a2a"][j]) translate([lr_pad_r, 0, lr_nb - lr_solder - 3]) cylinder(d=1.2, h=3, $fn=8);   // solo il primo tratto
}
// inviluppo per i controlli: PCB + LED + saldature (solo nell'arco piazzole)
module led_ring_env() {
    translate([0,0,lr_nb]) difference() {
        cylinder(d=lr_do, h=lr_t, $fn=96);
        translate([0,0,-1]) cylinder(d=lr_di, h=lr_t+2, $fn=96);
    }
    intersection() {
        translate([0,0,lr_nb - lr_solder - 3]) difference() {
            cylinder(r=lr_pad_r + 1.5, h=lr_solder + 3.01, $fn=96);
            translate([0,0,-1]) cylinder(r=lr_pad_r - 1.5, h=lr_solder + 6, $fn=96);
        }
        rotate(lr_pad_ang - lr_pad_arc/2) rotate_extrude(angle=lr_pad_arc) square([40, 40]);
    }
}

// [VARIANTE SCARTATA 2026-10-14, vib_on = false] modulo vibrazione sul portaschede: PCB in piedi contro la culla
module vib_model() {
    color(c_green) translate([vib_x - vt_w/2, vib_y0, vib_z0]) cube([vt_w, 1.6, vt_h]);
    color(c_metal) translate([vib_x, vib_y0 + 1.6, vib_z0 + vt_h/2]) rotate([-90,0,0]) cylinder(d=10, h=vib_t - 1.6, $fn=40);
    color(c_chip) translate([vib_x - 8, vib_y0 + 1.6, vib_z0 + vt_h - 6]) cube([3, 1.2, 3]);
}
module vib_env() translate([vib_x - vt_w/2, vib_y0, vib_z0]) cube([vt_w, vib_t, vt_h]);

// schedina millefori (coordinate scocca) con testata JST-PH (da definire: 3 o 8 poli)
jst_n = 8;                                 // poli della testata sulla schedina (3 = solo anello; 8 = tutto il coperchio)
jst_w = 2.0*(jst_n-1) + 3.9;  jst_d = 4.5;  jst_h = 6.0;   // B?B-PH-K-S (passo 2.0); +~4 spina e fili
module mf_model() {
    color("#c8a95a") translate([mf_x0, mf_y0, mf_z0]) cube([mf_w, mf_t, mf_h]);
    color("#2b2b2b") translate([mf_x0 + 2, mf_y0 - 5, mf_z0 + 4]) rotate([0,90,0]) cylinder(d=5, h=11, $fn=24);   // 100uF coricato
    color(c_chip) translate([mf_x0 + 14, mf_y0 - 1.2, mf_z0 + 6]) cube([3, 1.2, 3]);                              // MOSFET
    color("white") translate([mf_x0 + (mf_w - jst_w)/2, mf_y0 - jst_h, mf_z0 + mf_h - jst_d - 0.5]) cube([jst_w, jst_h, jst_d]);
}
module mf_env() {
    translate([mf_x0, mf_y0, mf_z0]) cube([mf_w, mf_t, mf_h]);
    translate([mf_x0 + mf_eng + 0.3, mf_y0 + mf_t - 0.01, mf_z0]) cube([mf_w - 2*(mf_eng + 0.3), mf_sold, mf_h]);   // saldature
    // componenti: a >= mf_eng + 0.3 dai bordi laterali (le guide impegnano il bordo)
    translate([mf_x0 + mf_eng + 0.3, mf_y0 - mf_comp, mf_z0]) cube([mf_w - 2*(mf_eng + 0.3), mf_comp + 0.01, mf_h]);
    // fascia alta: testata JST con spina inserita (~10)
    translate([mf_x0 + mf_eng + 0.3, mf_y0 - jst_h - 4, mf_hi_z]) cube([mf_w - 2*(mf_eng + 0.3), jst_h + 4, mf_z0 + mf_h - mf_hi_z]);
}

// viti principali (coordinate scocca)
module screw_m(d, l, head_d, csk=true) {
    color(c_metal) {
        if (csk) cylinder(d1=head_d, d2=d, h=(head_d-d)/2, $fn=24);
        else translate([0,0,-1.6]) cylinder(d=head_d, h=1.6, $fn=24);
        cylinder(d=d, h=l, $fn=16);
    }
}
module screws_model(ex=0) {
    for (sx=[-1,1], sy=[-1,1]) translate([sx*px, sy*py, -1.2*ex]) screw_m(3, 8, 6);
    for (p = sled_scr) translate([p.x, p.y, -0.6*ex]) screw_m(3, 8, 6);
}
module tp_screws_model() for (h = tp_holes) translate([h.x, h.y, tp_zb + tp_t]) rotate([180,0,0]) screw_m(2, 5, 3.8, false);
