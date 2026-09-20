"""
Les pages web (routes Flask) de la mini app "Détecteur de phishing".

Séparé de __init__.py : ce fichier s'occupe du web (formulaires, HTML),
__init__.py s'occupe de la logique pure (analyser...).
"""

from flask import Blueprint, render_template, request

from . import analyser, analyser_url, extraire_urls

blueprint = Blueprint("detecteur_phishing", __name__)


def _est_un_lien_seul(texte):
    """Vrai si le texte collé est UN SEUL lien, sans rien d'autre autour."""
    return bool(texte) and " " not in texte and extraire_urls(texte) == [texte]


@blueprint.route("/detecteur_phishing", methods=["GET", "POST"])
def detecteur_phishing():
    texte = ""
    resultat = None
    mode_lien_seul = False

    if request.method == "POST":
        texte = request.form.get("texte", "")
        texte_nettoye = texte.strip()
        mode_lien_seul = _est_un_lien_seul(texte_nettoye)
        resultat = analyser_url(texte_nettoye) if mode_lien_seul else analyser(texte)

    return render_template(
        "detecteur_phishing/detecteur_phishing.html",
        texte=texte,
        resultat=resultat,
        mode_lien_seul=mode_lien_seul,
    )
