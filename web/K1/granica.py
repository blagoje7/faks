"""GRANICA - HTTP i JSON izmedju View-a i Presentera. Bez pravila domena."""

import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import presenter

FOLDER_VIEW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "view")

TIPOVI = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}

# metoda, putanja, funkcija Presentera, prima li telo zahteva
RUTE = [
    ("GET", r"^/api/narudzbine$", presenter.lista_narudzbina, False),
    ("GET", r"^/api/narudzbine/(\d+)$", presenter.jedna_narudzbina, False),
    ("DELETE", r"^/api/narudzbine/(\d+)$", presenter.obrisi_narudzbinu, False),
    ("GET", r"^/api/proizvodi$", presenter.lista_proizvoda, False),
    ("DELETE", r"^/api/proizvodi/(\d+)$", presenter.obrisi_proizvod, False),
    ("POST", r"^/api/stavke$", presenter.dodaj_stavku, True),
    ("DELETE", r"^/api/stavke/(\d+)$", presenter.obrisi_stavku, False),
]


class Obrada(BaseHTTPRequestHandler):
    server_version = "K1-MVP"

    def do_GET(self):
        if self.path.startswith("/api/"):
            self._obradi("GET")
        else:
            self._posluzi_view()

    def do_POST(self):
        self._obradi("POST")

    def do_DELETE(self):
        self._obradi("DELETE")

    def _obradi(self, metoda):
        putanja = self.path.split("?")[0]

        for ruta_metoda, obrazac, funkcija, sa_telom in RUTE:
            poklapanje = re.match(obrazac, putanja)
            if not poklapanje or ruta_metoda != metoda:
                continue

            argumenti = [int(vrednost) for vrednost in poklapanje.groups()]
            if sa_telom:
                argumenti.append(self._telo_zahteva())

            telo, status = funkcija(*argumenti)
            self._odgovori(telo, status)
            return

        self._odgovori({"poruka": "Trazena adresa ne postoji."}, 404)

    def _telo_zahteva(self):
        duzina = int(self.headers.get("Content-Length") or 0)
        if not duzina:
            return {}

        try:
            return json.loads(self.rfile.read(duzina).decode("utf-8"))
        except ValueError:
            return {}

    def _odgovori(self, telo, status):
        sadrzaj = json.dumps(telo, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(sadrzaj)))
        self.end_headers()
        self.wfile.write(sadrzaj)

    def _posluzi_view(self):
        putanja = self.path.split("?")[0]
        ime = "index.html" if putanja == "/" else putanja.lstrip("/")
        fajl = os.path.normpath(os.path.join(FOLDER_VIEW, ime))

        if not fajl.startswith(FOLDER_VIEW) or not os.path.isfile(fajl):
            self.send_error(404)
            return

        with open(fajl, "rb") as otvoren:
            sadrzaj = otvoren.read()

        self.send_response(200)
        self.send_header(
            "Content-Type",
            TIPOVI.get(os.path.splitext(fajl)[1], "application/octet-stream"),
        )
        self.send_header("Content-Length", str(len(sadrzaj)))
        self.end_headers()
        self.wfile.write(sadrzaj)

    def log_message(self, format, *args):
        print("   %s" % (format % args))


def pokreni(port=8000):
    server = ThreadingHTTPServer(("127.0.0.1", port), Obrada)
    server.serve_forever()
