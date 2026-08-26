from flask import Blueprint, jsonify, request

from database import db
from models import Narudzbina, Proizvod, Stavka
from presenters import validacija

stavka_bp = Blueprint("stavka", __name__, url_prefix="/api/stavke")


def procitaj_podatke(podaci, stavka=None):
    """Vraća (vrednosti, greske) za stavku.

    I narudžbina i proizvod se biraju preko select polja, pa oba stižu kao
    identifikatori u telu zahteva i oba se proveravaju ovde.
    """
    vrednosti = {}
    greske = {}

    vrednosti["narudzbina_id"], greska = validacija.ceo_broj(
        podaci, "narudzbina_id", "Narudžbina"
    )
    if greska:
        greske["narudzbina_id"] = greska
    elif db.session.get(Narudzbina, vrednosti["narudzbina_id"]) is None:
        greske["narudzbina_id"] = "Izabrana narudžbina ne postoji."

    proizvod = None
    vrednosti["proizvod_id"], greska = validacija.ceo_broj(
        podaci, "proizvod_id", "Proizvod"
    )
    if greska:
        greske["proizvod_id"] = greska
    else:
        proizvod = db.session.get(Proizvod, vrednosti["proizvod_id"])
        if proizvod is None:
            greske["proizvod_id"] = "Izabrani proizvod ne postoji."
        elif not proizvod.dostupan and (
            stavka is None or stavka.proizvod_id != vrednosti["proizvod_id"]
        ):
            greske["proizvod_id"] = "Izabrani proizvod nije dostupan za poručivanje."

    vrednosti["kolicina"], greska = validacija.ceo_broj(
        podaci, "kolicina", "Količina", minimum=1
    )
    if greska:
        greske["kolicina"] = greska

    if "narudzbina_id" not in greske and "proizvod_id" not in greske:
        zauzet = Stavka.query.filter_by(
            narudzbina_id=vrednosti["narudzbina_id"],
            proizvod_id=vrednosti["proizvod_id"],
        )
        if stavka is not None:
            zauzet = zauzet.filter(Stavka.id != stavka.id)

        if zauzet.first() is not None:
            greske["proizvod_id"] = (
                "Taj proizvod već postoji na ovoj narudžbini. Izmenite količinu "
                "postojeće stavke."
            )

    # Cena se prepisuje iz šifarnika samo kada se proizvod postavlja ili menja.
    # Izmena same količine ne dira zapamćenu cenu.
    if proizvod is not None and (
        stavka is None or stavka.proizvod_id != vrednosti["proizvod_id"]
    ):
        vrednosti["cena_po_komadu"] = proizvod.cena

    return vrednosti, greske


@stavka_bp.get("/<int:stavka_id>")
def jedna_stavka(stavka_id):
    stavka = db.session.get(Stavka, stavka_id)
    if stavka is None:
        return jsonify({"poruka": "Tražena stavka ne postoji."}), 404

    return jsonify(stavka.u_recnik())


@stavka_bp.post("")
def dodaj_stavku():
    vrednosti, greske = procitaj_podatke(request.get_json(silent=True) or {})
    if greske:
        return jsonify({"greske": greske}), 400

    stavka = Stavka(**vrednosti)
    db.session.add(stavka)
    db.session.commit()

    return jsonify(stavka.u_recnik()), 201


@stavka_bp.put("/<int:stavka_id>")
def izmeni_stavku(stavka_id):
    stavka = db.session.get(Stavka, stavka_id)
    if stavka is None:
        return jsonify({"poruka": "Tražena stavka ne postoji."}), 404

    vrednosti, greske = procitaj_podatke(
        request.get_json(silent=True) or {}, stavka=stavka
    )
    if greske:
        return jsonify({"greske": greske}), 400

    for polje, vrednost in vrednosti.items():
        setattr(stavka, polje, vrednost)
    db.session.commit()

    return jsonify(stavka.u_recnik())


@stavka_bp.delete("/<int:stavka_id>")
def obrisi_stavku(stavka_id):
    stavka = db.session.get(Stavka, stavka_id)
    if stavka is None:
        return jsonify({"poruka": "Tražena stavka ne postoji."}), 404

    db.session.delete(stavka)
    db.session.commit()

    return jsonify({"poruka": "Stavka je obrisana."})
