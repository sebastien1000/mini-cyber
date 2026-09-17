# Mon projet Cyber

Une petite boîte à outils web, en Flask, réunissant plusieurs "mini apps" autour de la cybersécurité.

## Lancer le projet

```bash
python -m venv venv
source venv/bin/activate
pip install flask
python app.py
```

Puis ouvre http://127.0.0.1:5000 dans ton navigateur.

## Lancer les tests

```bash
./venv/bin/python -m pytest
```

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
