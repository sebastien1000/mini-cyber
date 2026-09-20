"""
Mini app : Détecteur de phishing.
"""

import ipaddress
import re
from urllib.parse import urlsplit

INFO = {
    "nom": "Détecteur de phishing",
    "icone": "🎣",
    "description": "Analyser un email ou un SMS suspect pour repérer les signaux de phishing.",
}


# Repère les liens dans un texte : avec un schéma (http/https), le nom d'hôte peut
# être précédé d'un "identifiant@" (la technique classique pour cacher la vraie
# destination) et être une adresse IP ; sans schéma, on exige un vrai nom de domaine
# pour éviter de confondre un lien nu avec une adresse email (ex: contact@site.fr).
_URL_REGEX = re.compile(
    r"https?://(?:[^\s/@]+@)?"
    r"(?:\d{1,3}(?:\.\d{1,3}){3}(?::\d+)?|(?:[\w-]+\.)+[a-zA-Z]{2,})(?:/[^\s]*)?"
    r"|(?:[\w-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?",
    re.IGNORECASE,
)

RACCOURCISSEURS_CONNUS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "rebrand.ly",
    "cutt.ly",
    "shorturl.at",
}

# Marques souvent usurpées, avec leur vrai domaine. Un lien qui contient le nom
# de la marque sans être ce domaine (ni un de ses sous-domaines) est suspect.
MARQUES_CONNUES = {
    "paypal": "paypal.com",
    "amazon": "amazon.fr",
    "google": "google.com",
    "microsoft": "microsoft.com",
    "apple": "apple.com",
    "facebook": "facebook.com",
    "netflix": "netflix.com",
    "laposte": "laposte.fr",
    "impots": "impots.gouv.fr",
    "ameli": "ameli.fr",
    "orange": "orange.fr",
    "free": "free.fr",
}

MOTS_URGENCE = [
    "immédiatement",
    "de toute urgence",
    "sous 24h",
    "sous 24 heures",
    "dans les 24 heures",
    "compte sera suspendu",
    "compte bloqué",
    "compte suspendu",
    "compte sera fermé",
    "dernier délai",
    "expire aujourd'hui",
    "action requise",
    "agissez maintenant",
    "avant qu'il ne soit trop tard",
    "délai de 48h",
]

MOTS_DONNEES_SENSIBLES = [
    "mot de passe",
    "numéro de carte",
    "code de carte",
    "coordonnées bancaires",
    "numéro de sécurité sociale",
    "code confidentiel",
    "cvv",
    "identifiants de connexion",
    "code secret",
    "numéro de compte",
]

SALUTATIONS_GENERIQUES = [
    "cher client",
    "chère cliente",
    "cher utilisateur",
    "chère utilisatrice",
    "cher membre",
    "dear customer",
]

EXTENSIONS_DANGEREUSES = [".exe", ".scr", ".js", ".vbs", ".bat", ".jar", ".msi", ".zip"]


def extraire_urls(texte):
    """Renvoie la liste des liens trouvés dans un texte."""
    return _URL_REGEX.findall(texte or "")


def _hote(url):
    """Renvoie le nom d'hôte d'une URL (ex: 'faux-site.com' pour 'http://x@faux-site.com/y')."""
    url_normalisee = url if "://" in url else "http://" + url
    return urlsplit(url_normalisee).hostname or ""


def _est_adresse_ip(hote):
    try:
        ipaddress.ip_address(hote)
        return True
    except ValueError:
        return False


def _imite_une_marque(hote):
    """Vrai si l'hôte contient le nom d'une marque connue sans être (un sous-domaine de) son vrai domaine."""
    if not hote:
        return False
    for marque, domaine_officiel in MARQUES_CONNUES.items():
        if marque in hote and hote != domaine_officiel and not hote.endswith("." + domaine_officiel):
            return True
    return False


def _contient_un_mot(texte_minuscule, mots):
    return any(mot in texte_minuscule for mot in mots)


def analyser(texte):
    """Analyse un texte (email, SMS...) et repère les signaux classiques de phishing.

    Retourne un dictionnaire avec :
    - niveau : 'sûr', 'suspect' ou 'dangereux'
    - signaux : la liste des critères testés (respecté ou non)
    - conseils : les explications des signaux détectés
    - urls_trouvees : les liens repérés dans le texte
    """
    texte = texte or ""
    texte_minuscule = texte.lower()
    urls = extraire_urls(texte)
    hotes = [_hote(url) for url in urls]

    url_ip = any(_est_adresse_ip(hote) for hote in hotes)
    url_raccourci = any(hote in RACCOURCISSEURS_CONNUS for hote in hotes)
    url_arobase = any("@" in url for url in urls)
    url_sans_https = any(url.lower().startswith("http://") for url in urls)
    url_imite_marque = any(_imite_une_marque(hote) for hote in hotes)

    signaux = [
        {
            "label": "Aucun lien ne pointe vers une adresse IP",
            "ok": not url_ip,
            "conseil": (
                "Un lien qui pointe vers une adresse IP plutôt qu'un nom de domaine "
                "(ex: http://192.168.1.1/...) est un signal fort de phishing."
            ),
        },
        {
            "label": "Aucun lien ne passe par un raccourcisseur d'URL",
            "ok": not url_raccourci,
            "conseil": (
                "Les raccourcisseurs (bit.ly, tinyurl...) cachent la vraie destination "
                "du lien : méfie-toi avant de cliquer."
            ),
        },
        {
            "label": "Aucun lien ne contient de @ suspect",
            "ok": not url_arobase,
            "conseil": (
                "Un @ dans un lien peut cacher la vraie destination juste après lui "
                "(ex: vrai-site.com@faux-site.com mène en réalité à faux-site.com)."
            ),
        },
        {
            "label": "Les liens utilisent une connexion sécurisée (https)",
            "ok": not url_sans_https,
            "conseil": "Un lien en http:// (non chiffré) est plus facilement intercepté ou falsifié.",
        },
        {
            "label": "Aucun lien n'imite le nom d'une marque connue",
            "ok": not url_imite_marque,
            "conseil": (
                "Un domaine comme paypal-securite-login.com n'est PAS le vrai site PayPal : "
                "seul paypal.com (ou un de ses sous-domaines) l'est."
            ),
        },
        {
            "label": "Pas de sentiment d'urgence excessif",
            "ok": not _contient_un_mot(texte_minuscule, MOTS_URGENCE),
            "conseil": (
                "Créer un sentiment d'urgence ('agis maintenant', 'compte bloqué'...) "
                "est une technique classique pour empêcher de réfléchir."
            ),
        },
        {
            "label": "Ne demande pas d'informations sensibles",
            "ok": not _contient_un_mot(texte_minuscule, MOTS_DONNEES_SENSIBLES),
            "conseil": "Une organisation sérieuse ne demande jamais un mot de passe ou un code de carte par email/SMS.",
        },
        {
            "label": "Salutation personnalisée (pas générique)",
            "ok": not _contient_un_mot(texte_minuscule, SALUTATIONS_GENERIQUES),
            "conseil": "'Cher client' à la place de ton prénom peut indiquer un envoi de masse frauduleux.",
        },
        {
            "label": "Pas de pièce jointe à un format à risque",
            "ok": not _contient_un_mot(texte_minuscule, EXTENSIONS_DANGEREUSES),
            "conseil": (
                "Les formats .exe, .js, .zip, .scr... peuvent contenir des virus : "
                "ne les ouvre jamais sans certitude sur leur origine."
            ),
        },
    ]

    nombre_signaux = sum(1 for signal in signaux if not signal["ok"])

    if nombre_signaux == 0:
        niveau = "sûr"
    elif nombre_signaux <= 2:
        niveau = "suspect"
    else:
        niveau = "dangereux"

    conseils = [signal["conseil"] for signal in signaux if not signal["ok"]]

    return {
        "niveau": niveau,
        "signaux": signaux,
        "conseils": conseils,
        "urls_trouvees": urls,
        "nombre_signaux": nombre_signaux,
    }
