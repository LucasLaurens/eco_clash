# Combat

[Sommaire](../README.md) · Précédent : [Le combattant](02-combattant.md) · Suivant : [IA](04-ia.md)

## Timeline d'un coup : `AttackData`

`src/combat/attack_data.gd`. Un coup se déroule en trois phases :

```
|-- startup --|-- active --|-- recovery --|
  préparation   touche       récupération
```

| Champ | Rôle |
|---|---|
| `damage` | Pourcentage ajouté à la cible. |
| `base_knockback`, `knockback_growth` | Force de projection de base et sa croissance avec les dégâts. |
| `launch_angle_deg` | 0 = droit devant, 90 = droit vers le haut. |
| `hitbox_offset`, `hitbox_size` | Rectangle du coup, relatif aux pieds (x inversé selon l'orientation). |
| `startup`, `active`, `recovery` | Durées en secondes. |
| `poison_damage`, `poison_duration` | Dégâts ajoutés après le coup, par paliers de 0,5 s, répartis sur la durée. |
| `paralysis` | Secondes pendant lesquelles la cible ne peut pas agir, même une fois la projection finie. |

L'effet du coup (`FighterMove.trigger_effect`) part à la fin de `startup`. Le volume de coup vit
`active` secondes (ou `lifetime` pour un projectile).

## Volumes de coup : `HitVolume`

`src/combat/hit_volume.gd`. Un rectangle vivant qui fait mal :

- au corps à corps, enfant du combattant (il suit ses mouvements) ;
- en projectile, enfant du monde, avec une vitesse, une gravité éventuelle (tir en cloche) et une
  animation. Un projectile en cloche ignore le sol et tombe jusqu'à la fin de sa durée de vie.

Un volume touche chaque cible **une seule fois**. Un projectile disparaît au premier coup porté.
Tous les volumes rejoignent le groupe `hit_volumes`.

Sens de la projection : un projectile pousse dans le sens de son vol ; un coup au corps à corps
pousse à l'opposé du corps de l'attaquant.

## Qui touche qui : `CombatResolver`

`src/combat/combat_resolver.gd` est le seul endroit qui croise volumes et combattants. Il tourne
après les déplacements du tick (`process_physics_priority = 100`) :

```
pour chaque volume du groupe hit_volumes
  pour chaque combattant
    si le volume peut le toucher et qu'il n'est pas invulnérable
    et que le rectangle du coup croise le rectangle du corps :
      le combattant reçoit le coup, le volume le note, signal hit_landed
```

Coût : O(V x F) par tick, avec V volumes vivants et F = 2 combattants.

## Projection : `KnockbackFormula`

`src/combat/knockback_formula.gd`, fonctions pures :

```
force    = base_knockback + knockback_growth x pourcentage_après_coup x 100 / poids
vitesse  = (cos(angle) x sens, -sin(angle)) x force
hitstun  = force x 0,0018 secondes
```

- Plus la cible a de dégâts, plus elle vole loin.
- À dégâts égaux, un personnage lourd vole moins loin (le poids de référence est 100).
- La vitesse de projection a pour norme exactement la force.

Ces trois propriétés sont vérifiées par des tests.

## Recevoir un coup

`Fighter.receive_hit` :

1. ajoute les dégâts au pourcentage ;
2. calcule la force avec le nouveau pourcentage, puis la vitesse de projection et le hitstun
   (au moins `paralysis`) ;
3. transmet le coup à son `FighterStatus` (poison, paralysie) ;
4. passe en `HITSTUN`, se tourne vers l'attaquant ;
5. lance le flash d'impact (0,08 s) ;
6. supprime ses propres volumes de coup en cours ;
7. émet `damage_changed`.

## Sensation d'impact

Gérée par `fight.gd` à chaque `hit_landed` :

| Effet | Réglage |
|---|---|
| Étincelle | Effet ponctuel au centre de la zone de contact. |
| Détonation | Si le coup paralyse, éclat de KO violet en plus, au même point. |
| Tremblement | Trauma ajouté = dégâts x 0,03. Amplitude = trauma² x 6 px ; le trauma décroît de 2,5 par seconde. |
| Hit-stop | `Engine.time_scale = 0,05` pendant 0,03 + dégâts x 0,004 secondes (temps réel). |

## KO et fin de match

À chaque tick, `fight.gd` vérifie si chaque combattant en jeu est encore dans la zone d'éjection de
l'arène (`Rect2(-110, -150, 700, 500)`). Sinon :

1. fort tremblement (trauma 0,7) et éclat de KO au point de sortie, ramené dans l'écran ;
2. le combattant perd une vie ;
3. s'il lui en reste, il réapparaît plus haut que son point de départ, avec 0 % et 2 s
   d'invulnérabilité ;
4. sinon, le match se termine :
   - le résultat est enregistré dans `MatchSettings.last_result` ;
   - les deux combattants passent sur `NullInputSource` ;
   - « FIN DU COMBAT ! » s'affiche au ralenti (`time_scale` 0,35) pendant 2 s ;
   - puis l'écran de résultats s'ouvre.
