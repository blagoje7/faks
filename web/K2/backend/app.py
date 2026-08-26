import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from sqlalchemy import text

from config import Config
from database import db
from presenters.narudzbina_presenter import narudzbina_bp
from presenters.proizvod_presenter import proizvod_bp
from presenters.stavka_presenter import stavka_bp

PUTANJA_KLIJENTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


def create_app(config_object=Config):
    # Flask servira samo /assets (fajlove koje generiše Vite build), da njegova
    # static ruta ne bi presrela duboke putanje namenjene Vue Routeru.
    app = Flask(
        __name__,
        static_folder=os.path.join(PUTANJA_KLIJENTA, "assets"),
        static_url_path="/assets",
    )
    app.config.from_object(config_object)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}})

    app.register_blueprint(proizvod_bp)
    app.register_blueprint(narudzbina_bp)
    app.register_blueprint(stavka_bp)

    registruj_greske(app)
    registruj_klijenta(app)

    return app


def registruj_greske(app):
    """API greške moraju biti JSON, a ne Flask HTML stranica."""

    @app.errorhandler(404)
    def nije_pronadjeno(greska):
        if request.path.startswith("/api/"):
            return jsonify({"poruka": "Tražena putanja ne postoji."}), 404
        return greska

    @app.errorhandler(405)
    def metoda_nije_dozvoljena(greska):
        return jsonify({"poruka": "HTTP metoda nije dozvoljena za ovu putanju."}), 405

    @app.errorhandler(Exception)
    def neocekivana_greska(greska):
        app.logger.exception("Neočekivana greška")
        db.session.rollback()
        if request.path.startswith("/api/"):
            return jsonify({"poruka": f"Greška na serveru: {greska}"}), 500
        raise greska

    @app.get("/api/stanje")
    def stanje():
        """Provera veze sa bazom pre prezentacije."""
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"baza": "povezana"})
        except Exception as greska:
            return jsonify({"baza": "nedostupna", "detalji": str(greska)}), 503


def registruj_klijenta(app):
    """Servira izgrađenu Vue aplikaciju iz static/.

    Sve putanje koje nisu API i nisu postojeći fajl vraćaju index.html,
    da bi Vue Router mogao da preuzme rutiranje na klijentu.
    """

    @app.route("/", defaults={"putanja": ""})
    @app.route("/<path:putanja>")
    def klijentska_aplikacija(putanja):
        # Nepoznata API putanja ne sme da vrati klijentsku stranicu.
        if putanja.startswith("api/"):
            return jsonify({"poruka": "Tražena API putanja ne postoji."}), 404

        if putanja and os.path.isfile(os.path.join(PUTANJA_KLIJENTA, putanja)):
            return send_from_directory(PUTANJA_KLIJENTA, putanja)

        index = os.path.join(PUTANJA_KLIJENTA, "index.html")
        if not os.path.exists(index):
            return (
                jsonify(
                    {
                        "poruka": "Vue klijent nije izgrađen.",
                        "resenje": "U folderu frontend/ pokrenite: npm install && npm run build",
                    }
                ),
                501,
            )

        return send_from_directory(PUTANJA_KLIJENTA, "index.html")


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
