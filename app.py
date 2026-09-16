"""
LE CONTENEUR - page d'accueil du projet.

Lance avec : python app.py
Puis ouvre : http://127.0.0.1:5000
"""
from flask import Flask, render_template
from mini_apps import charger_mini_apps, enregistrer_routes

app = Flask(__name__)

# On charge la liste des mini apps, puis on branche leurs routes
MINI_APPS = charger_mini_apps()
enregistrer_routes(app)


@app.route("/")
def accueil():
    return render_template("accueil.html", apps=MINI_APPS)


if __name__ == "__main__":
    app.run(debug=True)
