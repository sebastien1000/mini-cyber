"""
Le CHARGEUR de mini apps.

Son travail : regarder tous les fichiers/dossiers de mini_apps/,
et pour chacun :
- récupérer sa carte d'identité (INFO), pour l'afficher sur l'accueil
- brancher ses routes web (routes.py) sur l'application, si elle en a

On ne touchera JAMAIS ce fichier pour ajouter une mini app.
"""

import importlib
import importlib.util
import pkgutil


def charger_mini_apps():
    apps = {}

    # pkgutil.iter_modules regarde tous les fichiers/dossiers de mini_apps/
    for module_info in pkgutil.iter_modules(__path__):
        nom_fichier = module_info.name

        # on ignore les fichiers qui commencent par _ (comme ce fichier-ci)
        if nom_fichier.startswith("_"):
            continue

        # on importe le fichier/dossier, comme un "import mini_apps.nom_fichier"
        module = importlib.import_module(f"mini_apps.{nom_fichier}")

        # on ne garde que ceux qui ont bien une variable INFO
        if hasattr(module, "INFO"):
            apps[nom_fichier] = module.INFO

    return apps


def enregistrer_routes(app):
    """Cherche un fichier routes.py dans chaque mini app, et branche son
    Blueprint sur l'application Flask, s'il y en a un."""
    for module_info in pkgutil.iter_modules(__path__):
        nom_fichier = module_info.name

        if nom_fichier.startswith("_"):
            continue

        chemin_routes = f"mini_apps.{nom_fichier}.routes"

        # find_spec vérifie que le fichier existe, SANS l'importer
        # (une mini app qui n'a pas encore de routes.py, ce n'est pas une erreur)
        if importlib.util.find_spec(chemin_routes) is None:
            continue

        module_routes = importlib.import_module(chemin_routes)

        if hasattr(module_routes, "blueprint"):
            app.register_blueprint(module_routes.blueprint)
