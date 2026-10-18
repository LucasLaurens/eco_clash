# Arène et effets

[Sommaire](../README.md) · Précédent : [IA](04-ia.md) · Suivant : [Interface](06-interface.md)

## L'arène : `scenes/stage.tscn` et `Stage`

Couches dessinées de l'arrière vers l'avant :

| Nœud | Contenu |
|---|---|
| `Sky` | Ciel de crépuscule, arche ancienne lointaine, soleil bas. |
| `Clouds` | Bande de nuages qui défile lentement (`Parallax2D`, boucle sur 480 px). |
| `Far` | Flèches anciennes et mer de nuages. |
| `FluxMotes` | Particules de flux qui scintillent (animée). |
| `Mid` | Deux pylônes flottants qui encadrent l'arène. |
| `PylonGlow` | Conduits de flux des pylônes qui pulsent (animée). |
| `Ground` | Le sol : collision 312 x 40, surface à y = 186, et la dalle dessinée. |
| `Platforms` | Trois plateformes à sens unique, 60 x 6 : gauche (150, 130), droite (330, 130), haut (240, 84). |
| `Spawns` | Points de départ (176, 186) et (304, 186). |

`Stage` expose :

| Méthode | Rôle |
|---|---|
| `is_inside_blast_zone(point)` | Le combattant est-il encore dans la zone d'éjection ? |
| `get_spawn_position(slot)` | Point de départ d'un slot. |
| `compute_ground_surface()` | Rectangle du sol, lu sur la forme de collision : une seule source pour le bot. |

### Couches animées

Leur placement et leur cadence ne sont pas écrits dans la scène mais dans
`assets/stage/animated_layers.json`, généré à côté des images :

```json
"PylonGlow": { "sheet": "pylon_glow.png", "frame_width": 480, "fps": 3, "offset": [0, 0] }
```

Au `_ready`, `Stage` remplit chaque nœud `AnimatedSprite2D` du même nom avec `SpriteStrip` et lance
l'animation. Un test vérifie que chaque entrée correspond à un nœud de la scène et que sa planche
se découpe en images entières.

## Effets ponctuels : `OneShotEffect`

`src/fx/one_shot_effect.gd`. Une planche jouée une fois puis libérée. Les images sont découpées une
seule fois par planche et mises en cache.

| Planche | Quand | Teinte |
|---|---|---|
| `HIT_SPARK` | Chaque coup qui touche. | Blanche. |
| `DUST` | Saut au sol, saut en l'air, atterrissage rapide. | Sable. |
| `KO_BURST` | Sortie de la zone d'éjection, au bord de l'écran. | Couleur du personnage. |

## Flash d'impact

`src/fx/hit_flash.gdshader`, un shader `canvas_item` posé sur le sprite de chaque combattant.
`flash_amount` passe à 1 pendant 0,08 s après un coup reçu : le sprite vire au blanc chaud
`(1.0, 0.97, 0.9)` en gardant sa transparence et son clignotement.

## Ombre au sol

À chaque tick, le combattant lance un rayon vers le bas, sur 160 px au plus, avec son propre masque
de collision. Pendant une traversée, ce masque exclut les plateformes, donc l'ombre aussi. L'ombre
se pose sur la surface touchée.

Sa taille vient de 3 images (grande, moyenne, petite) plutôt que d'un agrandissement : la grille de
pixels reste nette. `Fighter.compute_shadow_frame(hauteur, nombre_d_images)` choisit l'image.

## Marqueurs de joueur

`fight.gd` associe à chaque slot une étiquette (`marker_p1`, `marker_p2`, `marker_bot`) via
`MatchConfig.resolve_slot_tag(slot)`, la même clé que les curseurs de la sélection. Un test vérifie
que chaque slot de chaque mode a son curseur et son marqueur.

## Caméra

`ShakeCamera` (`src/fx/shake_camera.gd`) : tremblement par trauma, voir [Combat](03-combat.md).
La caméra est fixe, centrée sur l'arène.
