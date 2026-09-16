"""
Le CHARGEUR de mini apps.

Son travail : regarder tous les fichiers .py dans ce dossier,
et les ranger dans un dictionnaire pour que le site puisse les afficher.

On ne touchera JAMAIS ce fichier pour ajouter une mini app.
"""
import importlib
import pkgutil


def charger_mini_apps():
    apps = {}

    # pkgutil.iter_modules regarde tous les fichiers .py de ce dossier
    for module_info in pkgutil.iter_modules(__path__):
        nom_fichier = module_info.name

        # on ignore les fichiers qui commencent par _ (comme ce fichier-ci)
        if nom_fichier.startswith("_"):
            continue

        # on importe le fichier, comme un "import mini_apps.nom_fichier"
        module = importlib.import_module(f"mini_apps.{nom_fichier}")

        # on ne garde que les fichiers qui ont bien une variable INFO
        if hasattr(module, "INFO"):
            apps[nom_fichier] = module.INFO

    return apps
