# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app (http://127.0.0.1:5000)
./venv/bin/python app.py

# Run all tests
./venv/bin/python -m pytest

# Run a single test file / test
./venv/bin/python -m pytest tests/mots_de_passe/test_mots_de_passe.py
./venv/bin/python -m pytest tests/mots_de_passe/test_mots_de_passe.py::test_generer_respecte_la_longueur
```

There is no lint/format tooling configured in this repo.

## Architecture

This is a French-language Flask app that hosts a growing collection of independent "mini apps" (small cybersecurity tools), each self-contained in its own folder. The key design goal is that **adding a new mini app never requires touching `app.py` or `mini_apps/__init__.py`** — they auto-discover mini apps at startup.

### Auto-discovery mechanism (`mini_apps/__init__.py`)

- `charger_mini_apps()` iterates every submodule of `mini_apps/` (via `pkgutil.iter_modules`), imports it, and collects its `INFO` dict (name, icon, description) if present. This powers the home page cards.
- `enregistrer_routes(app)` checks each mini app folder for a `routes.py`; if found and it exposes a `blueprint`, it's registered on the Flask app.
- Folders/files starting with `_` are skipped.

### Per-mini-app convention

Each mini app lives at `mini_apps/<name>/` and follows a strict separation:
- `__init__.py` — pure logic only (no Flask imports). Must define `INFO = {"nom": ..., "icone": ..., "description": ...}`. Functions here should be independently unit-testable.
- `routes.py` — Flask-facing layer only. Defines `blueprint = Blueprint(<name>, __name__)` and route handlers that call into the sibling `__init__.py` logic functions.

Templates go in `templates/<name>/`, static assets in `static/<name>/`, tests in `tests/<name>/`. `templates/accueil.html` links to each mini app via `/<name>` (i.e. the URL path is expected to match the mini app's folder name).

### Example: `mots_de_passe` mini app

Read this one as the reference implementation when adding a new mini app:
- `mini_apps/mots_de_passe/__init__.py` — password generation (`generer`, `generer_memorisable`, using `secrets`, never `random`, for anything security-sensitive) and strength analysis (`analyser`, which also checks against a common-password list including normalized/leetspeak variants via `_normaliser`).
- `mini_apps/mots_de_passe/routes.py` — single route `/mots_de_passe` (GET/POST) handling two form actions (`generer`, `verifier`) dispatched via a hidden `action` field on each `<form>`.

### Tests

Tests import directly from the mini app's logic module (e.g. `from mini_apps.mots_de_passe import generer, generer_memorisable, analyser`) — they test pure functions, not HTTP routes.
