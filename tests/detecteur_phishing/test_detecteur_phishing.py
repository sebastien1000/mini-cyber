"""
Tests pour la mini app "Détecteur de phishing".

Chaque fonction dont le nom commence par test_ est un test.
pytest les lance toutes et affiche celles qui échouent.

Pour les lancer : ./venv/bin/python -m pytest
"""

from mini_apps.detecteur_phishing import analyser, extraire_urls


def test_message_sans_signal_est_sur():
    resultat = analyser("Bonjour Sébastien, voici le compte-rendu de notre réunion d'hier. À bientôt !")
    assert resultat["niveau"] == "sûr"
    assert resultat["nombre_signaux"] == 0


def test_extraire_urls_trouve_les_liens():
    texte = "Clique ici : http://exemple-test.com/verif et aussi sur bit.ly/abc123."
    urls = extraire_urls(texte)
    assert "http://exemple-test.com/verif" in urls
    assert any(url.startswith("bit.ly") for url in urls)


def test_detecte_une_adresse_ip():
    resultat = analyser("Connecte-toi vite sur http://192.168.1.50/login pour vérifier ton compte.")
    labels_en_echec = [s["label"] for s in resultat["signaux"] if not s["ok"]]
    assert "Aucun lien ne pointe vers une adresse IP" in labels_en_echec


def test_detecte_un_raccourcisseur():
    resultat = analyser("Regarde vite : http://bit.ly/xyz")
    labels_en_echec = [s["label"] for s in resultat["signaux"] if not s["ok"]]
    assert "Aucun lien ne passe par un raccourcisseur d'URL" in labels_en_echec


def test_detecte_un_arobase_avec_une_adresse_ip_avant():
    # Cas piège : une IP suivie d'un @ suivi d'un vrai domaine, le tout doit être
    # reconnu comme UN SEUL lien (et pas coupé en deux morceaux au niveau du @).
    resultat = analyser("Vérifie ton compte : http://192.168.1.1@faux-banque.com/verif")
    assert resultat["urls_trouvees"] == ["http://192.168.1.1@faux-banque.com/verif"]
    labels_en_echec = [s["label"] for s in resultat["signaux"] if not s["ok"]]
    assert "Aucun lien ne contient de @ suspect" in labels_en_echec


def test_detecte_un_arobase_suspect():
    resultat = analyser("Vérifie ton compte : http://paypal.com@faux-site.net/login")
    labels_en_echec = [s["label"] for s in resultat["signaux"] if not s["ok"]]
    assert "Aucun lien ne contient de @ suspect" in labels_en_echec


def test_detecte_une_marque_imitee():
    resultat = analyser("Connecte-toi sur http://paypal-securite-login.com/verif")
    labels_en_echec = [s["label"] for s in resultat["signaux"] if not s["ok"]]
    assert "Aucun lien n'imite le nom d'une marque connue" in labels_en_echec


def test_sous_domaine_legitime_nest_pas_signale():
    resultat = analyser("Va sur https://www.paypal.com/login pour te connecter.")
    labels_en_echec = [s["label"] for s in resultat["signaux"] if not s["ok"]]
    assert "Aucun lien n'imite le nom d'une marque connue" not in labels_en_echec


def test_detecte_urgence_et_donnees_sensibles():
    resultat = analyser(
        "Cher client, votre compte sera suspendu sous 24h. Merci de confirmer votre mot de passe immédiatement."
    )
    labels_en_echec = [s["label"] for s in resultat["signaux"] if not s["ok"]]
    assert "Pas de sentiment d'urgence excessif" in labels_en_echec
    assert "Ne demande pas d'informations sensibles" in labels_en_echec
    assert "Salutation personnalisée (pas générique)" in labels_en_echec


def test_detecte_urgence_et_donnees_sensibles_sans_accents():
    # Beaucoup de SMS sont tapés vite, sans accents : les mots-clés doivent quand
    # même être détectés (ex: "immediatement" doit matcher "immédiatement").
    resultat = analyser(
        "Cher client, votre compte sera suspendu sous 24h. Merci de confirmer votre mot de passe immediatement."
    )
    labels_en_echec = [s["label"] for s in resultat["signaux"] if not s["ok"]]
    assert "Pas de sentiment d'urgence excessif" in labels_en_echec
    assert "Ne demande pas d'informations sensibles" in labels_en_echec
    assert "Salutation personnalisée (pas générique)" in labels_en_echec


def test_message_avec_plusieurs_signaux_est_dangereux():
    resultat = analyser(
        "Cher client, votre compte sera bloqué sous 24h. "
        "Confirmez votre mot de passe ici : http://192.168.1.1@faux-banque.com/verif"
    )
    assert resultat["niveau"] == "dangereux"
    assert resultat["nombre_signaux"] >= 3


def test_texte_vide_est_sur():
    resultat = analyser("")
    assert resultat["niveau"] == "sûr"
    assert resultat["urls_trouvees"] == []
