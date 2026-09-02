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
    app = Flask(
        __name__,
        static_folder=os.path.join(PUTANJA_KLIJENTA, "assets"),
        static_url_path="/assets",  # da static ruta ne presretne Vue Router
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
    """API greske kao JSON, ne kao HTML."""

    @app.errorhandler(404)
    def nije_pronadjeno(greska):
        if request.path.startswith("/api/"):
            return jsonify({"poruka": "Trazena putanja ne postoji."}), 404
        return greska

    @app.errorhandler(405)
    def metoda_nije_dozvoljena(greska):
        return jsonify({"poruka": "HTTP metoda nije dozvoljena za ovu putanju."}), 405

    @app.errorhandler(Exception)
    def neocekivana_greska(greska):
        app.logger.exception("Neocekivana greska")
        db.session.rollback()
        if request.path.startswith("/api/"):
            return jsonify({"poruka": f"Greska na serveru: {greska}"}), 500
        raise greska

    @app.get("/api/stanje")
    def stanje():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"baza": "povezana"})
        except Exception as greska:
            return jsonify({"baza": "nedostupna", "detalji": str(greska)}), 503


def registruj_klijenta(app):
    """Nepoznate putanje vracaju index.html, da rutiranje preuzme Vue Router."""

    @app.route("/", defaults={"putanja": ""})
    @app.route("/<path:putanja>")
    def klijentska_aplikacija(putanja):
        if putanja.startswith("api/"):
            return jsonify({"poruka": "Trazena API putanja ne postoji."}), 404

        if putanja and os.path.isfile(os.path.join(PUTANJA_KLIJENTA, putanja)):
            return send_from_directory(PUTANJA_KLIJENTA, putanja)

        index = os.path.join(PUTANJA_KLIJENTA, "index.html")
        if not os.path.exists(index):
            return (
                jsonify(
                    {
                        "poruka": "Vue klijent nije izgradjen.",
                        "resenje": "U folderu frontend/ pokrenite: npm install && npm run build",
                    }
                ),
                501,
            )

        return send_from_directory(PUTANJA_KLIJENTA, "index.html")


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
