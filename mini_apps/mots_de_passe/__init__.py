"""
Mini app : Mots de passe.
"""

import secrets
import string

INFO = {
    "nom": "Mots de passe",
    "icone": "🔑",
    "description": "Générer un mot de passe solide, ou vérifier la robustesse d'un mot de passe.",
}


# Les types de caractères disponibles, avec un nom court pour les formulaires
TYPES_CARACTERES = {
    "min": string.ascii_lowercase,
    "maj": string.ascii_uppercase,
    "chiffres": string.digits,
    "symboles": string.punctuation,
}


def generer(longueur=16, types=None):
    """Crée un mot de passe aléatoire à partir des types de caractères choisis."""
    if not types:
        types = ["min", "maj", "chiffres", "symboles"]  # par défaut, on utilise tout

    categories = [TYPES_CARACTERES[t] for t in types if t in TYPES_CARACTERES]
    longueur = max(longueur, len(categories))  # sinon on ne peut pas caser une catégorie par caractère

    # 1. on force un caractère de chaque catégorie choisie, pour être sûr de toutes les avoir
    mot = [secrets.choice(categorie) for categorie in categories]

    # 2. on complète le reste au hasard, parmi tous les caractères possibles
    tous_caracteres = "".join(categories)
    mot += [secrets.choice(tous_caracteres) for _ in range(longueur - len(mot))]

    # 3. on mélange, sinon les premiers caractères suivraient toujours le même ordre
    secrets.SystemRandom().shuffle(mot)

    return "".join(mot)


# Une petite liste de mots simples, pour le mode "mémorisable"
# fmt: off
MOTS_SIMPLES = [
    "cheval", "tigre", "lampe", "montagne", "riviere", "nuage", "soleil", "lune",
    "etoile", "foret", "rocher", "sable", "vague", "orage", "vent", "feuille",
    "arbre", "fleur", "jardin", "maison", "porte", "fenetre", "table", "chaise",
    "livre", "crayon", "papier", "cle", "montre", "clavier", "ecran", "ombre",
    "miroir", "chemin", "pont", "tour", "chateau", "epee", "bouclier", "dragon",
    "aigle", "loup", "renard", "ours", "lion", "serpent", "tortue", "dauphin",
    "baleine", "requin", "poisson", "oiseau", "papillon", "abeille", "fourmi",
    "hibou", "corbeau", "faucon", "cygne", "canard", "vache", "mouton", "chevre",
    "lapin", "ecureuil", "herisson", "cerf", "chameau", "elephant", "girafe",
    "zebre", "singe", "panda", "jaguar", "leopard", "crocodile", "eclair",
    "tonnerre", "tempete", "givre", "glace", "neige", "printemps", "automne",
    "hiver", "matin", "minuit", "seconde", "planete", "comete", "galaxie",
    "fusee", "robot", "machine", "moteur", "bateau", "avion", "train", "voiture",
    "velo", "route", "vallee", "plaine", "desert", "ocean", "lac", "ile",
    "village", "marche", "ecole", "musee", "theatre", "cinema", "stade",
]
# fmt: on


def generer_memorisable(nombre_mots=4):
    """Crée un mot de passe façon 'Cheval-Tigre-Lampe-42' : facile à retenir, et 'très fort'."""
    # .capitalize() met une majuscule au début du mot : ça ajoute le critère
    # "majuscule" à la vérification, sans nuire à la lisibilité
    mots = [secrets.choice(MOTS_SIMPLES).capitalize() for _ in range(nombre_mots)]
    nombre = secrets.randbelow(100)  # un nombre entre 0 et 99
    return "-".join(mots) + f"-{nombre}"


def proposer_amelioration(mot_de_passe):
    """À partir d'un mot de passe existant, propose une version plus robuste
    qui garde le début reconnaissable (ex: 'bonjour' -> 'bonjourT4!-Renard')."""
    base = mot_de_passe or secrets.choice(MOTS_SIMPLES)

    # on ajoute ce qui manque le plus souvent : une majuscule, un chiffre, un symbole
    ajouts = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation),
    ]
    secrets.SystemRandom().shuffle(ajouts)

    proposition = base + "".join(ajouts)

    # si c'est encore trop court, on ajoute des mots jusqu'à atteindre 16 caractères
    while len(proposition) < 16:
        proposition += "-" + secrets.choice(MOTS_SIMPLES).capitalize()

    return proposition


# Les mots de passe les plus utilisés au monde : les premiers essayés par les pirates.
# On utilise un set (et pas une liste) car la recherche "est-ce que X est dedans ?" y est plus rapide.
# fmt: off
MOTS_DE_PASSE_COURANTS = {
    "123456", "123456789", "12345678", "12345", "1234567", "1234", "111111",
    "000000", "123123", "abc123", "qazwsx", "1q2w3e4r",
    "password", "passw0rd", "letmein", "welcome", "login", "master",
    "monkey", "dragon", "football", "baseball", "superman", "batman",
    "trustno1", "iloveyou", "sunshine", "princess", "starwars", "computer",
    "azerty", "azerty123", "qwerty", "qwerty123", "motdepasse", "bienvenue",
    "soleil", "bonjour", "chocolat", "marseille", "france",
}
# fmt: on


def _normaliser(texte):
    """Ne garde que les lettres, en minuscules : 'Azerty2024!' devient 'azerty'."""
    return "".join(c for c in texte.lower() if c.isalpha())


# On précalcule les versions "nettoyées" de la liste, une seule fois au démarrage
_MOTS_DE_PASSE_COURANTS_NORMALISES = {_normaliser(mdp) for mdp in MOTS_DE_PASSE_COURANTS if _normaliser(mdp)}


def analyser(mot_de_passe):
    """Évalue un mot de passe et explique ce qui pourrait être amélioré.

    Retourne un dictionnaire avec :
    - niveau : 'faible', 'moyen', 'fort' ou 'très fort'
    - criteres : la liste des critères testés (rempli ou non)
    - conseils : les conseils pour les critères qui manquent
    """
    criteres = [
        {
            "label": "Au moins 8 caractères",
            "ok": len(mot_de_passe) >= 8,
            "conseil": "Utilise au moins 8 caractères.",
        },
        {
            "label": "Au moins 16 caractères",
            "ok": len(mot_de_passe) >= 16,
            "conseil": "Vise 16 caractères ou plus pour une sécurité maximale.",
        },
        {
            "label": "Contient une minuscule",
            "ok": any(c.islower() for c in mot_de_passe),
            "conseil": "Ajoute au moins une lettre minuscule.",
        },
        {
            "label": "Contient une majuscule",
            "ok": any(c.isupper() for c in mot_de_passe),
            "conseil": "Ajoute au moins une lettre MAJUSCULE.",
        },
        {
            "label": "Contient un chiffre",
            "ok": any(c.isdigit() for c in mot_de_passe),
            "conseil": "Ajoute au moins un chiffre.",
        },
        {
            "label": "Contient un symbole",
            "ok": any(c in string.punctuation for c in mot_de_passe),
            "conseil": "Ajoute au moins un symbole, comme ! @ # ou -.",
        },
    ]

    score = sum(1 for critere in criteres if critere["ok"])

    if score <= 2:
        niveau = "faible"
    elif score <= 4:
        niveau = "moyen"
    elif score <= 5:
        niveau = "fort"
    else:
        niveau = "très fort"

    # Un mot de passe très courant (ou une variante, ex: "Soleil123!") reste
    # dangereux même s'il coche toutes les cases au-dessus
    est_courant = mot_de_passe.lower() in MOTS_DE_PASSE_COURANTS
    mdp_normalise = _normaliser(mot_de_passe)
    est_variante_courante = bool(mdp_normalise) and mdp_normalise in _MOTS_DE_PASSE_COURANTS_NORMALISES
    est_trop_previsible = est_courant or est_variante_courante

    criteres.append(
        {
            "label": "N'est pas un mot de passe trop courant (ni une variante)",
            "ok": not est_trop_previsible,
            "conseil": (
                "Ce mot de passe fait partie des plus utilisés au monde (ou en est une "
                "variante proche) : change-le, même s'il te semble complexe."
            ),
        }
    )

    if est_trop_previsible:
        niveau = "faible"

    conseils = [critere["conseil"] for critere in criteres if not critere["ok"]]

    return {
        "niveau": niveau,
        "criteres": criteres,
        "conseils": conseils,
        "mot_de_passe_courant": est_trop_previsible,
    }
