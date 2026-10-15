# -*- coding: utf-8 -*-
# Serigrafia e ordine di instradamento (eseguito dentro genera_pcb.py)
ROUTE_ORDER = ["GND", "SW", "ENC_A", "ENC_B", "VIB_IN", "5V", "VBAT", "LEDP", "B_Q1", "C_Q2", "B_Q2", "GPIO9", "DI", "GPIO2", "GPIO1",
               "3V3", "GPIO8", "GPIO10", "CHRG", "STDBY"]
SILK = []

SILK = [("USB-C", 8.2, 1.9, 0, 1.0), ("YTC-IF v1", 7.8, 30.2, 0, 1.0),
        ("J1", 0.9, 34.4, 0, 0.9), ("1", 2.9, 34.9, 0, 0.8), ("2", 5.5, 34.9, 0, 0.8), ("10", 5.2, 49.4, 0, 0.8), ("9", 3.0, 49.4, 0, 0.8),
        ("J2", 5.2, 57.0, 0, 0.9),
        ("B+", 7.5, 59.1, 0, 0.8), ("B-", 10.1, 59.1, 0, 0.8), ("CH", 12.7, 59.1, 0, 0.8), ("SB", 15.2, 59.1, 0, 0.8)]
# contorno SuperMini (4,65..22,65 x 4,28..27,78), solo serigrafia
RECTS = [(4.65, 4.28, 22.4, 27.78)]
