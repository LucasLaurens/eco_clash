# Eco Clash

Jeu de combat 1 contre 1 en pixel art, façon Smash Bros, dans un univers
de tech ancienne : une arène qui flotte au crépuscule au-dessus des nuages. Godot 4.7, GDScript, rendu 480x270 agrandi x3.

## Documentation

La documentation complète est dans [`docs/`](docs/README.md) :

- **Fonctionnel** : [présentation](docs/fonctionnel/01-presentation.md),
  [règles et commandes](docs/fonctionnel/02-regles-et-commandes.md),
  [personnages](docs/fonctionnel/03-personnages.md), [écrans](docs/fonctionnel/04-ecrans.md).
- **Technique** : [architecture](docs/technique/01-architecture.md),
  [le combattant](docs/technique/02-combattant.md), [combat](docs/technique/03-combat.md),
  [IA](docs/technique/04-ia.md), [arène et effets](docs/technique/05-arene-et-effets.md),
  [interface](docs/technique/06-interface.md), [pipeline d'assets](docs/technique/07-assets.md),
  [tests](docs/technique/08-tests.md), [ajouter un personnage](docs/technique/09-ajouter-un-personnage.md),
  [qualité et CI](docs/technique/10-qualite-et-ci.md).

## Lancer le jeu (Mac)

```bash
godot --path .
```

Ou ouvrir `project.godot` dans Godot puis F5.

Spectateur bot contre bot : `godot --path . res://scenes/fight.tscn -- --demo`

## Commandes

| | Joueur 1 | Joueur 2 | Manette (chaque joueur) |
|---|---|---|---|
| Bouger / sauter | Z Q S D (W A S D en QWERTY) | Flèches | Stick gauche ou croix ; X saute aussi |
| Attaque | F | K | A (Croix sur DualSense) |
| Spécial | G | L | B (Rond) |
| Traverser une plateforme | Bas + Saut | Bas + Saut | Bas + Saut |
| Pause | Échap | Échap | Start (Options) |

Touches physiques : la disposition s'adapte au clavier AZERTY ou QWERTY. Chaque joueur peut jouer au
clavier ou à la manette : la 1re manette branchée va au joueur 1, la 2e au joueur 2, et une manette
branchée en cours de partie marche aussitôt. Clavier + manette ou deux manettes, au choix.

## Personnages

Fiches complètes et statistiques : [docs/fonctionnel/03-personnages.md](docs/fonctionnel/03-personnages.md).

| | Rôle | Spécial |
|---|---|---|
| Kael | Équilibré | Emprise Sombre (son prochain coup frappe bien plus fort) |
| Pip | Rapide, léger, triple saut | Sprint Éclair (2 s très rapide, le premier contact frappe) |
| Grondak | Lourd, frappe fort | Orbe de Rage (orbe rouge craché) |
| Ormos | Vieux sage endurant | Sève de Vie (soigne 30 % des dégâts) |
| Vargo | Colosse du désert, lourd | Détonation (charge violette qui paralyse 1,5 s) |
| Kragg | Patron sur fauteuil volant, double saut | Fiole Toxique (poison en cloche, 6 % sur 1,5 s) |

Règles : 3 vies. Plus le pourcentage monte, plus on vole loin. Sortir de l'écran coûte une vie.
Chaque spécial a un temps de recharge (4,5 à 10 s), visible sous le pourcentage.

## Tests

Suites et conventions : [docs/technique/08-tests.md](docs/technique/08-tests.md).

```bash
godot --headless --path . --fixed-fps 60 res://tests/test_runner.tscn
pytest --cov
```

Le premier lance les tests du jeu (ajouter `-- --only=unit` ou `-- --only=features` pour une seule
famille), le second ceux des outils Python (`pip install -r requirements-dev.txt`). Code de sortie
1 en cas d'échec. Chaque test est listé par son nom.

## Qualité et CI

À chaque push et pull request, la CI GitHub Actions vérifie le format et le lint (gdformat, gdlint,
ruff), la règle de nommage (fonctions qui commencent par un verbe), lance tous les tests et mesure la
couverture. Détails et commandes locales : [docs/technique/10-qualite-et-ci.md](docs/technique/10-qualite-et-ci.md).

## Assets

Pipeline détaillé : [docs/technique/07-assets.md](docs/technique/07-assets.md).

Tous les sprites, le décor, l'UI et la police pixel sont générés une seule fois par
`tools/assets/generate_assets.py` (Python + Pillow), puis versionnés en PNG.
Le jeu ne les régénère jamais. `assets/fighters/layout.json` est la seule source
des indices d'animation, lue par Python et par Godot. De même, `assets/stage/animated_layers.json`
place et cadence les couches animées du décor (conduits de flux des pylônes, particules de flux).
Les couleurs de joueur (1P rouge, 2P bleu, BOT gris) vivent dans `tools/assets/palette.py`.

## Lisibilité en combat

Un marqueur 1P / 2P / BOT flotte au-dessus de chaque combattant, une ombre au sol rétrécit
quand il monte, et le décor garde peu de formes et peu de teintes : seul le flux (cyan) y luit, les couleurs
vives restent aux personnages. Les cartes du HUD sont compactes et sans cadre.
Chaque coup fait flasher la cible en blanc ; saut et atterrissage soulèvent de la poussière ;
un KO éclate au bord de l'écran dans la couleur du personnage. Le cadre produit est décrit
dans `PRODUCT.md`.

## Arborescence

Rôle de chaque dossier et des scènes : [docs/technique/01-architecture.md](docs/technique/01-architecture.md).

```
assets/          PNG générés, police EcoPixel (.fnt), thème UI
data/fighters/   Les 4 personnages (.tres) : stats, attaques, sprites
scenes/          fighter, stage, fight, ui/(main_menu, character_select, results)
src/core/        Entrées : InputFrame, InputSource (port), clavier et manette, Null Object
src/bot/         IA : perception, cerveau (pur), source d'entrée bot
src/combat/      AttackData, formule de knockback, HitVolume, CombatResolver
src/fighters/    Fighter, état (FighterStatus), définitions, roster, coups (MeleeStrike, ProjectileShot, DarkSurge, HasteRush, Mend)
src/match/       Config, résultat, autoload MatchSettings, fabrique d'entrées, scène de combat
src/stage/       Arène : sol, plateformes, spawns, zone d'éjection
src/fx/          Effets ponctuels (étincelle, poussière, KO), flash d'impact, tremblement de caméra, sprite strips
src/ui/          Textes, kit UI, menus, HUD, pause, résultats
tests/           Runner headless, unit/ et features/
tools/assets/    Générateur d'assets (one-shot)
tools/ci/        Règle de nommage, couverture GDScript
tools/tests/     Tests pytest des outils
.github/         Workflow de CI
PRODUCT.md       Public, personnalité et principes visuels du jeu
CONTRIBUTING.md  Règles du projet : doc à jour à chaque changement, univers original
docs/            Documentation fonctionnelle et technique
```
