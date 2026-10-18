# Qualité et CI

[Sommaire](../README.md) · Précédent : [Ajouter un personnage](09-ajouter-un-personnage.md)

La CI GitHub Actions (`.github/workflows/ci.yml`) tourne à chaque push sur `main` et sur chaque pull
request. Tout ce qu'elle fait se lance aussi en local, avec les mêmes versions d'outils
(`requirements-dev.txt`).

## Ce qui est vérifié

| Contrôle | Outil | Configuration | Commande locale |
|---|---|---|---|
| Format GDScript | gdformat (gdtoolkit) | `gdformatrc`, 120 colonnes | `gdformat --check src tests` |
| Lint GDScript | gdlint (gdtoolkit) | `gdlintrc`, 120 colonnes | `gdlint src tests` |
| Format Python | ruff | `pyproject.toml`, 120 colonnes | `ruff format --check tools` |
| Lint Python | ruff | `pyproject.toml` : pycodestyle, pyflakes, imports, nommage, bugbear, syntaxe moderne | `ruff check tools` |
| Nommage | `tools/ci/check_naming.py` | liste de verbes dans le script | `python3 tools/ci/check_naming.py` |
| Tests unitaires du jeu | runner Godot | `tests/unit/` | `godot --headless --path . --fixed-fps 60 res://tests/test_runner.tscn -- --only=unit` |
| Tests de fonctionnalité du jeu | runner Godot | `tests/features/` | `... -- --only=features` |
| Couverture GDScript | `tools/ci/gd_coverage.py` | seuil 90 % | `python3 tools/ci/gd_coverage.py --fail-under 90` |
| Tests et couverture Python | pytest + pytest-cov | `pyproject.toml`, seuil 95 % | `pytest --cov --cov-fail-under=95` |

Pour corriger le format au lieu de seulement le vérifier : `gdformat src tests` et
`ruff format tools`.

## Jobs

| Job | Étapes |
|---|---|
| `quality` | Format et lint GDScript, format et lint Python, règle de nommage. |
| `python-tests` | Tests des outils (unitaires et fonctionnalité) avec couverture par ligne. |
| `godot-tests` | Téléchargement de Godot 4.7.2 pour Linux (mis en cache), import du projet, tests unitaires, tests de fonctionnalité, couverture GDScript. |

Les seuils de couverture sont des planchers, définis en tête du workflow (`GDSCRIPT_COVERAGE_MIN`,
`PYTHON_COVERAGE_MIN`). On les remonte quand la couverture monte ; on ne les baisse jamais pour
faire passer un run.

## Règle de nommage

Une méthode est une action : son nom commence par un verbe qui dit ce qu'elle fait ou produit.

| La fonction... | Verbe |
|---|---|
| interroge et renvoie | `find_`, `list_`, `read_` |
| calcule à partir de ce qu'elle a | `compute_`, `build_`, `format_` |
| résout une indirection | `resolve_` |
| crée et renvoie | `create_`, `make_`, `build_` |
| change un état | `update_`, `apply_`, `set_`, `register_` |
| répond oui ou non | `is_`, `has_`, `can_`, `should_` |

Les variables portent un nom explicite ; une seule lettre n'est admise que pour les coordonnées
`x` et `y`.

`check_naming.py` lit le GDScript de `src/` et `tests/` (signatures, `var`, `for`, paramètres) et le
Python de `tools/` (arbre syntaxique). Exemptions :

- les fonctions virtuelles de Godot (`_ready`, `_physics_process`...) ;
- les gestionnaires de signaux `_on_*` ;
- les méthodes spéciales Python (`__init__`...) ;
- les propriétés Python (`@property`), qui sont des valeurs et non des actions.

Si un vrai verbe manque à la liste, on l'ajoute à `VERBS` ; on ne renomme jamais une fonction en
nom pour contourner la règle.

## Couverture GDScript

Godot 4 n'a pas d'outil de couverture par ligne ; `gd_coverage.py` mesure donc la **couverture par
fonction**, ce qui est dit tel quel dans son rapport :

1. le projet est copié dans un dossier temporaire (les sources ne sont jamais modifiées) ;
2. une sonde `CoverageProbe.hit("<fichier>:<fonction>")` est insérée en tête de chaque fonction de
   `src/` (les fonctions abstraites, sans corps, ne comptent pas) ;
3. toutes les suites tournent dans la copie ;
4. le rapport donne, par fichier, les fonctions exécutées et la liste de celles qui ne l'ont pas
   été. En CI, il est aussi publié dans le résumé du job.

Les fonctions qui restent non couvertes changent de scène ou terminent le match : les exécuter
remplacerait le runner de tests.

## Avant de pousser

```bash
gdformat src tests && ruff format tools
gdlint src tests && ruff check tools && python3 tools/ci/check_naming.py
pytest --cov --cov-fail-under=95
godot --headless --path . --fixed-fps 60 res://tests/test_runner.tscn
```
