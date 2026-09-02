"""PRESENTER - provera ulaza, rad nad modelom, stanje i statusni kod za View"""

import model


def _stavki(koliko):
    """kolicina stavki"""
    if koliko % 10 == 1 and koliko % 100 != 11:
        return "%d stavka" % koliko
    if koliko % 10 in (2, 3, 4) and koliko % 100 not in (12, 13, 14):
        return "%d stavke" % koliko
    return "%d stavki" % koliko


def _ceo_broj(podaci, polje, naziv, minimum=None):
    vrednost = podaci.get(polje)

    if vrednost is None or vrednost == "":
        return None, "%s je obavezno polje." % naziv

    try:
        broj = int(vrednost)
    except (TypeError, ValueError):
        return None, "%s mora biti ceo broj." % naziv

    if minimum is not None and broj < minimum:
        return None, "%s mora biti najmanje %d." % (naziv, minimum)

    return broj, None


def lista_narudzbina():
    narudzbine = model.sve_narudzbine()
    return {"narudzbine": [jedna.u_recnik() for jedna in narudzbine]}, 200


def jedna_narudzbina(narudzbina_id):
    narudzbina = model.narudzbina(narudzbina_id)

    if narudzbina is None:
        return {"poruka": "Trazena narudzbina ne postoji."}, 404

    return narudzbina.u_recnik(sa_stavkama=True), 200


def lista_proizvoda():
    proizvodi = model.svi_proizvodi()
    return {"proizvodi": [jedan.u_recnik() for jedan in proizvodi]}, 200


def dodaj_stavku(podaci):
    greske = {}

    narudzbina_id, greska = _ceo_broj(podaci, "narudzbina_id", "Narudzbina")
    if greska:
        greske["narudzbina_id"] = greska
    elif model.narudzbina(narudzbina_id) is None:
        greske["narudzbina_id"] = "Izabrana narudzbina ne postoji."

    proizvod = None
    proizvod_id, greska = _ceo_broj(podaci, "proizvod_id", "Proizvod")
    if greska:
        greske["proizvod_id"] = greska
    else:
        proizvod = model.proizvod(proizvod_id)
        if proizvod is None:
            greske["proizvod_id"] = "Izabrani proizvod ne postoji."

    kolicina, greska = _ceo_broj(podaci, "kolicina", "Kolicina", minimum=1)
    if greska:
        greske["kolicina"] = greska

    if not greske and model.proizvod_vec_na_narudzbini(narudzbina_id, proizvod_id):
        greske["proizvod_id"] = (
            "Taj proizvod vec stoji na ovoj narudzbini. Obrisite postojecu "
            "stavku pa je unesite ponovo sa drugom kolicinom."
        )

    if greske:
        return {"greske": greske}, 400  # model se ne dodiruje

    # cena iz sifarnika, ne iz zahteva
    stavka_id = model.upisi_stavku(narudzbina_id, proizvod_id, kolicina, proizvod.cena)

    return model.stavka(stavka_id).u_recnik(), 201


def obrisi_stavku(stavka_id):
    if model.stavka(stavka_id) is None:
        return {"poruka": "Trazena stavka ne postoji."}, 404

    model.obrisi_stavku(stavka_id)
    return {"poruka": "Stavka je obrisana."}, 200


def obrisi_narudzbinu(narudzbina_id):
    narudzbina = model.narudzbina(narudzbina_id)
    if narudzbina is None:
        return {"poruka": "Trazena narudzbina ne postoji."}, 404

    koliko = narudzbina.broj_stavki
    model.obrisi_narudzbinu(narudzbina_id)

    return {
        "poruka": "Narudzbina %s je obrisana, a sa njom i %s."
        % (narudzbina.broj, _stavki(koliko))
    }, 200


def obrisi_proizvod(proizvod_id):
    proizvod = model.proizvod(proizvod_id)
    if proizvod is None:
        return {"poruka": "Trazeni proizvod ne postoji."}, 404

    koliko = model.broj_stavki_sa_proizvodom(proizvod_id)
    if koliko:
        return {
            "poruka": 'Proizvod "%s" ne moze se obrisati jer se pojavljuje na '
            "postojecim narudzbinama (%s). Sifarnik je referenca ranijih "
            "narudzbina, a ne njihov vlasnik." % (proizvod.naziv, _stavki(koliko))
        }, 409

    try:
        model.obrisi_proizvod(proizvod_id)
    except model.SukobUPodacima as sukob:
        return {"poruka": str(sukob)}, 409

    return {"poruka": 'Proizvod "%s" je obrisan.' % proizvod.naziv}, 200
