# Tests

[Sommaire](../README.md) · Précédent : [Pipeline d'assets](07-assets.md) · Suivant : [Ajouter un personnage](09-ajouter-un-personnage.md)

## Lancer

```bash
godot --headless --path . --fixed-fps 60 res://tests/test_runner.tscn
```

Code de sortie 1 en cas d'échec. Chaque test est listé par son nom, puis le total :

```
# test_knockback_formula.gd
  ok   test_force_grows_with_damage
  ...
27 tests, 0 failed
```

Ne jamais se fier au total seul : un fichier qui ne se charge pas n'apporte aucun test. Lire les
noms.

## Fonctionnement

- `tests/test_case.gd` : base minimale, avec `assert_true` et `assert_equal`. Chaque méthode
  `test_*` d'une suite est appelée par le runner.
- `tests/test_runner.gd` : liste les suites (`SUITES`), les exécute, affiche le rapport et quitte
  avec le bon code.
- **Scénarios** : une suite peut surcharger `run_scenarios(host)` pour faire tourner de vraies frames
  physiques dans l'arbre de scène ; elle déclare leurs noms dans la méta `scenario_names`.

## Suites

| Suite | Ce qu'elle protège |
|---|---|
| `test_knockback_formula` | La projection grandit avec les dégâts, diminue avec le poids, part vers le haut, a pour norme la force ; hitstun proportionnel. |
| `test_attack_data` | Les phases suivent la timeline. |
| `test_bot_brain` | Poursuite, attaque à portée, retour vers l'arène, refus de tomber. |
| `test_selection_cursor` | Le curseur boucle sur le roster et se verrouille une fois validé. |
| `test_match_config` | Qui est bot dans chaque mode, schéma de touches de chaque slot, aucune touche en double, chaque slot a son curseur et son marqueur. |
| `test_roster` | Six identifiants distincts, planches conformes à `layout.json`, coups complets, jauges entre 1 et 5. |
| `test_ui_text` | La police sait dessiner chaque texte et chaque nom de personnage. |
| `test_stage_layers` | Les plateformes sont sur la couche que les combattants traversent ; chaque couche animée a son nœud et une planche découpable. |
| `test_fighter_visuals` | L'ombre est pleine au sol, la plus petite à hauteur max, et ne grandit jamais en montant. |
| `test_match_simulation` | Un coup au corps à corps ne touche qu'une fois ; deux bots s'affrontent 2 400 ticks sans erreur et se touchent. |

## Conventions

- **Arrange / Act / Assert** commentés dans chaque test.
- **Données générées** : les valeurs qui ne pilotent pas le test sont tirées au hasard
  (`RandomNumberGenerator`) plutôt qu'écrites en dur.
- **Pas de mocks** : le cerveau du bot est testé sur une `BotPerception` réelle, la simulation sur de
  vraies scènes.
- **Une règle qui peut se vérifier devient un test.** Quand deux représentations d'une même
  information existent (Python et Godot, texte et police), un test échoue si elles divergent.
- **Prouver qu'un test mord.** Un nouveau test doit avoir été vu en échec (casser volontairement,
  voir le rouge, restaurer).

## Vérifier le visuel

Une suite verte ne prouve rien sur le rendu. Pour capturer un écran réel (avec fenêtre, pas en
headless), le writer vidéo de Godot écrit une image par frame :

```bash
godot --path . --resolution 1440x810 --write-movie /tmp/shot.png --fixed-fps 60 --quit-after 200 res://scenes/fight.tscn -- --demo
```
