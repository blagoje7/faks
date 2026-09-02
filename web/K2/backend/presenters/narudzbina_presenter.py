from datetime import date

from flask import Blueprint, jsonify, request

from database import db
from models import STATUSI, Narudzbina, Stavka
from presenters import tekst, validacija

narudzbina_bp = Blueprint("narudzbina", __name__, url_prefix="/api/narudzbine")

KOLONE_ZA_SORTIRANJE = {
    "broj": Narudzbina.broj,
    "kupac": Narudzbina.kupac,
    "datum": Narudzbina.datum,
}


def procitaj_podatke(podaci, narudzbina_id=None):
    vrednosti = {}
    greske = {}

    vrednosti["broj"], greska = validacija.tekst(podaci, "broj", "Broj", maksimum=20)
    if greska:
        greske["broj"] = greska
    else:
        zauzet = Narudzbina.query.filter_by(broj=vrednosti["broj"]).filter(
            Narudzbina.id != narudzbina_id
        )
        if zauzet.first() is not None:
            greske["broj"] = "Narudzbina sa tim brojem vec postoji."

    vrednosti["kupac"], greska = validacija.tekst(podaci, "kupac", "Kupac", maksimum=100)
    if greska:
        greske["kupac"] = greska

    vrednosti["email"], greska = validacija.eposta(podaci, "email", "Elektronska posta")
    if greska:
        greske["email"] = greska

    vrednosti["datum"], greska = validacija.datum(
        podaci, "datum", "Datum", bez_buducnosti=True
    )
    if greska:
        greske["datum"] = greska

    vrednosti["status"], greska = validacija.izbor(
        podaci, "status", "Status", STATUSI.keys()
    )
    if greska:
        greske["status"] = greska

    return vrednosti, greske


@narudzbina_bp.get("/statusi")
def statusi():
    return jsonify([{"vrednost": k, "naziv": v} for k, v in STATUSI.items()])


@narudzbina_bp.get("/sledeci-broj")
def sledeci_broj():
    """Predlog broja za novu narudzbinu."""
    godina = date.today().year
    prefiks = f"NAR-{godina}-"

    postojeci = Narudzbina.query.filter(Narudzbina.broj.like(f"{prefiks}%")).all()

    najveci = 0
    for narudzbina in postojeci:
        nastavak = narudzbina.broj[len(prefiks) :]
        if nastavak.isdigit():
            najveci = max(najveci, int(nastavak))

    return jsonify({"broj": f"{prefiks}{najveci + 1:04d}"})


@narudzbina_bp.get("")
def lista_narudzbina():
    pretraga = request.args.get("pretraga", "").strip()
    status = request.args.get("status", "").strip()
    sortiranje = request.args.get("sortiranje", "datum")
    smer = request.args.get("smer", "desc")

    upit = Narudzbina.query

    if pretraga:
        uzorak = f"%{pretraga}%"
        upit = upit.filter(
            db.or_(Narudzbina.broj.ilike(uzorak), Narudzbina.kupac.ilike(uzorak))
        )

    if status:
        upit = upit.filter(Narudzbina.status == status)

    kolona = KOLONE_ZA_SORTIRANJE.get(sortiranje, Narudzbina.datum)
    upit = upit.order_by(kolona.desc() if smer == "desc" else kolona.asc())

    return jsonify([narudzbina.u_recnik() for narudzbina in upit.all()])


@narudzbina_bp.get("/<int:narudzbina_id>")
def jedna_narudzbina(narudzbina_id):
    narudzbina = db.session.get(Narudzbina, narudzbina_id)
    if narudzbina is None:
        return jsonify({"poruka": "Trazena narudzbina ne postoji."}), 404

    return jsonify(narudzbina.u_recnik(sa_stavkama=True))


@narudzbina_bp.get("/<int:narudzbina_id>/stavke")
def stavke_narudzbine(narudzbina_id):
    narudzbina = db.session.get(Narudzbina, narudzbina_id)
    if narudzbina is None:
        return jsonify({"poruka": "Trazena narudzbina ne postoji."}), 404

    stavke = Stavka.query.filter_by(narudzbina_id=narudzbina_id).all()
    return jsonify([stavka.u_recnik() for stavka in stavke])


@narudzbina_bp.post("")
def dodaj_narudzbinu():
    vrednosti, greske = procitaj_podatke(request.get_json(silent=True) or {})
    if greske:
        return jsonify({"greske": greske}), 400

    narudzbina = Narudzbina(**vrednosti)
    db.session.add(narudzbina)
    db.session.commit()

    return jsonify(narudzbina.u_recnik()), 201


@narudzbina_bp.put("/<int:narudzbina_id>")
def izmeni_narudzbinu(narudzbina_id):
    narudzbina = db.session.get(Narudzbina, narudzbina_id)
    if narudzbina is None:
        return jsonify({"poruka": "Trazena narudzbina ne postoji."}), 404

    vrednosti, greske = procitaj_podatke(
        request.get_json(silent=True) or {}, narudzbina_id=narudzbina_id
    )
    if greske:
        return jsonify({"greske": greske}), 400

    for polje, vrednost in vrednosti.items():
        setattr(narudzbina, polje, vrednost)
    db.session.commit()

    return jsonify(narudzbina.u_recnik())


@narudzbina_bp.delete("/<int:narudzbina_id>")
def obrisi_narudzbinu(narudzbina_id):
    narudzbina = db.session.get(Narudzbina, narudzbina_id)
    if narudzbina is None:
        return jsonify({"poruka": "Trazena narudzbina ne postoji."}), 404

    obrisano_stavki = narudzbina.broj_stavki
    db.session.delete(narudzbina)
    db.session.commit()

    if obrisano_stavki:
        poruka = f"Narudzbina je obrisana zajedno sa {tekst.stavki(obrisano_stavki)}."
    else:
        poruka = "Narudzbina je obrisana."

    return jsonify({"poruka": poruka, "obrisano_stavki": obrisano_stavki})
