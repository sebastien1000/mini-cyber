"""
Tests pour la mini app "Mots de passe".

Chaque fonction dont le nom commence par test_ est un test.
pytest les lance toutes et affiche celles qui échouent.

Pour les lancer : ./venv/bin/python -m pytest
"""
from mini_apps.mots_de_passe import generer, generer_memorisable, analyser


def test_generer_respecte_la_longueur():
    mot_de_passe = generer(longueur=20)
    assert len(mot_de_passe) == 20


def test_generer_avec_un_seul_type_de_caracteres():
    # Si on ne demande que des chiffres, il ne doit y avoir QUE des chiffres
    mot_de_passe = generer(longueur=10, types=["chiffres"])
    assert mot_de_passe.isdigit()


def test_generer_contient_tous_les_types_demandes():
    mot_de_passe = generer(longueur=16, types=["min", "maj", "chiffres", "symboles"])
    assert any(c.islower() for c in mot_de_passe)
    assert any(c.isupper() for c in mot_de_passe)
    assert any(c.isdigit() for c in mot_de_passe)


def test_generer_est_toujours_tres_fort():
    mot_de_passe = generer()
    assert analyser(mot_de_passe)["niveau"] == "très fort"


def test_generer_memorisable_est_toujours_tres_fort():
    mot_de_passe = generer_memorisable()
    assert analyser(mot_de_passe)["niveau"] == "très fort"


def test_analyser_mot_de_passe_court_est_faible():
    resultat = analyser("abc")
    assert resultat["niveau"] == "faible"


def test_analyser_detecte_un_mot_de_passe_courant():
    resultat = analyser("azerty")
    assert resultat["mot_de_passe_courant"] is True
    assert resultat["niveau"] == "faible"


def test_analyser_detecte_une_variante_dun_mot_de_passe_courant():
    # "Azerty2024!" a l'air complexe, mais reste juste "azerty" déguisé
    resultat = analyser("Azerty2024!")
    assert resultat["mot_de_passe_courant"] is True


def test_analyser_mot_de_passe_solide_nest_pas_signale_comme_courant():
    resultat = analyser("Xk9$mPqR2vLtZ8bN")
    assert resultat["mot_de_passe_courant"] is False
