"""
Les pages web (routes Flask) de la mini app "Mots de passe".

Séparé de __init__.py : ce fichier s'occupe du web (formulaires, HTML),
__init__.py s'occupe de la logique pure (générer, analyser...).
"""

from flask import Blueprint, render_template, request

from . import analyser, generer, generer_memorisable, proposer_amelioration

# Un "Blueprint" est un mini groupe de routes, qu'on branche sur l'app principale
blueprint = Blueprint("mots_de_passe", __name__)


@blueprint.route("/mots_de_passe", methods=["GET", "POST"])
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
