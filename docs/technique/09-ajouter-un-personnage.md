# Ajouter un personnage

[Sommaire](../README.md) · Précédent : [Tests](08-tests.md)

Exemple : un personnage d'identifiant `zara`. L'identifiant sert partout (fichiers, ressource).

## 1. Le dessiner

Dans `tools/assets/fighters.py` :

1. Créer `class ZaraArtist(FighterArtist)` et implémenter au minimum `paint_torso` et `paint_head`.
   Optionnel :
   - `paint_back_extras` / `paint_front_extras` pour les accessoires ;
   - `paint_boot` / `paint_forearm` / `paint_arm` / `paint_leg` pour les membres ;
   - `place_head` pour une tête penchée ;
   - `paint_effect` pour un effet de spécial propre.
2. Ajouter l'entrée `"zara": ZaraArtist(...)` dans `build_artists()`, avec :
   - son `Anatomy` ;
   - ses couleurs (`skin`, `limb`, `sleeve`, `boot`) ;
   - son flux (une couleur de `palette.py`, distincte des autres pour le HUD) ;
   - si besoin, ses `special_poses` (3 poses : préparation, déclenchement, suite).
3. Si son spécial est un projectile d'une nouvelle couleur, ajouter la planche dans
   `generate_stage()` : `stage.render_flux_bolt(palette.FLUX_...)`.

Générer, puis importer :

```bash
python3 tools/assets/generate_assets.py
godot --headless --path . --import
```

Contrôler la planche à l'œil (`preview.py`) : rien ne doit sortir du cadre de 64 px, la silhouette
doit se lire en garde à taille réelle.

## 2. Ses données

Copier une ressource proche dans `data/fighters/zara.tres` et adapter :

- **chemins** : `assets/fighters/zara.png`, `assets/ui/portrait_zara.png`,
  `assets/ui/stock_zara.png` ;
- **identité** : `id = &"zara"`, `display_name`, `title`, `accent_color` (la couleur de son flux) ;
- **corps** : `body_size`, à mesurer sur la silhouette dessinée, pieds en bas ;
- **déplacement** : `run_speed`, `jump_velocity`, `air_jumps`, `weight` ;
- **coups** : `light_attack` et `special`, chacun un `MeleeStrike` (avec `lunge`) ou un
  `ProjectileShot` (avec `speed`, `lifetime`, `sprite_sheet`), chacun avec son `AttackData`.

Les noms et descriptions s'écrivent en majuscules, avec les caractères de la police EcoPixel.

## 3. L'ajouter au roster

Dans `src/fighters/fighter_roster.gd`, ajouter la ressource à `DEFINITIONS`, à la place voulue
dans l'écran de sélection.

## 4. Mettre à jour tests et doc

- `tests/unit/test_roster.gd` : le nombre attendu de combattants distincts.
- `README.md` : tableau des personnages.
- [Personnages](../fonctionnel/03-personnages.md) : fiche et tableaux.

## 5. Vérifier

```bash
godot --headless --path . --fixed-fps 60 res://tests/test_runner.tscn
```

Les tests contrôlent :

- la planche (largeur et hauteur conformes à `layout.json`) ;
- les coups (complets, avec une animation qui existe) ;
- les jauges (entre 1 et 5) ;
- la police (chaque caractère du nom et des descriptions).

Ils ne jugent ni l'équilibrage ni le rendu : faire au moins un combat contre le bot, et regarder
l'écran de sélection (le panneau doit tenir dans l'écran).
