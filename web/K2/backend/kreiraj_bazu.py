"""Kreira semu k2_narudzbine i puni je podacima iz baza.sql."""

import getpass
import os
import sys

import pymysql

import config


def lozinka():
    if config.MYSQL_PASSWORD:
        return config.MYSQL_PASSWORD
    return getpass.getpass(f"Lozinka za MySQL korisnika '{config.MYSQL_USER}': ")


def naredbe_iz_fajla(putanja):
    with open(putanja, "r", encoding="utf-8") as fajl:
        for naredba in fajl.read().split(";"):
            if naredba.strip():
                yield naredba


def main():
    putanja = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baza.sql")

    try:
        veza = pymysql.connect(
            host=config.MYSQL_HOST,
            port=int(config.MYSQL_PORT),
            user=config.MYSQL_USER,
            password=lozinka(),
            charset="utf8mb4",
            autocommit=True,
        )
    except pymysql.err.OperationalError as greska:
        print(f"Povezivanje na MySQL nije uspelo: {greska}")
        print("Proverite da li MySQL servis radi i da li su podaci u .env fajlu tacni.")
        return 1

    with veza:
        with veza.cursor() as kursor:
            for naredba in naredbe_iz_fajla(putanja):
                kursor.execute(naredba)

        with veza.cursor() as kursor:
            kursor.execute(
                "SELECT (SELECT COUNT(*) FROM k2_narudzbine.proizvod),"
                "       (SELECT COUNT(*) FROM k2_narudzbine.narudzbina),"
                "       (SELECT COUNT(*) FROM k2_narudzbine.stavka)"
            )
            proizvoda, narudzbina, stavki = kursor.fetchone()

    print(
        f"Baza k2_narudzbine je kreirana: {proizvoda} proizvoda, "
        f"{narudzbina} narudzbine, {stavki} stavki."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
