"""main"""

import sys
import threading
import webbrowser

import granica
import model

PORT = 8000
ADRESA = "http://localhost:%d" % PORT

NAJAVA = """
  Evidencija narudzbina - MVP (Model - View - Presenter)

    MODEL      model.py                    entiteti, pravila domena, baza
    PRESENTER  presenter.py                provera ulaza, rad nad modelom
    GRANICA    granica.py                  HTTP + JSON
    VIEW       view/index.html, view.js    prikaz i korisnicki dogadjaji

  Aplikacija radi na %s
  Zaustavljanje: Ctrl+C
"""


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    model.pripremi_bazu()
    print(NAJAVA % ADRESA)

    threading.Timer(1.0, lambda: webbrowser.open(ADRESA)).start()

    try:
        granica.pokreni(PORT)
    except OSError:
        print(
            "  Port %d je zauzet. Zatvorite raniji prozor sa aplikacijom "
            "ili izmenite PORT u pokreni.py." % PORT
        )
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n  Zaustavljeno.")


if __name__ == "__main__":
    main()
