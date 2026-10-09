// ======================================================================
//  YOUTUBE CONTROL  -  case stampabile in 3D (OpenSCAD)
// ======================================================================
//  PEZZI (tutti nel piatto di stampa, uno accanto all'altro):
//   1  body     scocca 105x70 (3:2), piano superiore inclinato, spigoli arrotondati, finestre/condotti di
//               raffreddamento, fori manopola e pulsante, torrette viti
//   2  lid      fondo, entra nella scocca e si avvita (4x M3)
//   3  panel x2 pannelli laterali a feritoie, si incastrano a scatto
//   4  knob     manopola zigrinata (stile ottone)
//   5  collar   anello decorativo attorno alla manopola
//   6  cap      tasto Play/Pause (con flangia di ritenzione)
//   7  bracket  supporto interno del tasto (switch tattile + 2 viti M2)
//
//  COMPONENTI PREVISTI
//   - encoder rotativo tipo EC11 (bussola M7, albero 6 mm a "D")
//   - switch tattile 6x6 mm (altezza corpo 3.5, attuatore 1.4)
//   - 4x viti M3 autofilettanti (fondo)   - 2x viti M2x8 (supporto tasto)
//   - 1x vite/grano M3 (blocco manopola)
//
//  mode = "print"     -> piatto di stampa
//         "assembly"  -> tutto montato (controllo incastri)
//         "exploded"  -> vista esplosa
//  part = "all" oppure un singolo pezzo (per esportare l'STL separato)
// ======================================================================

mode          = "print";     // "print" | "assembly" | "exploded"
part          = "all";       // "all" | "body" | "lid" | "panel" | "knob" | "collar" | "cap" | "bracket"
section_view  = false;       // sezione (solo assembly/exploded)
cut_x         = 0;           // piano di sezione
engrave_text  = true;        // scritte incise sulla faccia superiore
button_glyph  = false;       // simbolo play/pause inciso sul tasto
qi_recess     = true;        // sede per bobina di ricezione Qi sul fondo
fnt           = "Liberation Sans:style=Bold";

$fn = 48;

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
qi_d     = 44;        // diametro sede bobina Qi

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
//  MANOPOLA
// ----------------------------------------------------------------------
K          = [0, 14];   // centro manopola (coordinate sul piano inclinato: x, s)
knob_d     = 32;
flutes     = 60;        // zigrinatura
knob_gap   = 1.8;       // distanza base manopola dalla faccia superiore
enc_hole   = 7.3;       // foro bussola encoder M7
enc_bush   = 6;         // lunghezza bussola filettata
enc_shaft  = 13;        // albero sopra la bussola
shaft_d    = 6.15;      // albero 6 mm + gioco
shaft_flat = 4.6;       // quota sul piatto del "D"
nut_recess_d = 13;  nut_recess_h = 1.2;
enc_end    = (enc_bush - wall) + enc_shaft;      // fine albero sopra la faccia superiore
bore_depth = enc_end - knob_gap + 0.5;
knob_h     = bore_depth + 2.5;

// anello decorativo (collar)
ring_ri = 17.3;  ring_ro = 20.5;  ring_h = 1.4;
pin_r = 18.9;  pin_d = 2.2;  pin_len = 2.0;
pin_hole_d = 2.5;  pin_hole_depth = 2.2;

// ----------------------------------------------------------------------
//  TASTO PLAY/PAUSE
// ----------------------------------------------------------------------
B          = [-10, -33];   // centro tasto (coordinate sul piano inclinato)
btn_hole_d = 16.5;
cap_head_d = 16.0;
cap_fl_d   = 19.4;  cap_fl_t = 1.2;
cap_protr  = 2.4;                    // quanto sporge dalla faccia superiore
cap_head_h = wall + cap_protr;
nub_d = 3.4;  nub_h = 0.8;
// switch tattile
sw_pocket = 6.2;  sw_body_h = 3.5;  sw_act = 1.4;
// supporto
screw_dx = 13.5;  boss_d = 5;  boss_pilot = 1.7;
br_t = 4.5;  br_l = 34;  br_w = 12;
// quote nel sistema locale del piano superiore (z=0 = faccia superiore, z<0 = verso l'interno)
z_ceil = -wall;
z_bt   = z_ceil - cap_fl_t - nub_h - sw_act;   // piano superiore del supporto
boss_h = z_ceil - z_bt;

// presa cavo (USB-C) sul retro
usb_x = 14;  usb_z = 14;  usb_w = 13;  usb_h = 7;  usb_r = 3;

// posizioni torrette fondo
px = BW/2 - Rp + post_off*cos(45);
py = BL/2 - Rp + post_off*sin(45);

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
            // torrette supporto tasto (nel sistema inclinato)
            top_frame() for (sx=[-1,1])
                translate([B.x+sx*screw_dx, B.y, z_bt])
                    cylinder(d=boss_d, h=boss_h+0.5);
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

            // tasto: foro passante + anello inciso + fori pilota viti M2
            translate([B.x, B.y, -wall-1]) cylinder(d=btn_hole_d, h=wall+2);
            translate([B.x, B.y, -0.6]) difference() {
                cylinder(d=24.4, h=1);
                translate([0,0,-0.1]) cylinder(d=22.8, h=1.2);
            }
            for (sx=[-1,1])
                translate([B.x+sx*screw_dx, B.y, z_bt-0.01])
                    cylinder(d=boss_pilot, h=boss_h+2.0, $fn=24);

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

module top_text() {
    arc_text("YOYO CONTROL", 23.4, 2.6, 90, K);
    translate([K.x+6,  K.y-23.5]) text("<< SEEK >>", size=2.6, halign="center", valign="center", font=fnt);
    translate([B.x,    B.y+14.5]) text("SELECT",     size=2.6, halign="center", valign="center", font=fnt);
    translate([B.x+14.5, B.y])    text("PLAY/PAUSE", size=2.4, halign="left",   valign="center", font=fnt);
}

// ======================================================================
//  2) FONDO
// ======================================================================
module lid() {
    difference() {
        linear_extrude(lid_t)
            rr2d(BW-2*wall-2*lid_tol, BL-2*wall-2*lid_tol, Rp-wall-lid_tol);
        for (sx=[-1,1], sy=[-1,1]) translate([sx*px, sy*py, 0]) {
            translate([0,0,-0.01]) cylinder(d=3.4, h=lid_t+0.02, $fn=32);
            translate([0,0,-0.01]) cylinder(d1=6.4, d2=3.4, h=1.7, $fn=32);   // svasatura
        }
        if (qi_recess) translate([0,0,lid_t-1.2]) cylinder(d=qi_d, h=1.3, $fn=96);
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
//  4) MANOPOLA
// ======================================================================
module D2d(d, flat) {
    intersection() {
        circle(d=d, $fn=48);
        translate([-d, -d]) square([d + (flat - d/2), 2*d]);
    }
}

module knob() {
    Rk = knob_d/2;
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
        // sede albero a "D"
        translate([0,0,-0.01]) linear_extrude(bore_depth) D2d(shaft_d, shaft_flat);
        // alloggio dado encoder
        translate([0,0,-0.01]) cylinder(d=nut_recess_d, h=nut_recess_h, $fn=64);
        // foro per grano/vite M3 (spinge sul piatto dell'albero, lato +X)
        translate([0,0,bore_depth*0.5]) rotate([0,90,0]) cylinder(d=2.8, h=Rk+1, $fn=24);
        // incisioni sul top: anelli concentrici + indicatore
        translate([0,0,knob_h-0.4]) linear_extrude(0.5) {
            for (r=[5,8.5,12]) difference() { circle(r=r+0.25); circle(r=r-0.25); }
            translate([-0.6, 12.8]) square([1.2, 2.6]);
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
        translate([pin_r*cos(a), pin_r*sin(a), -pin_len]) cylinder(d=pin_d, h=pin_len+0.1, $fn=24);
}

// ======================================================================
//  6) TASTO (z=0 = faccia inferiore della flangia)
// ======================================================================
module cap() {
    top = cap_fl_t + cap_head_h;
    difference() {
        union() {
            translate([0,0,-nub_h]) cylinder(d=nub_d, h=nub_h+0.01, $fn=32);
            cylinder(d=cap_fl_d, h=cap_fl_t, $fn=96);
            translate([0,0,cap_fl_t-0.01]) rotate_extrude($fn=96)
                polygon([[0,0],[cap_head_d/2,0],[cap_head_d/2,cap_head_h-0.8],
                         [cap_head_d/2-0.8,cap_head_h+0.01],[0,cap_head_h+0.01]]);
        }
        translate([0,0,top-0.4]) linear_extrude(0.5) {
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
//  7) SUPPORTO TASTO (piatto, tasca switch verso l'alto)
// ======================================================================
module bracket() {
    difference() {
        linear_extrude(br_t) rr2d(br_l, br_w, 3);
        translate([-sw_pocket/2, -sw_pocket/2, br_t-sw_body_h]) cube([sw_pocket, sw_pocket, sw_body_h+0.01]);
        translate([-2.2, -2.2, -0.01]) cube([4.4, 4.4, br_t]);          // piedini / fili
        for (sx=[-1,1]) translate([sx*screw_dx, 0, 0]) {
            translate([0,0,-0.01]) cylinder(d=2.4, h=br_t+0.02, $fn=24);
            translate([0,0,-0.01]) cylinder(d=4.4, h=1.5, $fn=24);       // sede testa M2
        }
        translate([-1.5, 0, -0.01]) cube([3, br_w/2+1, 1.2]);              // canale fili
    }
}

// ======================================================================
//  LAYOUT
// ======================================================================
module print_layout() {
    // scocca: ruotata in modo che il piano superiore inclinato poggi in piano sul piatto
    show("body")    rotate([180,0,0]) rotate([-tilt,0,0]) translate([0,0,-z0]) body();
    show("lid")     translate([78,0,0]) lid();
    show("knob")    translate([-28,-88,knob_h]) rotate([180,0,0]) knob();
    show("collar")  translate([15,-88,ring_h]) rotate([180,0,0]) collar();
    show("cap")     translate([58,-82,cap_fl_t+cap_head_h]) rotate([180,0,0]) cap();
    show("bracket") translate([58,-108,0]) bracket();
    show("panel") {
        translate([108,-90,0])  panel_local();
        translate([108,-130,0]) panel_local();
    }
}

module clip() {
    if (section_view)
        difference() { union() children(); translate([cut_x,-300,-100]) cube([600,600,600]); }
    else children();
}

module assembly(ex) {
    clip() {
        show("body")    body();
        show("lid")     translate([0,0,-ex]) lid();
        show("panel")   on_walls() translate([0,0,-ex]) panel_local();
        top_frame() {
            show("knob")    translate([K.x,K.y,knob_gap+2*ex]) knob();
            show("collar")  translate([K.x,K.y,ex]) collar();
            show("cap")     translate([B.x,B.y,z_ceil-cap_fl_t-ex]) cap();
            show("bracket") translate([B.x,B.y,z_bt-br_t-1.5*ex]) bracket();
        }
    }
}

if (mode == "print") print_layout();
else assembly(mode == "exploded" ? 25 : 0);
