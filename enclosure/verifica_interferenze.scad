// ======================================================================
//  VERIFICA INTERFERENZE (non e' un pezzo da stampare)
//  Per ogni chk = 1..20 esporta l'intersezione tra gruppi di pezzi/componenti:
//    openscad -o chkN.stl -D chk=N verifica_interferenze.scad
//  Esito atteso: "Current top level object is empty" oppure volume 0 (solo facce a contatto:
//  chk 4, 7, 8, 14). Eccezione voluta: chk 11 = piccole nervature di pinzatura del modulo vibrazione
//  (pinch 0,15 mm sui labbri). chk 19 (radici dei ganci nella parete) = solo contatto.
//  Gli inviluppi (encoder_env, led_ring_env, vib_top_env, mf_env) stanno in componenti.scad.
//  Pulsante PBS-110 eliminato il 2026-10-14: chk 2 e 5 (pulsante e cappuccio) ora sono il modulo vibrazione.
// ======================================================================
include <youtube_control.scad>
mode = "none";
chk = 1;
module enc() top_frame() translate([K.x,K.y,0]) encoder_env();
module cell() battery_model();
module elec() { sm_frame() supermini_model(); tp4056_model(); }
module knobw() top_frame() translate([K.x,K.y,knob_gap]) knob();
module knobp() top_frame() translate([K.x,K.y,knob_gap - enc_travel]) knob();   // manopola a fine corsa del pulsante
module collw() if (!led_ring) top_frame() translate([K.x,K.y,0]) collar();
module ring()  top_frame() translate([K.x,K.y,0]) led_ring_env();
module diffw() top_frame() translate([K.x,K.y,0]) diffuser();
module vt()    top_frame() vib_top_env();
module vtp()   top_frame() vib_top_pcb();
module mf()    mf_env();
module newp()  { ring(); vt(); mf(); }
module ringx() top_frame() translate([K.x,K.y,0]) led_ring_model();   // modello (LED reali, non inviluppo)
module ring_feat() top_frame() translate([K.x,K.y,0]) { lr_arms(); lr_stops(); lr_pockets(); }
module encm()  top_frame() translate([K.x,K.y,0]) encoder_model();      // modello (dado, bussola, albero)
if (chk==1)  intersection() { body(); union() { sled(); cell(); elec(); mf(); } }
if (chk==2)  intersection() { vt();  union() { sled(); cell(); elec(); mf(); ring(); enc(); } }   // modulo vibrazione vs resto
if (chk==3)  intersection() { enc();  union() { sled(); cell(); elec(); body(); knobw(); collw(); newp(); } }
if (chk==4)  intersection() { union() { cell(); elec(); } sled(); }
if (chk==5)  intersection() { vt(); knobw(); }
if (chk==6)  intersection() { body(); on_walls() panel_local(); }
if (chk==7)  intersection() { sled(); lid(); }
if (chk==8)  intersection() { body(); lid(); }
if (chk==9)  intersection() { union() {knobw(); collw();} body(); }
// nuovi
if (chk==10) intersection() { ringx(); union() { body(); sled(); cell(); elec(); vt(); mf(); knobw(); diffw(); } }
if (chk==11) intersection() { vtp(); body(); }                         // solo PCB vs scocca: nervature di pinzatura (voluto, ~3 mm3)
if (chk==20) intersection() { vt(); body(); }                          // PCB + motore vs scocca: i labbri coprono 1,0 del bordo: nessun componente entro 1,0 dal bordo (~24 mm3 = solo labbri)
if (chk==12) intersection() { vt(); union() { sled(); cell(); elec(); mf(); lid(); } }
if (chk==13) intersection() { mf(); union() { sled(); cell(); elec(); } }
if (chk==14) intersection() { diffw(); union() { body(); knobw(); } }
if (chk==15) intersection() { on_walls() panel_local(); union() { sled(); cell(); newp(); } }
// pulsante dell'encoder: la manopola a fine corsa non deve toccare dado/bussola/anello/diffusore/faccia
module encnut() top_frame() translate([K.x,K.y,0]) {          // dado + rondella (Ø10.4) e bussola oltre la faccia; l'albero scende insieme alla manopola
    cylinder(d=10.4, h=enc_nut_t + enc_washer_t, $fn=48);
    cylinder(d=7, h=enc_bush - wall, $fn=48);
}
if (chk==16) intersection() { knobp(); union() { encnut(); body(); diffw(); ringx(); } }
// sede del modulo vibrazione: ganci/tasche dell'anello e lavorazioni vicine
if (chk==17) intersection() { top_frame() vt_nest(); union() { ring_feat(); ringx(); top_frame() translate([K.x,K.y,0]) diffuser_cut(); } }
// la sede non deve sbucare dalla scocca
if (chk==18) difference() { top_frame() vt_nest(); rbox_t(Rp, Rt, 0); }
// parte della sede dentro le pareti (radici): solo la sovrapposizione di 0,01 con la faccia
if (chk==19) intersection() { top_frame() vt_nest(); difference() { rbox_t(Rp, Rt, 0); rbox_t(Rp-wall, Rt-wall, -0.01); } }
