"""Provera ulaznih podataka pre nego sto presenter dodirne model."""

from datetime import date


def tekst(podaci, polje, naziv_polja, maksimum=None):
    vrednost = (podaci.get(polje) or "").strip()

    if not vrednost:
        return None, f"{naziv_polja} je obavezan podatak."
    if maksimum and len(vrednost) > maksimum:
        return None, f"{naziv_polja} moze imati najvise {maksimum} karaktera."

    return vrednost, None


def eposta(podaci, polje, naziv_polja):
    vrednost, greska = tekst(podaci, polje, naziv_polja, maksimum=120)
    if greska:
        return None, greska

    if "@" not in vrednost or "." not in vrednost.split("@")[-1]:
        return None, f"{naziv_polja} mora biti ispravna adresa elektronske poste."

    return vrednost, None


def ceo_broj(podaci, polje, naziv_polja, minimum=None):
    vrednost = podaci.get(polje)

    if vrednost is None or vrednost == "":
        return None, f"{naziv_polja} je obavezan podatak."

    try:
        broj = int(vrednost)
    except (TypeError, ValueError):
        return None, f"{naziv_polja} mora biti ceo broj."

    if minimum is not None and broj < minimum:
        return None, f"{naziv_polja} ne moze biti manji od {minimum}."

    return broj, None


def decimalni_broj(podaci, polje, naziv_polja, minimum=None):
    vrednost = podaci.get(polje)

    if vrednost is None or vrednost == "":
        return None, f"{naziv_polja} je obavezan podatak."

    try:
        broj = float(vrednost)
    except (TypeError, ValueError):
        return None, f"{naziv_polja} mora biti broj."

    if minimum is not None and broj < minimum:
        return None, f"{naziv_polja} ne moze biti manji od {minimum}."

    return broj, None


def datum(podaci, polje, naziv_polja, bez_buducnosti=False):
    vrednost = (podaci.get(polje) or "").strip()

    if not vrednost:
        return None, f"{naziv_polja} je obavezan podatak."

    try:
        vrednost = date.fromisoformat(vrednost)
    except ValueError:
        return None, f"{naziv_polja} mora biti u obliku GGGG-MM-DD."

    if bez_buducnosti and vrednost > date.today():
        return None, f"{naziv_polja} ne moze biti u buducnosti."

    return vrednost, None


def izbor(podaci, polje, naziv_polja, dozvoljene):
    vrednost = (podaci.get(polje) or "").strip()

    if not vrednost:
        return None, f"{naziv_polja} je obavezan podatak."
    if vrednost not in dozvoljene:
        return None, f"{naziv_polja} nema dozvoljenu vrednost."

    return vrednost, None


def logicka(podaci, polje):
    return bool(podaci.get(polje)), None
