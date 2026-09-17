# Mon projet Cyber

[![CI](https://github.com/sebastien1000/mini-cyber/actions/workflows/ci.yml/badge.svg)](https://github.com/sebastien1000/mini-cyber/actions/workflows/ci.yml)

Une petite boîte à outils web, en Flask, réunissant plusieurs "mini apps" autour de la cybersécurité.

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt   # inclut Flask + les outils de dev (pytest, ruff)
cp .env.example .env                  # config locale (voir .env.example)
```

## Lancer le projet

```bash
./venv/bin/python app.py
```

Puis ouvre http://127.0.0.1:5000 dans ton navigateur.

## Lancer les tests

```bash
./venv/bin/python -m pytest
```

## Vérifier le style du code

Le projet utilise [ruff](https://docs.astral.sh/ruff/) pour le linting et le formatage.

```bash
./venv/bin/ruff check .           # détecte les erreurs et le code suspect
./venv/bin/ruff format .          # reformate le code automatiquement
```

Ces vérifications (+ les tests) tournent aussi automatiquement sur GitHub Actions à chaque push (voir `.github/workflows/ci.yml`).

## Configuration

La config (mode debug, clé secrète) se fait via des variables d'environnement, lues depuis un fichier `.env` local (non commité, voir `.env.example` pour les valeurs possibles).

## Mini apps disponibles

- 🔑 **Mots de passe** (`/mots_de_passe`) : générer un mot de passe solide (aléatoire ou mémorisable), ou vérifier la robustesse d'un mot de passe existant.

## Structure du projet

```
app.py                  # Le conteneur : page d'accueil, lance l'app Flask
mini_apps/
  __init__.py           # Le chargeur : détecte automatiquement les mini apps
  <nom_de_la_mini_app>/
    __init__.py          # Logique pure (INFO, fonctions)
    routes.py             # Routes Flask (formulaires, pages)
templates/
  accueil.html
  <nom_de_la_mini_app>/
static/
  style.css
  <nom_de_la_mini_app>/
tests/
  <nom_de_la_mini_app>/
```

## Ajouter une nouvelle mini app

Pas besoin de toucher à `app.py` ni à `mini_apps/__init__.py` : ils détectent automatiquement les mini apps présentes.

1. Crée un dossier `mini_apps/<nom_de_la_mini_app>/`.
2. Dans son `__init__.py`, définis un dictionnaire `INFO` :
   ```python
   INFO = {
       "nom": "Nom affiché",
       "icone": "🔒",
       "description": "Ce que fait la mini app.",
   }
   ```
3. Si la mini app a des pages web, ajoute un `routes.py` avec un `Blueprint` nommé `blueprint`.
4. Ajoute les templates dans `templates/<nom_de_la_mini_app>/` et les fichiers statiques dans `static/<nom_de_la_mini_app>/`.
5. (Optionnel mais recommandé) Ajoute des tests dans `tests/<nom_de_la_mini_app>/`.

La mini app apparaît alors automatiquement sur la page d'accueil.
