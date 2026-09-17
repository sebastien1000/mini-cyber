"""
LE CONTENEUR - page d'accueil du projet.

Lance avec : python app.py
Puis ouvre : http://127.0.0.1:5000
"""

import os

from dotenv import load_dotenv
from flask import Flask, render_template

from mini_apps import charger_mini_apps, enregistrer_routes

# Charge les variables du fichier .env (s'il existe) dans l'environnement.
# Pratique en local ; en production, les variables sont plutôt définies
# directement par l'hébergeur.
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")
DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"

# On charge la liste des mini apps, puis on branche leurs routes
MINI_APPS = charger_mini_apps()
enregistrer_routes(app)


@app.route("/")
def accueil():
    return render_template("accueil.html", apps=MINI_APPS)


if __name__ == "__main__":
    app.run(debug=DEBUG)
