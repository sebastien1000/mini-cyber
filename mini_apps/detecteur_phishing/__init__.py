"""
Mini app : Détecteur de phishing.
"""

import ipaddress
import re
import unicodedata
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


def _normaliser_texte(texte):
    """Minuscules et sans accents : 'Immédiatement' et 'immediatement' deviennent identiques.

    Beaucoup de SMS/emails sont tapés vite, sans accents : sans cette étape, un mot-clé
    comme 'immédiatement' ne détecterait pas 'immediatement'.
    """
    texte = texte.lower()
    texte_decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in texte_decompose if not unicodedata.combining(c))


# On précalcule les versions "sans accents" des mots-clés, une seule fois au démarrage
_MOTS_URGENCE_NORMALISES = [_normaliser_texte(mot) for mot in MOTS_URGENCE]
_MOTS_DONNEES_SENSIBLES_NORMALISES = [_normaliser_texte(mot) for mot in MOTS_DONNEES_SENSIBLES]
_SALUTATIONS_GENERIQUES_NORMALISEES = [_normaliser_texte(mot) for mot in SALUTATIONS_GENERIQUES]


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


def _distance_levenshtein(a, b):
    """Nombre minimal de lettres à ajouter/enlever/changer pour passer de a à b."""
    longueur_b = len(b)
    ligne_precedente = list(range(longueur_b + 1))

    for i, lettre_a in enumerate(a, start=1):
        ligne_courante = [i] + [0] * longueur_b
        for j, lettre_b in enumerate(b, start=1):
            cout_substitution = 0 if lettre_a == lettre_b else 1
            ligne_courante[j] = min(
                ligne_precedente[j] + 1,  # suppression
                ligne_courante[j - 1] + 1,  # insertion
                ligne_precedente[j - 1] + cout_substitution,  # substitution
            )
        ligne_precedente = ligne_courante

    return ligne_precedente[longueur_b]


def _ressemble_a_une_marque(morceau, marque):
    """Vrai si un morceau du domaine contient la marque, ou une faute de frappe très proche
    (ex: 'paypa1', 'paypall' pour 'paypal'). Les marques trop courtes (ex: 'free') sont
    exclues de la comparaison approximative pour éviter de signaler des mots ordinaires."""
    if marque in morceau:
        return True
    return len(marque) >= 5 and _distance_levenshtein(morceau, marque) <= 1


def _imite_une_marque(hote):
    """Vrai si l'hôte imite le nom d'une marque connue sans être (un sous-domaine de) son vrai domaine."""
    if not hote:
        return False
    for marque, domaine_officiel in MARQUES_CONNUES.items():
        if hote == domaine_officiel or hote.endswith("." + domaine_officiel):
            continue  # c'est le vrai domaine (ou un de ses sous-domaines) : rien à signaler
        if any(_ressemble_a_une_marque(morceau, marque) for morceau in hote.split(".")):
            return True
    return False


def _contient_un_mot(texte_minuscule, mots):
    return any(mot in texte_minuscule for mot in mots)


def _signaux_liens(urls):
    """Les 5 signaux propres aux liens trouvés (utilisables seuls, sans texte de message autour)."""
    hotes = [_hote(url) for url in urls]

    url_ip = any(_est_adresse_ip(hote) for hote in hotes)
    url_raccourci = any(hote in RACCOURCISSEURS_CONNUS for hote in hotes)
    url_arobase = any("@" in url for url in urls)
    url_sans_https = any(url.lower().startswith("http://") for url in urls)
    url_imite_marque = any(_imite_une_marque(hote) for hote in hotes)

    return [
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
                "Un domaine comme paypal-securite-login.com (ou une faute de frappe comme "
                "paypa1.com) n'est PAS le vrai site PayPal : seul paypal.com (ou un de ses "
                "sous-domaines) l'est."
            ),
        },
    ]


def _signaux_texte(texte_normalise):
    """Les 4 signaux propres au contenu d'un message (urgence, ton, pièces jointes...)."""
    return [
        {
            "label": "Pas de sentiment d'urgence excessif",
            "ok": not _contient_un_mot(texte_normalise, _MOTS_URGENCE_NORMALISES),
            "conseil": (
                "Créer un sentiment d'urgence ('agis maintenant', 'compte bloqué'...) "
                "est une technique classique pour empêcher de réfléchir."
            ),
        },
        {
            "label": "Ne demande pas d'informations sensibles",
            "ok": not _contient_un_mot(texte_normalise, _MOTS_DONNEES_SENSIBLES_NORMALISES),
            "conseil": "Une organisation sérieuse ne demande jamais un mot de passe ou un code de carte par email/SMS.",
        },
        {
            "label": "Salutation personnalisée (pas générique)",
            "ok": not _contient_un_mot(texte_normalise, _SALUTATIONS_GENERIQUES_NORMALISEES),
            "conseil": "'Cher client' à la place de ton prénom peut indiquer un envoi de masse frauduleux.",
        },
        {
            "label": "Pas de pièce jointe à un format à risque",
            "ok": not _contient_un_mot(texte_normalise, EXTENSIONS_DANGEREUSES),
            "conseil": (
                "Les formats .exe, .js, .zip, .scr... peuvent contenir des virus : "
                "ne les ouvre jamais sans certitude sur leur origine."
            ),
        },
    ]


def _construire_resultat(signaux, urls):
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


def analyser(texte):
    """Analyse un texte (email, SMS...) et repère les signaux classiques de phishing.

    Retourne un dictionnaire avec :
    - niveau : 'sûr', 'suspect' ou 'dangereux'
    - signaux : la liste des critères testés (respecté ou non)
    - conseils : les explications des signaux détectés
    - urls_trouvees : les liens repérés dans le texte
    """
    texte = texte or ""
    urls = extraire_urls(texte)
    signaux = _signaux_liens(urls) + _signaux_texte(_normaliser_texte(texte))
    return _construire_resultat(signaux, urls)


def analyser_url(url):
    """Analyse un lien seul (sans texte de message autour) : ne vérifie que les 5 signaux
    propres aux liens (pas l'urgence, la salutation... qui n'ont pas de sens pour un lien seul)."""
    urls = extraire_urls(url or "")
    signaux = _signaux_liens(urls)
    return _construire_resultat(signaux, urls)
