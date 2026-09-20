"""
Les pages web (routes Flask) de la mini app "Détecteur de phishing".

Séparé de __init__.py : ce fichier s'occupe du web (formulaires, HTML),
__init__.py s'occupe de la logique pure (analyser...).
"""

from flask import Blueprint, render_template, request

from . import analyser

blueprint = Blueprint("detecteur_phishing", __name__)


@blueprint.route("/detecteur_phishing", methods=["GET", "POST"])
def detecteur_phishing():
    texte = ""
    resultat = None

    if request.method == "POST":
        texte = request.form.get("texte", "")
        resultat = analyser(texte)

    return render_template(
        "detecteur_phishing/detecteur_phishing.html",
        texte=texte,
        resultat=resultat,
    )
