# Eco Clash

Jeu de combat 1 contre 1 en pixel art, façon Smash Bros, dans l'univers Precursor
de Jak II et Jak 3 : une arène de tech ancienne qui flotte au crépuscule au-dessus des nuages. Godot 4.7, GDScript, rendu 480x270 agrandi x3.

## Lancer le jeu (Mac)

```bash
godot --path .
```

Ou ouvrir `project.godot` dans Godot puis F5.

Spectateur bot contre bot : `godot --path . res://scenes/fight.tscn -- --demo`

## Commandes

| | Joueur 1 | Joueur 2 |
|---|---|---|
| Bouger / sauter | Z Q S D (W A S D en QWERTY) | Flèches |
| Attaque | F | K |
| Spécial | G | L |
| Traverser une plateforme | Bas + Saut | Bas + Saut |
| Pause | Échap | Échap |

Touches physiques : la disposition s'adapte au clavier AZERTY ou QWERTY.

## Personnages

| | Rôle | Spécial |
|---|---|---|
| Kael | Équilibré | Uppercut Eco (vertical, sert aussi à revenir) |
| Pip | Rapide, léger, triple saut | Ruée Bleue (charge horizontale) |
| Grondak | Lourd, frappe fort | Séisme Rouge (sol des deux côtés, plongeon en l'air) |
| Ormos | Vieux sage à distance | Orbe Jaune (projectile) |
| Vargo | Colosse du désert, lourd | Pacificateur (tir lourd et lent, projette loin) |
| Kragg | Patron sur fauteuil volant, double saut | Ruée du Fauteuil (charge horizontale) |

Règles : 3 vies. Plus le pourcentage monte, plus on vole loin. Sortir de l'écran coûte une vie.

## Tests

```bash
godot --headless --path . --fixed-fps 60 res://tests/test_runner.tscn
```

Code de sortie 1 en cas d'échec. Chaque test est listé par son nom.

## Assets

Tous les sprites, le décor, l'UI et la police pixel sont générés une seule fois par
`tools/assets/generate_assets.py` (Python + Pillow), puis versionnés en PNG.
Le jeu ne les régénère jamais. `assets/fighters/layout.json` est la seule source
des indices d'animation, lue par Python et par Godot. De même, `assets/stage/animated_layers.json`
place et cadence les couches animées du décor (conduits d'éco des pylônes, particules d'éco).
Les couleurs de joueur (1P rouge, 2P bleu, BOT gris) vivent dans `tools/assets/palette.py`.

## Lisibilité en combat

Un marqueur 1P / 2P / BOT flotte au-dessus de chaque combattant, une ombre au sol rétrécit
quand il monte, et le décor garde peu de formes et peu de teintes : seule l'éco (cyan) y luit, les couleurs
vives restent aux personnages. Les cartes du HUD sont compactes et sans cadre.
Chaque coup fait flasher la cible en blanc ; saut et atterrissage soulèvent de la poussière ;
un KO éclate au bord de l'écran dans la couleur du personnage. Le cadre produit est décrit
dans `PRODUCT.md`.

## Arborescence

```
assets/          PNG générés, police EcoPixel (.fnt), thème UI
data/fighters/   Les 4 personnages (.tres) : stats, attaques, sprites
scenes/          fighter, stage, fight, ui/(main_menu, character_select, results)
src/core/        Entrées : InputFrame, InputSource (port), clavier, Null Object
src/bot/         IA : perception, cerveau (pur), source d'entrée bot
src/combat/      AttackData, formule de knockback, HitVolume, CombatResolver
src/fighters/    Fighter, définitions, roster, coups (MeleeStrike, ProjectileShot)
src/match/       Config, résultat, autoload MatchSettings, fabrique d'entrées, scène de combat
src/stage/       Arène : sol, plateformes, spawns, zone d'éjection
src/fx/          Effets ponctuels (étincelle, poussière, KO), flash d'impact, tremblement de caméra, sprite strips
src/ui/          Textes, kit UI, menus, HUD, pause, résultats
tests/           Runner headless + suites unitaires et scénarios
tools/assets/    Générateur d'assets (one-shot)
PRODUCT.md       Public, personnalité et principes visuels du jeu
```
