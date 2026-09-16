"""
LE CONTENEUR - page d'accueil du projet.

Lance avec : python app.py
Puis ouvre : http://127.0.0.1:5000
"""
from flask import Flask, render_template, request
from mini_apps import charger_mini_apps
from mini_apps.mots_de_passe import generer, generer_memorisable, analyser, proposer_amelioration

app = Flask(__name__)

# On charge la liste des mini apps une fois, au démarrage
MINI_APPS = charger_mini_apps()


@app.route("/")
def accueil():
    return render_template("accueil.html", apps=MINI_APPS)


@app.route("/mots_de_passe", methods=["GET", "POST"])
def mots_de_passe():
    mot_de_passe = None
    mot_de_passe_teste = None
    analyse = None
    proposition = None
    longueur_choisie = 16
    types_choisis = ["min", "maj", "chiffres", "symboles"]
    mode_choisi = "aleatoire"

    if request.method == "POST":
        action = request.form.get("action")

        if action == "generer":
            mode_choisi = request.form.get("mode", "aleatoire")

            if mode_choisi == "memorisable":
                mot_de_passe = generer_memorisable()
            else:
                try:
                    longueur_choisie = int(request.form.get("longueur", 16))
                except ValueError:
                    longueur_choisie = 16
                longueur_choisie = max(4, min(64, longueur_choisie))

                types_choisis = request.form.getlist("types")
                mot_de_passe = generer(longueur=longueur_choisie, types=types_choisis)
        elif action == "verifier":
            mot_de_passe_teste = request.form.get("mot_de_passe_teste", "")
            analyse = analyser(mot_de_passe_teste)
            if analyse["niveau"] != "très fort":
                proposition = proposer_amelioration(mot_de_passe_teste)

    return render_template(
        "mots_de_passe/mots_de_passe.html",
        mot_de_passe=mot_de_passe,
        mot_de_passe_teste=mot_de_passe_teste,
        analyse=analyse,
        proposition=proposition,
        longueur_choisie=longueur_choisie,
        types_choisis=types_choisis,
        mode_choisi=mode_choisi,
    )


if __name__ == "__main__":
    app.run(debug=True)
