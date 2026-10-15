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
    tp4056_model();
    battery_model();
    tp_screws_model();
    if (mf_on) { mf_model(); cn_model(); }
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

// ----------------------------------------------------------------------------------------------
//  Millefori unica 8 x 20 (22,54 x 60) con la SuperMini saldata sopra: modello e inviluppi
//  (coordinate scocca; interno: sistema millefori x/y/z, z = 0 faccia inferiore del PCB)
// ----------------------------------------------------------------------------------------------
module mf_frame() translate([mf_x0, mf_y0, mf_zb]) children();
// SuperMini sulla strip: coordinate scheda (X dalla USB-C verso l'antenna, Y dalla fila 5V alla fila TX) -> millefori
module mf_sm_frame() multmatrix([[0,-1,0,mf_sm_x],[1,0,0,mf_sm_y],[0,0,1,mf_t + mf_strip_h + sm_t],[0,0,0,1]]) children();
function mf_cx(c) = mf_a1.x + c*mf_pitch;            // x del centro della colonna c (A = 0)
function mf_ry(r) = mf_a1.y + (r - 1)*mf_pitch;      // y del centro della riga r

// strip maschio 2 x 1x9 + SuperMini (insieme usato nei controlli come "scheda")
module mf_sm_all() mf_frame() {
    color("#2b2b2b") for (c = [1, 7]) translate([mf_cx(c) - 1.27, mf_ry(1) - 1.27, mf_t]) cube([2.54, 9*2.54, mf_strip_h]);
    mf_sm_frame() supermini_model();
}

// componenti dall'elenco di firmware/millefori/README.md: [colonna, riga, tipo, (colonna2, riga2)]
// tipo: "r" resistenza in piedi (Ø2.4, h10), "e" elettrolitico 5x11 a cavallo di due fori, "c" ceramico (h6), "q" TO-92, "d" diodo
mf_parts = [
    [5,15,"e",4,15],   [7,20,"e",6,20],                                      // C1, C3
    [3,15,"r"], [2,12,"r"], [4,12,"r"], [7,14,"r"], [1,16,"r"], [0,11,"r"],  // R1, R2, R3, R4, R5, R6
    [0,14,"r"], [0,18,"r"], [0,15,"r"], [7,16,"r"], [5,17,"r"],              // R7, R8, R9, R10, R11
    [0,3,"c",0,4], [7,18,"c",6,18],                                          // C2, C4
    [7,11,"d"],                                                              // D1
    [2,13,"q",4,13], [5,13,"q",7,13]                                         // Q2, Q1
];
module mf_model() {
    mf_frame() {
        color("#c8a95a") difference() {
            cube([mf_w, mf_l, mf_t]);
            for (h = mf_holes) translate([h.x, h.y, -1]) cylinder(d=mf_hole_d, h=mf_t + 2, $fn=24);
        }
        for (p = mf_parts) {
            x1 = mf_cx(p[0]);  y1 = mf_ry(p[1]);
            two = len(p) > 3;
            x2 = two ? mf_cx(p[3]) : x1;  y2 = two ? mf_ry(p[4]) : y1;
            xc = (x1 + x2)/2;  yc = (y1 + y2)/2;
            translate([xc, yc, mf_t]) {
                if (p[2] == "e") color("#2b2b2b") cylinder(d=5, h=11, $fn=24);
                if (p[2] == "r") color("#b0a080") cylinder(d=2.4, h=10, $fn=12);
                if (p[2] == "c") color("#c06020") cylinder(d=2.5, h=6, $fn=12);
                if (p[2] == "d") color("#202020") cylinder(d=2.8, h=10, $fn=12);
                if (p[2] == "q") color(c_chip) translate([-2.3, -1.8, 0]) cube([4.6, 3.6, 8]);
            }
        }
    }
    mf_sm_all();
    pk_model();
}

// inviluppo del PACCO (millefori + SuperMini + componenti + guaina), libero nella corsia: fascia sinistra bassa
// (solo PCB e saldature), corpo alto dai 2,1 mm dal bordo sinistro in poi. pk_dx/pk_dy spostano il pacco per le prove agli estremi.
module pk_env() translate([pk_x0, pk_y0, sp_top + 0.01]) {
    cube([pk_w, pk_l, pk_lo_h]);
    translate([pk_lo_w, 0, 0]) cube([pk_w - pk_lo_w, pk_l, pk_h]);
}
// guaina semitrasparente attorno al pacco (anteprima)
module pk_model() %color("#e0a030", 0.35) translate([pk_x0, pk_y0, sp_top + 0.01]) cube([pk_w, pk_l, pk_h]);
// spina USB-C normale (guscio 12 x 6,5, angoli r 2,5) infilata nella presa del TP4056 dal retro: deve passare dalla finestra 13 x 7
plug_w = 12.0;  plug_h = 6.5;  plug_len = 25;
module plug_env() translate([usb_x, tp_y1 + tp_usb_out + 0.01, usb_z]) rotate([-90,0,0]) translate([0,0,0])
    linear_extrude(plug_len) rr2d(plug_w, plug_h, 2.5);

// connettore volante (coppia innestata 2 x 5, in piedi nella tasca): ingombro con 5 mm di curvatura dei fili in alto
module cn_model() color("#d8d8d8") translate([cn_xi[0] + cn_c.x, cn_yi[0] + cn_c.y, sp_top]) cube([cn_w, cn_d, cn_h]);
module cn_env()   translate([cn_xi[0] + cn_c.x, cn_yi[0] + cn_c.y, sp_top + 0.01]) cube([cn_w, cn_d, cn_h + 5]);

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
