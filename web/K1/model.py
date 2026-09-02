"""MODEL - entiteti domena, njihova pravila i pristup bazi."""

import os
import sqlite3

PUTANJA_BAZE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baza.sqlite")

STATUSI = {
    "u_pripremi": "U pripremi",
    "potvrdjena": "Potvrdjena",
    "isporucena": "Isporucena",
}


class Proizvod:
    """Sifarnik, van master-detail veze."""

    def __init__(self, red):
        self.id = red["id"]
        self.naziv = red["naziv"]
        self.cena = red["cena"]
        self.jedinica_mere = red["jedinica_mere"]

    def u_recnik(self):
        return {
            "id": self.id,
            "naziv": self.naziv,
            "cena": self.cena,
            "jedinica_mere": self.jedinica_mere,
        }


class Stavka:
    """Detail entitet, ne postoji bez narudzbine."""

    def __init__(self, red):
        self.id = red["id"]
        self.narudzbina_id = red["narudzbina_id"]
        self.proizvod_id = red["proizvod_id"]
        self.kolicina = red["kolicina"]
        self.cena_po_komadu = red["cena_po_komadu"]
        self.proizvod_naziv = red["proizvod_naziv"]
        self.jedinica_mere = red["jedinica_mere"]

    @property
    def iznos(self):
        return round(self.kolicina * self.cena_po_komadu, 2)

    def u_recnik(self):
        return {
            "id": self.id,
            "narudzbina_id": self.narudzbina_id,
            "proizvod_id": self.proizvod_id,
            "proizvod_naziv": self.proizvod_naziv,
            "jedinica_mere": self.jedinica_mere,
            "kolicina": self.kolicina,
            "cena_po_komadu": self.cena_po_komadu,
            "iznos": self.iznos,
        }


class Narudzbina:
    """Master entitet."""

    def __init__(self, red, stavke=None):
        self.id = red["id"]
        self.broj = red["broj"]
        self.kupac = red["kupac"]
        self.datum = red["datum"]
        self.status = red["status"]
        self.stavke = stavke or []

    @property
    def broj_stavki(self):
        return len(self.stavke)

    @property
    def ukupan_iznos(self):
        return round(sum(stavka.iznos for stavka in self.stavke), 2)

    def u_recnik(self, sa_stavkama=False):
        podaci = {
            "id": self.id,
            "broj": self.broj,
            "kupac": self.kupac,
            "datum": self.datum,
            "status": self.status,
            "status_naziv": STATUSI.get(self.status, self.status),
            "broj_stavki": self.broj_stavki,
            "ukupan_iznos": self.ukupan_iznos,
        }
        if sa_stavkama:
            podaci["stavke"] = [stavka.u_recnik() for stavka in self.stavke]
        return podaci


class SukobUPodacima(Exception):
    pass


def veza():
    povezano = sqlite3.connect(PUTANJA_BAZE)
    povezano.row_factory = sqlite3.Row
    povezano.execute("PRAGMA foreign_keys = ON")  # bez ovoga CASCADE i RESTRICT ne rade
    return povezano


SEMA = """
DROP TABLE IF EXISTS stavka;
DROP TABLE IF EXISTS narudzbina;
DROP TABLE IF EXISTS proizvod;

CREATE TABLE proizvod (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    naziv         TEXT    NOT NULL,
    cena          REAL    NOT NULL,
    jedinica_mere TEXT    NOT NULL
);

CREATE TABLE narudzbina (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    broj   TEXT    NOT NULL UNIQUE,
    kupac  TEXT    NOT NULL,
    datum  TEXT    NOT NULL,
    status TEXT    NOT NULL DEFAULT 'u_pripremi'
);

CREATE TABLE stavka (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    narudzbina_id  INTEGER NOT NULL,
    proizvod_id    INTEGER NOT NULL,
    kolicina       INTEGER NOT NULL,
    cena_po_komadu REAL    NOT NULL,   -- zapamcena cena

    -- narudzbina je vlasnik stavke
    FOREIGN KEY (narudzbina_id) REFERENCES narudzbina(id) ON DELETE CASCADE,

    -- proizvod je sifarnik, ne vlasnik
    FOREIGN KEY (proizvod_id) REFERENCES proizvod(id) ON DELETE RESTRICT,

    UNIQUE (narudzbina_id, proizvod_id)
);
"""

POCETNI_PODACI = """
INSERT INTO proizvod (naziv, cena, jedinica_mere) VALUES
    ('Brasno T-500',        89.90, 'kg'),
    ('Suncokretovo ulje',  219.00, 'l'),
    ('Secer kristal',      129.50, 'kg'),
    ('Kvasac svezi',        34.00, 'pak');

INSERT INTO narudzbina (broj, kupac, datum, status) VALUES
    ('NAR-2025-0001', 'Pekara Zlatni klas',   '2025-08-04', 'isporucena'),
    ('NAR-2025-0002', 'Restoran Dunav',       '2025-08-11', 'potvrdjena'),
    ('NAR-2025-0003', 'Poslasticarnica Ras',  '2025-08-18', 'u_pripremi');

INSERT INTO stavka (narudzbina_id, proizvod_id, kolicina, cena_po_komadu) VALUES
    (1, 1, 25, 84.90),
    (1, 4,  6, 34.00),
    (2, 2, 12, 219.00),
    (3, 3,  8, 129.50);
"""


def pripremi_bazu():
    povezano = veza()
    with povezano:
        povezano.executescript(SEMA)
        povezano.executescript(POCETNI_PODACI)
    povezano.close()


def sve_narudzbine():
    povezano = veza()
    try:
        redovi = povezano.execute("SELECT * FROM narudzbina ORDER BY id").fetchall()
        return [Narudzbina(red, _stavke(povezano, red["id"])) for red in redovi]
    finally:
        povezano.close()


def narudzbina(narudzbina_id):
    povezano = veza()
    try:
        red = povezano.execute(
            "SELECT * FROM narudzbina WHERE id = ?", (narudzbina_id,)
        ).fetchone()

        if red is None:
            return None

        return Narudzbina(red, _stavke(povezano, narudzbina_id))
    finally:
        povezano.close()


def _stavke(povezano, narudzbina_id):
    redovi = povezano.execute(
        """SELECT s.*, p.naziv AS proizvod_naziv, p.jedinica_mere
             FROM stavka s JOIN proizvod p ON p.id = s.proizvod_id
            WHERE s.narudzbina_id = ?
            ORDER BY s.id""",
        (narudzbina_id,),
    ).fetchall()

    return [Stavka(red) for red in redovi]


def svi_proizvodi():
    povezano = veza()
    try:
        redovi = povezano.execute("SELECT * FROM proizvod ORDER BY naziv").fetchall()
        return [Proizvod(red) for red in redovi]
    finally:
        povezano.close()


def proizvod(proizvod_id):
    povezano = veza()
    try:
        red = povezano.execute(
            "SELECT * FROM proizvod WHERE id = ?", (proizvod_id,)
        ).fetchone()
        return Proizvod(red) if red else None
    finally:
        povezano.close()


def stavka(stavka_id):
    povezano = veza()
    try:
        red = povezano.execute(
            """SELECT s.*, p.naziv AS proizvod_naziv, p.jedinica_mere
                 FROM stavka s JOIN proizvod p ON p.id = s.proizvod_id
                WHERE s.id = ?""",
            (stavka_id,),
        ).fetchone()
        return Stavka(red) if red else None
    finally:
        povezano.close()


def broj_stavki_sa_proizvodom(proizvod_id):
    povezano = veza()
    try:
        red = povezano.execute(
            "SELECT COUNT(*) AS koliko FROM stavka WHERE proizvod_id = ?",
            (proizvod_id,),
        ).fetchone()
        return red["koliko"]
    finally:
        povezano.close()


def proizvod_vec_na_narudzbini(narudzbina_id, proizvod_id):
    povezano = veza()
    try:
        red = povezano.execute(
            "SELECT id FROM stavka WHERE narudzbina_id = ? AND proizvod_id = ?",
            (narudzbina_id, proizvod_id),
        ).fetchone()
        return red is not None
    finally:
        povezano.close()


def upisi_stavku(narudzbina_id, proizvod_id, kolicina, cena_po_komadu):
    povezano = veza()
    try:
        with povezano:
            kursor = povezano.execute(
                """INSERT INTO stavka
                        (narudzbina_id, proizvod_id, kolicina, cena_po_komadu)
                   VALUES (?, ?, ?, ?)""",
                (narudzbina_id, proizvod_id, kolicina, cena_po_komadu),
            )
        return kursor.lastrowid
    finally:
        povezano.close()


def obrisi_stavku(stavka_id):
    povezano = veza()
    try:
        with povezano:
            povezano.execute("DELETE FROM stavka WHERE id = ?", (stavka_id,))
    finally:
        povezano.close()


def obrisi_narudzbinu(narudzbina_id):
    """Stavke odlaze same, po ON DELETE CASCADE."""
    povezano = veza()
    try:
        with povezano:
            povezano.execute("DELETE FROM narudzbina WHERE id = ?", (narudzbina_id,))
    finally:
        povezano.close()


def obrisi_proizvod(proizvod_id):
    povezano = veza()
    try:
        with povezano:
            povezano.execute("DELETE FROM proizvod WHERE id = ?", (proizvod_id,))
    except sqlite3.IntegrityError:  # ON DELETE RESTRICT
        raise SukobUPodacima("Proizvod se koristi na postojecim stavkama.")
    finally:
        povezano.close()
