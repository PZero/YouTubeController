#!/usr/bin/env python3
"""Cerca parti nel catalogo JLCPCB (API pubblica del sito). Uso: jlc_cerca.py "parola chiave" [N]"""
import json, sys, urllib.request
def cerca(k, n=8):
    req = urllib.request.Request(
        "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList",
        data=json.dumps({"currentPage": 1, "pageSize": n, "keyword": k, "searchSource": "search"}).encode(),
        headers={"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    for c in d["data"]["componentPageInfo"]["list"]:
        p = c.get("componentPrices") or [{}]
        print(c.get("componentCode"), c.get("componentLibraryType"), c.get("componentModelEn"), c.get("componentSpecificationEn"),
              "|", (c.get("describe") or "")[:60], "| stock", c.get("stockCount"), "| $", p[0].get("productPrice"))
if __name__ == "__main__":
    cerca(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8)
