# Personnages

[Sommaire](../README.md) · Précédent : [Règles et commandes](02-regles-et-commandes.md) · Suivant : [Écrans](04-ecrans.md)

Six combattants, dans l'ordre de l'écran de sélection. Chacun a une attaque (touche attaque) et un
spécial (touche spécial). Les jauges de l'écran de sélection (1 à 5) sont calculées à partir des
statistiques ci-dessous ; elles ne sont jamais saisies à la main.

## Vue d'ensemble

| Personnage | Rôle | Vitesse | Puissance | Poids | Sauts en l'air | Couleur |
|---|---|---|---|---|---|---|
| Kael | Équilibré | 3 | 3 | 3 | 1 | Vert |
| Pip | Rapide et léger | 5 | 2 | 1 | 2 | Bleu |
| Grondak | Lourd, frappe fort | 2 | 5 | 5 | 1 | Rouge |
| Ormos | Distance | 2 | 2 | 2 | 1 | Jaune |
| Vargo | Lourd, distance | 2 | 4 | 4 | 1 | Violet |
| Kragg | Très lourd, aérien | 2 | 4 | 5 | 2 | Orange |

La couleur est celle de l'éco du personnage : elle teinte son nom et ses vies dans le HUD, ses
effets et son éclat de KO.

## Fiches

### Kael, l'aventurier

Ranger éco à coupe militaire : côtés rasés, longue crête blonde dressée, bouc, lunettes, longues
oreilles, gilet bleu, écharpe rouge, gantelets de métal.

| Coup | Dégâts | Effet |
|---|---|---|
| Direct (attaque) | 6 % | Coup de poing rapide devant soi. |
| Uppercut Éco (spécial) | 11 % | Bond vertical qui projette vers le haut. Sert aussi à revenir du vide. |

### Pip, le furtif

Petit ottsel orange avec lunettes, collier tech et grande queue rayée. Le plus rapide, le plus
léger : il vole loin quand il est touché.

| Coup | Dégâts | Effet |
|---|---|---|
| Griffe Éclair (attaque) | 4 % | Coup de griffe très rapide. |
| Ruée Bleue (spécial) | 8 % | Charge horizontale éclair. |

### Grondak, la brute

Brute Metal Head : peau sombre, carapace d'os, épines dorsales, crâne à cornes avec une gemme
lumineuse au front, poings de métal. Lent mais très lourd et très puissant.

| Coup | Dégâts | Effet |
|---|---|---|
| Marteau-Poing (attaque) | 9 % | Coup lourd et lent. |
| Séisme Rouge (spécial) | 14 % | Frappe le sol des deux côtés. En l'air, plonge d'un coup vers le bas. |

### Ormos, le sage

Vieux sage à la peau verte : longue barbe blanche, chapeau-souche d'où sortent des feuilles,
robe de lin, bâton surmonté d'un orbe d'éco jaune. Il joue à distance.

| Coup | Dégâts | Effet |
|---|---|---|
| Coup de Bâton (attaque) | 5 % | Coup de bâton à bonne portée. |
| Orbe Jaune (spécial) | 7 % | Projectile qui traverse l'arène. |

### Vargo, le colosse

Guerrier du désert : bras nus, gilet de cuir, bandoulière, casque-masque à visière lumineuse,
canon lourd à éco sombre.

| Coup | Dégâts | Effet |
|---|---|---|
| Crosse (attaque) | 8 % | Coup de crosse du canon. |
| Pacificateur (spécial) | 14 % | Tir lourd et lent d'éco sombre qui projette très loin. Long à préparer. |

### Kragg, le patron

Chef de gang sur fauteuil volant : énorme ventre, veste de velours bordeaux, boutons dorés,
moustache, bagues. Le fauteuil flotte sur un réacteur d'éco orange.

| Coup | Dégâts | Effet |
|---|---|---|
| Gifle Baguée (attaque) | 7 % | Revers de la main baguée. |
| Ruée du Fauteuil (spécial) | 12 % | Le fauteuil fonce droit devant. |

Double saut en vol stationnaire.

## Statistiques détaillées

Valeurs lues dans `data/fighters/*.tres` (unités : pixels et secondes).

| Personnage | Course (px/s) | Impulsion de saut | Poids | Corps (L x H) |
|---|---|---|---|---|
| Kael | 130 | 374 | 100 | 16 x 42 |
| Pip | 165 | 363 | 75 | 14 x 30 |
| Grondak | 100 | 341 | 135 | 28 x 44 |
| Ormos | 115 | 369 | 90 | 18 x 40 |
| Vargo | 115 | 352 | 125 | 20 x 46 |
| Kragg | 100 | 352 | 140 | 30 x 40 |

Le corps est la zone qui peut être touchée. Le calcul des jauges et des projections est décrit
dans [Combat](../technique/03-combat.md) et [Le combattant](../technique/02-combattant.md).
