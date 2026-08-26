from flask import Blueprint, jsonify, request

from database import db
from models import JEDINICE_MERE, Proizvod, Stavka
from presenters import validacija

proizvod_bp = Blueprint("proizvod", __name__, url_prefix="/api/proizvodi")

KOLONE_ZA_SORTIRANJE = {
    "naziv": Proizvod.naziv,
    "cena": Proizvod.cena,
}


def procitaj_podatke(podaci):
    vrednosti = {}
    greske = {}

    vrednosti["naziv"], greska = validacija.tekst(podaci, "naziv", "Naziv", maksimum=100)
    if greska:
        greske["naziv"] = greska

    vrednosti["opis"], greska = validacija.tekst(podaci, "opis", "Opis")
    if greska:
        greske["opis"] = greska

    vrednosti["cena"], greska = validacija.decimalni_broj(
        podaci, "cena", "Cena", minimum=0
    )
    if greska:
        greske["cena"] = greska

    vrednosti["jedinica_mere"], greska = validacija.izbor(
        podaci, "jedinica_mere", "Jedinica mere", JEDINICE_MERE
    )
    if greska:
        greske["jedinica_mere"] = greska

    vrednosti["dostupan"], _ = validacija.logicka(podaci, "dostupan")

    return vrednosti, greske


@proizvod_bp.get("/jedinice-mere")
def jedinice_mere():
    return jsonify(JEDINICE_MERE)


@proizvod_bp.get("")
def lista_proizvoda():
    pretraga = request.args.get("pretraga", "").strip()
    sortiranje = request.args.get("sortiranje", "naziv")
    smer = request.args.get("smer", "asc")

    upit = Proizvod.query

    if pretraga:
        upit = upit.filter(Proizvod.naziv.ilike(f"%{pretraga}%"))

    if request.args.get("samo_dostupni") == "1":
        upit = upit.filter(Proizvod.dostupan.is_(True))

    kolona = KOLONE_ZA_SORTIRANJE.get(sortiranje, Proizvod.naziv)
    upit = upit.order_by(kolona.desc() if smer == "desc" else kolona.asc())

    return jsonify([proizvod.u_recnik() for proizvod in upit.all()])


@proizvod_bp.get("/<int:proizvod_id>")
def jedan_proizvod(proizvod_id):
    proizvod = db.session.get(Proizvod, proizvod_id)
    if proizvod is None:
        return jsonify({"poruka": "Traženi proizvod ne postoji."}), 404

    return jsonify(proizvod.u_recnik())


@proizvod_bp.post("")
def dodaj_proizvod():
    vrednosti, greske = procitaj_podatke(request.get_json(silent=True) or {})
    if greske:
        return jsonify({"greske": greske}), 400

    proizvod = Proizvod(**vrednosti)
    db.session.add(proizvod)
    db.session.commit()

    return jsonify(proizvod.u_recnik()), 201


@proizvod_bp.put("/<int:proizvod_id>")
def izmeni_proizvod(proizvod_id):
    proizvod = db.session.get(Proizvod, proizvod_id)
    if proizvod is None:
        return jsonify({"poruka": "Traženi proizvod ne postoji."}), 404

    vrednosti, greske = procitaj_podatke(request.get_json(silent=True) or {})
    if greske:
        return jsonify({"greske": greske}), 400

    for polje, vrednost in vrednosti.items():
        setattr(proizvod, polje, vrednost)
    db.session.commit()

    return jsonify(proizvod.u_recnik())


@proizvod_bp.delete("/<int:proizvod_id>")
def obrisi_proizvod(proizvod_id):
    proizvod = db.session.get(Proizvod, proizvod_id)
    if proizvod is None:
        return jsonify({"poruka": "Traženi proizvod ne postoji."}), 404

    # Proizvod nije podređen narudžbini, pa se ne briše kaskadno. Ako se
    # pojavljuje na nekoj narudžbini, brisanje se odbija i nudi se
    # označavanje kao nedostupnog.
    upotrebljen = Stavka.query.filter_by(proizvod_id=proizvod_id).count()
    if upotrebljen:
        return (
            jsonify(
                {
                    "poruka": (
                        "Proizvod se već koristi u narudžbinama "
                        f"(broj stavki: {upotrebljen}) i zato ne može biti obrisan. "
                        "Označite ga kao nedostupan."
                    ),
                    "upotrebljen_na_stavki": upotrebljen,
                }
            ),
            409,
        )

    db.session.delete(proizvod)
    db.session.commit()

    return jsonify({"poruka": "Proizvod je obrisan."})
