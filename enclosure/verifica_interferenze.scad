// ======================================================================
//  VERIFICA INTERFERENZE (non e' un pezzo da stampare)
//  Per ogni chk = 1..15 esporta l'intersezione tra gruppi di pezzi/componenti:
//    openscad -o chkN.stl -D chk=N verifica_interferenze.scad
//  Esito atteso: "Current top level object is empty" oppure volume 0 (solo facce a contatto:
//  chk 4, 7, 8, 14). Eccezione voluta: chk 12 = ~8 mm3 (nervature schiacciabili sul motore vibrazione).
//  Gli inviluppi (encoder_env, button_env, led_ring_env, vib_env, mf_env) stanno in componenti.scad.
// ======================================================================
include <youtube_control.scad>
mode = "none";
chk = 1;
module enc() top_frame() translate([K.x,K.y,0]) encoder_env();
module btn() top_frame() translate([B.x,B.y,0]) button_env();
module cell() battery_model();
module elec() { sm_frame() supermini_model(); tp4056_model(); }
module knobw() top_frame() translate([K.x,K.y,knob_gap]) knob();
module capw()  top_frame() translate([B.x,B.y,cap_z0]) cap();
module capp()  top_frame() translate([B.x,B.y,cap_z0-btn_travel]) cap();
module collw() if (!led_ring) top_frame() translate([K.x,K.y,0]) collar();
module ring()  top_frame() translate([K.x,K.y,0]) led_ring_env();
module diffw() top_frame() translate([K.x,K.y,0]) diffuser();
module vib()   vib_env();
module mf()    mf_env();
module newp()  { ring(); vib(); mf(); }
module ringx() top_frame() translate([K.x,K.y,0]) led_ring_model();   // modello (LED reali, non inviluppo)
if (chk==1)  intersection() { body(); union() { sled(); cell(); elec(); mf(); } }
if (chk==2)  intersection() { btn();  union() { sled(); cell(); elec(); body(); newp(); } }
if (chk==3)  intersection() { enc();  union() { sled(); cell(); elec(); body(); knobw(); collw(); newp(); } }
if (chk==4)  intersection() { union() { cell(); elec(); } sled(); }
if (chk==5)  intersection() { union() { capw(); capp(); } union() { body(); btn(); } }
if (chk==6)  intersection() { body(); on_walls() panel_local(); }
if (chk==7)  intersection() { sled(); lid(); }
if (chk==8)  intersection() { body(); lid(); }
if (chk==9)  intersection() { union() {knobw(); collw();} body(); }
// nuovi
if (chk==10) intersection() { ringx(); union() { body(); sled(); cell(); elec(); vib(); mf(); knobw(); diffw(); } }
if (chk==11) intersection() { vib(); union() { body(); cell(); elec(); mf(); } }
if (chk==12) intersection() { vib(); sled(); }
if (chk==13) intersection() { mf(); union() { sled(); cell(); elec(); } }
if (chk==14) intersection() { diffw(); union() { body(); knobw(); } }
if (chk==15) intersection() { on_walls() panel_local(); union() { sled(); cell(); newp(); } }
