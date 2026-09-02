from decimal import Decimal

from database import db

STATUSI = {
    "u_pripremi": "U pripremi",
    "potvrdjena": "Potvrdjena",
    "isporucena": "Isporucena",
}

JEDINICE_MERE = ["kom", "kg", "l", "m", "pak"]


class Proizvod(db.Model):
    """Sifarnik, van master-detail veze."""

    __tablename__ = "proizvod"

    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(100), nullable=False)
    opis = db.Column(db.Text, nullable=False)
    cena = db.Column(db.Numeric(10, 2), nullable=False)
    jedinica_mere = db.Column(db.String(20), nullable=False)
    dostupan = db.Column(db.Boolean, nullable=False, default=True)

    def u_recnik(self):
        return {
            "id": self.id,
            "naziv": self.naziv,
            "opis": self.opis,
            "cena": float(self.cena),
            "jedinica_mere": self.jedinica_mere,
            "dostupan": bool(self.dostupan),
        }


class Narudzbina(db.Model):
    """Master entitet."""

    __tablename__ = "narudzbina"

    id = db.Column(db.Integer, primary_key=True)
    broj = db.Column(db.String(20), nullable=False, unique=True)
    kupac = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    datum = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="u_pripremi")

    stavke = db.relationship(
        "Stavka",
        backref="narudzbina",
        cascade="all, delete-orphan",
        order_by="Stavka.id",
    )

    @property
    def broj_stavki(self):
        return len(self.stavke)

    @property
    def ukupan_iznos(self):
        return sum((stavka.iznos for stavka in self.stavke), Decimal("0.00"))

    def u_recnik(self, sa_stavkama=False):
        podaci = {
            "id": self.id,
            "broj": self.broj,
            "kupac": self.kupac,
            "email": self.email,
            "datum": self.datum.isoformat(),
            "status": self.status,
            "status_naziv": STATUSI.get(self.status, self.status),
            "broj_stavki": self.broj_stavki,
            "ukupan_iznos": float(self.ukupan_iznos),
        }
        if sa_stavkama:
            podaci["stavke"] = [stavka.u_recnik() for stavka in self.stavke]
        return podaci


class Stavka(db.Model):
    """Detail entitet, ne postoji bez narudzbine."""

    __tablename__ = "stavka"
    __table_args__ = (
        db.UniqueConstraint("narudzbina_id", "proizvod_id", name="uq_stavka_proizvod"),
    )

    id = db.Column(db.Integer, primary_key=True)
    narudzbina_id = db.Column(
        db.Integer,
        db.ForeignKey("narudzbina.id", ondelete="CASCADE"),
        nullable=False,
    )
    proizvod_id = db.Column(
        db.Integer,
        db.ForeignKey("proizvod.id", ondelete="RESTRICT"),
        nullable=True,  # NULL kad je proizvod arhiviran
    )
    kolicina = db.Column(db.Integer, nullable=False)
    cena_po_komadu = db.Column(db.Numeric(10, 2), nullable=False)  # zapamcena cena
    proizvod_naziv = db.Column(db.String(100), nullable=False)     # zapamcen naziv
    jedinica_mere = db.Column(db.String(20), nullable=False)

    proizvod = db.relationship("Proizvod")

    @property
    def iznos(self):
        return self.cena_po_komadu * self.kolicina

    def u_recnik(self):
        return {
            "id": self.id,
            "narudzbina_id": self.narudzbina_id,
            "proizvod_id": self.proizvod_id,
            "proizvod_naziv": self.proizvod_naziv,
            "jedinica_mere": self.jedinica_mere,
            "kolicina": self.kolicina,
            "cena_po_komadu": float(self.cena_po_komadu),
            "iznos": float(self.iznos),
            "arhivirana": self.proizvod_id is None,
        }
