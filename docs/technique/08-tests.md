# Tests

[Sommaire](../README.md) · Précédent : [Pipeline d'assets](07-assets.md) · Suivant : [Ajouter un personnage](09-ajouter-un-personnage.md)

Deux familles de tests, côté jeu (GDScript) et côté outils (Python), chacune séparée en tests
unitaires et en tests de fonctionnalité. La couverture et la CI sont décrites dans
[Qualité et CI](10-qualite-et-ci.md).

## Lancer les tests du jeu

```bash
godot --headless --path . --fixed-fps 60 res://tests/test_runner.tscn
godot --headless --path . --fixed-fps 60 res://tests/test_runner.tscn -- --only=unit
godot --headless --path . --fixed-fps 60 res://tests/test_runner.tscn -- --only=features
```

Code de sortie 1 en cas d'échec, ou si aucun test n'a tourné. Chaque test est listé par son nom,
puis le total :

```
# test_knockback_formula.gd
  ok   test_force_grows_with_damage
  ...
38 tests, 0 failed
```

Ne jamais se fier au total seul : un fichier qui ne se charge pas n'apporte aucun test. Lire les
noms.

## Fonctionnement

| Élément | Rôle |
|---|---|
| `tests/test_case.gd` | Base minimale : `assert_true`, `assert_equal`, et `run_scenarios(host)` à surcharger. |
| `tests/test_runner.gd` | Découvre les suites par dossier (`tests/unit`, `tests/features`), les exécute, affiche le rapport. Une suite ajoutée tourne sans être enregistrée nulle part. |
| `tests/unit/` | Tests synchrones : chaque méthode `test_*` est appelée. |
| `tests/features/` | Scénarios asynchrones dans l'arbre de scène, avec de vraies frames physiques et de vrais évènements d'entrée. |

Un scénario est une méthode `_test_*` lancée par `run_scenarios(host)`, dont le nom est déclaré
dans la méta `scenario_names`. Ses messages d'échec commencent par ce nom.

Deux précautions pour les scénarios :

- **Détacher avant de libérer.** Un nœud mis en file avec `queue_free` reste dans l'arbre jusqu'à la
  fin de la frame. Son `CombatResolver`, qui lit le groupe global `hit_volumes`, pourrait alors faire
  toucher un combattant périmé au scénario suivant. D'où `_dispose(host, scene)`.
- **Ne jamais changer de scène.** `change_scene_to_file` remplacerait le runner lui-même. Les
  scénarios d'écran s'arrêtent donc avant de valider un choix qui lancerait le combat.

## Suites du jeu

### Unitaires

| Suite | Ce qu'elle protège |
|---|---|
| `test_knockback_formula` | La projection grandit avec les dégâts, diminue avec le poids, part vers le haut, a pour norme la force ; hitstun proportionnel. |
| `test_attack_data` | Les phases suivent la timeline. |
| `test_bot_brain` | Poursuite, attaque à portée, retour vers l'arène, refus de tomber. |
| `test_keyboard_input_source` | Les touches maintenues deviennent un `InputFrame` ; chaque action a un libellé de touche. |
| `test_selection_cursor` | Le curseur boucle sur le roster et se verrouille une fois validé. |
| `test_match_config` | Qui est bot dans chaque mode, schéma de touches de chaque slot, aucune touche en double, chaque slot a son curseur et son marqueur. |
| `test_roster` | Six identifiants distincts, planches conformes à `layout.json`, coups complets, jauges entre 1 et 5. |
| `test_ui_text` | La police sait dessiner chaque texte et chaque nom de personnage. |
| `test_stage_layers` | Les plateformes sont sur la couche que les combattants traversent ; chaque couche animée a son nœud et une planche découpable. |
| `test_fighter_visuals` | L'ombre est pleine au sol, la plus petite à hauteur max, et ne grandit jamais en montant. |
| `test_docs` | Chaque personnage du roster figure dans le README et la page Personnages ; chaque lien relatif des docs pointe vers un fichier existant ; aucun terme d'une autre licence (liste dans `CONTRIBUTING.md`) dans le code, les données ou la doc. |

### Fonctionnalités

| Suite | Scénarios |
|---|---|
| `test_match_flow` | Un coup au corps à corps ne touche qu'une fois ; un projectile touche une fois puis disparaît ; un KO coûte une vie et le combattant réapparaît dans l'arène à 0 % ; deux bots s'affrontent 2 400 ticks sans erreur. |
| `test_screens` | Le menu propose trois choix et rappelle les commandes ; la sélection déplace le curseur et valide le joueur 1 ; l'écran de victoire nomme le vainqueur et la durée ; Échap met et retire la pause. |

## Tests des outils Python

```bash
pip install -r requirements-dev.txt
pytest --cov --cov-report=term-missing
```

`tools/tests/`, configuré dans `pyproject.toml` :

| Fichier | Ce qu'il protège |
|---|---|
| `test_pixel.py` | Mélange de couleurs exact aux deux bouts ; le voile garde la transparence. |
| `test_fighters.py` | La cinématique inverse garde la longueur des segments ou ramène une main hors de portée ; `layout.json` compte chaque pose une fois ; chaque planche a la bonne taille et reste dans son cadre. |
| `test_stage.py` | Les couches animées se découpent en images entières ; les rayons de l'éclat de KO ne débordent pas. |
| `test_generated_assets.py` | **Fonctionnalité** : les assets versionnés sont exactement ce que le générateur produit (pixels comparés). Échoue si on a changé le dessin sans régénérer. |
| `test_preview.py` | L'agrandissement garde des pixels carrés. |
| `test_check_naming.py` | La règle de nommage elle-même, et le dépôt entier qui la respecte. |
| `test_gd_coverage.py` | L'instrumenteur de couverture GDScript : sondes au bon endroit, rien d'autre de modifié. |

## Conventions

- **Arrange / Act / Assert** commentés dans chaque test.
- **Données générées** : les valeurs qui ne pilotent pas le test sont tirées au hasard
  (`RandomNumberGenerator`, `random.Random`) plutôt qu'écrites en dur.
- **Pas de mocks** : le cerveau du bot est testé sur une `BotPerception` réelle, les scénarios sur de
  vraies scènes, le générateur sur ses vraies sorties.
- **Une règle qui peut se vérifier devient un test.** Quand deux représentations d'une même
  information existent (Python et Godot, texte et police, code et doc), un test échoue si elles
  divergent.
- **Prouver qu'un test mord.** Un nouveau test doit avoir été vu en échec (casser volontairement,
  voir le rouge, restaurer).

## Vérifier le visuel

Une suite verte ne prouve rien sur le rendu. Pour capturer un écran réel (avec fenêtre, pas en
headless), le writer vidéo de Godot écrit une image par frame :

```bash
godot --path . --resolution 1440x810 --write-movie /tmp/shot.png --fixed-fps 60 --quit-after 200 res://scenes/fight.tscn -- --demo
```
