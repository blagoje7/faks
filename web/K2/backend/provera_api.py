"""Samoprovera REST API-ja nad privremenom SQLite bazom; ne dira MySQL."""

import os
import sys
import tempfile
from datetime import date, timedelta

import app as modul_aplikacije
from database import db
from models import Narudzbina, Proizvod, Stavka

baza = os.path.join(tempfile.mkdtemp(), "provera.db")


class TestConfig:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{baza}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "provera"
    TESTING = True


app = modul_aplikacije.create_app(TestConfig)

DANAS = date.today()
JUCE = (DANAS - timedelta(days=1)).isoformat()
SUTRA = (DANAS + timedelta(days=1)).isoformat()

with app.app_context():
    db.create_all()
    db.session.add_all([
        Proizvod(naziv="Tastatura", opis="Opis", cena=8900, jedinica_mere="kom", dostupan=True),
        Proizvod(naziv="Mis", opis="Opis", cena=3450, jedinica_mere="kom", dostupan=True),
        Proizvod(naziv="Slusalice", opis="Opis", cena=12500, jedinica_mere="kom", dostupan=False),
    ])
    db.session.add(Narudzbina(
        broj="NAR-2026-0001", kupac="Milica", email="m@primer.rs",
        datum=DANAS, status="u_pripremi",
    ))
    db.session.commit()
    db.session.add(Stavka(
        narudzbina_id=1, proizvod_id=1, kolicina=2, cena_po_komadu=8500,
        proizvod_naziv="Tastatura", jedinica_mere="kom",
    ))
    db.session.commit()

klijent = app.test_client()
ukupno = 0
neuspesno = []


def proveri(opis, uslov, detalji=""):
    global ukupno
    ukupno += 1
    print(("OK   " if uslov else "PAD  ") + opis + (f"  -> {detalji}" if not uslov and detalji else ""))
    if not uslov:
        neuspesno.append(opis)


print("--- Proizvodi -----------------------------------------------")

o = klijent.get("/api/proizvodi")
proveri("GET /api/proizvodi vraca 200", o.status_code == 200, o.status_code)
proveri("sifarnik ima 3 proizvoda", len(o.json) == 3, o.json)

o = klijent.get("/api/proizvodi?samo_dostupni=1")
proveri("filter samo_dostupni izbacuje nedostupne", len(o.json) == 2, o.json)

o = klijent.get("/api/proizvodi?pretraga=TASTA")
proveri("pretraga ne razlikuje mala i velika slova", len(o.json) == 1, o.json)

o = klijent.get("/api/proizvodi?sortiranje=cena&smer=desc")
proveri("sortiranje po ceni opadajuce", o.json[0]["naziv"] == "Slusalice", o.json[0])

o = klijent.post("/api/proizvodi", json={"naziv": "Kabl", "opis": "Opis", "cena": 1200, "jedinica_mere": "kom", "dostupan": True})
proveri("POST /api/proizvodi vraca 201", o.status_code == 201, o.status_code)
kabl = o.json["id"]

o = klijent.post("/api/proizvodi", json={"naziv": "", "opis": "", "cena": -5, "jedinica_mere": "tona"})
proveri("neispravan proizvod vraca 400", o.status_code == 400, o.status_code)
proveri("greske stizu po poljima", set(o.json["greske"]) == {"naziv", "opis", "cena", "jedinica_mere"}, o.json)

o = klijent.get("/api/proizvodi/jedinice-mere")
proveri("GET /api/proizvodi/jedinice-mere vraca listu", "kom" in o.json, o.json)

print("--- Narudzbine ----------------------------------------------")

o = klijent.get("/api/narudzbine")
proveri("GET /api/narudzbine vraca 200", o.status_code == 200, o.status_code)
proveri("ukupan iznos je izracunat iz stavki", o.json[0]["ukupan_iznos"] == 17000.0, o.json[0])
proveri("broj stavki je izracunat", o.json[0]["broj_stavki"] == 1, o.json[0])
proveri("status ima citljiv naziv", o.json[0]["status_naziv"] == "U pripremi", o.json[0])

o = klijent.get("/api/narudzbine/sledeci-broj")
proveri("predlog broja nastavlja niz", o.json["broj"].endswith("-0002"), o.json)

o = klijent.get("/api/narudzbine/statusi")
proveri("GET /api/narudzbine/statusi vraca 3 statusa", len(o.json) == 3, o.json)

o = klijent.post("/api/narudzbine", json={"broj": "NAR-2026-0002", "kupac": "Stefan", "email": "s@primer.rs", "datum": JUCE, "status": "potvrdjena"})
proveri("POST /api/narudzbine vraca 201", o.status_code == 201, o.status_code)
druga = o.json["id"]

o = klijent.post("/api/narudzbine", json={"broj": "NAR-2026-0001", "kupac": "X", "email": "x@primer.rs", "datum": JUCE, "status": "u_pripremi"})
proveri("duplirani broj narudzbine vraca 400", o.status_code == 400 and "broj" in o.json["greske"], o.json)

o = klijent.post("/api/narudzbine", json={"broj": "NAR-2026-0009", "kupac": "X", "email": "x@primer.rs", "datum": SUTRA, "status": "u_pripremi"})
proveri("datum u buducnosti vraca 400", o.status_code == 400 and "datum" in o.json["greske"], o.json)

o = klijent.post("/api/narudzbine", json={"broj": "NAR-2026-0010", "kupac": "X", "email": "bez-majmuna", "datum": JUCE, "status": "u_pripremi"})
proveri("neispravna e-adresa vraca 400", o.status_code == 400 and "email" in o.json["greske"], o.json)

o = klijent.post("/api/narudzbine", json={"broj": "NAR-2026-0011", "kupac": "X", "email": "x@primer.rs", "datum": JUCE, "status": "izmisljen"})
proveri("nepostojeci status vraca 400", o.status_code == 400 and "status" in o.json["greske"], o.json)

o = klijent.get("/api/narudzbine?status=potvrdjena")
proveri("filter po statusu radi", len(o.json) == 1 and o.json[0]["status"] == "potvrdjena", o.json)

o = klijent.get("/api/narudzbine?pretraga=milica")
proveri("pretraga po kupcu radi", len(o.json) == 1, o.json)

o = klijent.get("/api/narudzbine/1")
proveri("GET /api/narudzbine/1 ugnjezdi stavke", len(o.json["stavke"]) == 1, o.json)
proveri("stavka nosi naziv proizvoda", o.json["stavke"][0]["proizvod_naziv"] == "Tastatura", o.json["stavke"][0])

o = klijent.get("/api/narudzbine/999")
proveri("nepostojeca narudzbina vraca 404 JSON", o.status_code == 404 and o.is_json, o.status_code)

print("--- Stavke --------------------------------------------------")

o = klijent.post("/api/stavke", json={"narudzbina_id": 1, "proizvod_id": 2, "kolicina": 3})
proveri("POST /api/stavke vraca 201", o.status_code == 201, o.status_code)
proveri("cena je preuzeta iz sifarnika", o.json["cena_po_komadu"] == 3450.0, o.json)
proveri("iznos je kolicina puta cena", o.json["iznos"] == 10350.0, o.json)
stavka_mis = o.json["id"]

o = klijent.post("/api/stavke", json={"narudzbina_id": 1, "proizvod_id": 2, "kolicina": 1})
proveri("isti proizvod dvaput na narudzbini vraca 400", o.status_code == 400 and "proizvod_id" in o.json["greske"], o.json)

o = klijent.post("/api/stavke", json={"narudzbina_id": 1, "proizvod_id": 3, "kolicina": 1})
proveri("nedostupan proizvod vraca 400", o.status_code == 400 and "proizvod_id" in o.json["greske"], o.json)

o = klijent.post("/api/stavke", json={"narudzbina_id": 999, "proizvod_id": 1, "kolicina": 1})
proveri("nepostojeca narudzbina u stavci vraca 400", o.status_code == 400 and "narudzbina_id" in o.json["greske"], o.json)

o = klijent.post("/api/stavke", json={"narudzbina_id": 1, "proizvod_id": 1, "kolicina": 0})
proveri("kolicina nula vraca 400", o.status_code == 400 and "kolicina" in o.json["greske"], o.json)

o = klijent.get("/api/narudzbine/1")
proveri("ukupan iznos prati dodavanje stavke", o.json["ukupan_iznos"] == 27350.0, o.json["ukupan_iznos"])

print("--- Zapamcena cena ------------------------------------------")

o = klijent.put("/api/proizvodi/2", json={"naziv": "Mis", "opis": "Opis", "cena": 9999, "jedinica_mere": "kom", "dostupan": True})
proveri("cena proizvoda je izmenjena u sifarniku", o.json["cena"] == 9999.0, o.json)

o = klijent.get("/api/narudzbine/1")
stavka = [s for s in o.json["stavke"] if s["id"] == stavka_mis][0]
proveri("izmena cenovnika ne menja zapamcenu cenu", stavka["cena_po_komadu"] == 3450.0, stavka)
proveri("izmena cenovnika ne menja iznos narudzbine", o.json["ukupan_iznos"] == 27350.0, o.json["ukupan_iznos"])

o = klijent.put(f"/api/stavke/{stavka_mis}", json={"narudzbina_id": 1, "proizvod_id": 2, "kolicina": 5})
proveri("izmena samo kolicine cuva zapamcenu cenu", o.json["cena_po_komadu"] == 3450.0, o.json)
proveri("iznos prati novu kolicinu", o.json["iznos"] == 17250.0, o.json)

o = klijent.put(f"/api/stavke/{stavka_mis}", json={"narudzbina_id": 1, "proizvod_id": kabl, "kolicina": 5})
proveri("promena proizvoda preuzima tekucu cenu", o.json["cena_po_komadu"] == 1200.0, o.json)

print("--- Premestanje i integritet --------------------------------")

o = klijent.put(f"/api/stavke/{stavka_mis}", json={"narudzbina_id": druga, "proizvod_id": kabl, "kolicina": 5})
proveri("izmena narudzbina_id premesta stavku", o.json["narudzbina_id"] == druga, o.json)

o = klijent.get(f"/api/narudzbine/{druga}")
proveri("premestena stavka je na novoj narudzbini", len(o.json["stavke"]) == 1, o.json)

o = klijent.get("/api/narudzbine/1")
proveri("stara narudzbina vise nema tu stavku", o.json["broj_stavki"] == 1, o.json)

o = klijent.delete(f"/api/proizvodi/{kabl}")
proveri("proizvod u narudzbini koja je u toku vraca 409", o.status_code == 409, o.status_code)
proveri("odgovor javlja na koliko stavki stoji", o.json["upotrebljen_na_stavki"] == 1, o.json)

o = klijent.delete("/api/proizvodi/3")
proveri("neupotrebljen proizvod se brise", o.status_code == 200, o.status_code)

o = klijent.delete("/api/narudzbine/1")
proveri("CASCADE: brisanje javlja broj obrisanih stavki", o.json["obrisano_stavki"] == 1, o.json)

with app.app_context():
    ostalo = Stavka.query.filter_by(narudzbina_id=1).count()
    proizvoda = Proizvod.query.count()
proveri("stavke obrisane narudzbine su kaskadno obrisane", ostalo == 0, ostalo)
proveri("brisanje narudzbine ne dira sifarnik", proizvoda == 3, proizvoda)

print("--- Brisanje proizvoda po statusu narudzbine -----------------")

o = klijent.post("/api/proizvodi", json={"naziv": "Podloga", "opis": "Opis", "cena": 900, "jedinica_mere": "kom", "dostupan": True})
podloga = o.json["id"]

o = klijent.post("/api/narudzbine", json={"broj": "NAR-2026-0020", "kupac": "Jelena", "email": "j@primer.rs", "datum": JUCE, "status": "isporucena"})
isporucena = o.json["id"]
o = klijent.post("/api/stavke", json={"narudzbina_id": isporucena, "proizvod_id": podloga, "kolicina": 2})
proveri("stavka na isporucenoj narudzbini je kreirana", o.status_code == 201, o.status_code)
iznos_pre = klijent.get(f"/api/narudzbine/{isporucena}").json["ukupan_iznos"]

o = klijent.post("/api/narudzbine", json={"broj": "NAR-2026-0021", "kupac": "Jelena", "email": "j@primer.rs", "datum": JUCE, "status": "potvrdjena"})
u_toku = o.json["id"]
klijent.post("/api/stavke", json={"narudzbina_id": u_toku, "proizvod_id": podloga, "kolicina": 1})

o = klijent.delete(f"/api/proizvodi/{podloga}")
proveri("proizvod i u toku i isporucen vraca 409", o.status_code == 409, o.status_code)
proveri("broje se samo stavke narudzbina u toku", o.json["upotrebljen_na_stavki"] == 1, o.json)

klijent.delete(f"/api/narudzbine/{u_toku}")

o = klijent.delete(f"/api/proizvodi/{podloga}")
proveri("proizvod samo na isporucenoj narudzbini se brise", o.status_code == 200, o.status_code)
proveri("odgovor javlja koliko je stavki zadrzano", o.json["arhivirano_stavki"] == 1, o.json)

o = klijent.get(f"/api/narudzbine/{isporucena}")
proveri("stavka isporucene narudzbine je zadrzana", len(o.json["stavke"]) == 1, o.json)
proveri("zapamcen naziv je prezivio brisanje", o.json["stavke"][0]["proizvod_naziv"] == "Podloga", o.json["stavke"][0])
proveri("stavka je oznacena kao arhivirana", o.json["stavke"][0]["arhivirana"] is True, o.json["stavke"][0])
proveri("iznos isporucene narudzbine je nepromenjen", o.json["ukupan_iznos"] == iznos_pre, o.json["ukupan_iznos"])

with app.app_context():
    veza = db.session.get(Stavka, o.json["stavke"][0]["id"]).proizvod_id
proveri("veza ka sifarniku je prekinuta", veza is None, veza)

print("--- Infrastruktura ------------------------------------------")

o = klijent.get("/api/stanje")
proveri("GET /api/stanje potvrdjuje vezu sa bazom", o.json["baza"] == "povezana", o.json)

o = klijent.get("/api/nepostojece")
proveri("nepoznata API putanja vraca JSON 404", o.status_code == 404 and o.is_json, o.status_code)

o = klijent.get("/")
proveri("/ servira izgradjeni Vue klijent", o.status_code == 200 and b'<div id="app">' in o.data, o.status_code)

o = klijent.get("/narudzbine/5/izmeni")
proveri("duboka putanja vraca index.html za Vue Router", o.status_code == 200 and b'<div id="app">' in o.data, o.status_code)

print()
if neuspesno:
    print(f"NEUSPESNO: {len(neuspesno)} od {ukupno}")
    for opis in neuspesno:
        print(f"  - {opis}")
    sys.exit(1)
print(f"Sve provere su prosle: {ukupno} od {ukupno}.")
