# Personnages

[Sommaire](../README.md) · Précédent : [Règles et commandes](02-regles-et-commandes.md) · Suivant : [Écrans](04-ecrans.md)

Six combattants, dans l'ordre de l'écran de sélection. Chacun a une attaque (touche attaque) et un
spécial (touche spécial). Après chaque spécial, un temps de recharge propre au personnage bloque le
suivant (jauge sous le pourcentage dans le HUD). Les jauges de l'écran de sélection (1 à 5) sont
calculées à partir des statistiques ci-dessous ; elles ne sont jamais saisies à la main.

## Vue d'ensemble

| Personnage | Rôle | Vitesse | Puissance | Poids | Sauts en l'air | Couleur |
|---|---|---|---|---|---|---|
| Kael | Équilibré, coup sombre | 3 | 3 | 3 | 1 | Vert |
| Pip | Rapide et léger, harcèlement | 5 | 1 | 1 | 2 | Bleu |
| Grondak | Lourd, frappe fort, orbe | 2 | 5 | 5 | 1 | Rouge |
| Ormos | Endurant, se soigne | 2 | 1 | 2 | 1 | Jaune |
| Vargo | Lourd, paralyse à distance | 2 | 4 | 4 | 1 | Violet |
| Kragg | Très lourd, poison en cloche | 2 | 3 | 5 | 2 | Orange |

## Spéciaux et recharges

| Personnage | Spécial | Recharge | En bref |
|---|---|---|---|
| Kael | Emprise Sombre | 6 s | Devient sombre 4 s : son prochain coup frappe à 12 % au lieu de 6 % et projette bien plus loin. |
| Pip | Sprint Éclair | 6 s | Court 1,6 fois plus vite pendant 2 s ; le premier contact frappe à 6 %, une seule fois. |
| Grondak | Orbe de Rage | 5 s | Crache un orbe rouge lent (14 %). Long à sortir. |
| Ormos | Sève de Vie | 10 s | Efface 30 % de ses dégâts, 20 points au plus. Long à lancer : un coup reçu l'annule. |
| Vargo | Détonation | 7 s | Charge violette lente (11 %) qui pousse peu mais paralyse 1,5 s. Le coup suivant la réveille. |
| Kragg | Fiole Toxique | 4,5 s | Fiole lancée en cloche (4 %), puis le poison ronge 6 % en 1,5 s. |

La recharge démarre au lancement du spécial. Équilibre visé : un spécial fort ou sûr se recharge
longtemps (soin, paralysie), un spécial à risque se recharge vite (fiole qui rate de près, orbe
lent à sortir). La paralysie pousse peu exprès : elle ouvre un coup gratuit, pas un KO direct.

La couleur est celle du flux du personnage : elle teinte son nom et ses vies dans le HUD, ses
effets et son éclat de KO.

## Fiches

### Kael, l'aventurier

Ranger du flux à coupe militaire : côtés rasés, longue crête blonde dressée, bouc, lunettes, longues
oreilles, gilet bleu, écharpe rouge, gantelets de métal.

| Coup | Dégâts | Effet |
|---|---|---|
| Direct (attaque) | 6 % | Coup de poing rapide devant soi. |
| Emprise Sombre (spécial) | 12 % | Une ombre s'empare de lui, il vire au sombre : son prochain coup (Direct Sombre, dans les 4 s) frappe plus fort, avance un peu et projette loin. |

### Pip, le furtif

Petit furet orange avec lunettes, collier tech et grande queue rayée. Le plus rapide, le plus
léger : il vole loin quand il est touché.

| Coup | Dégâts | Effet |
|---|---|---|
| Griffe Éclair (attaque) | 4 % | Coup de griffe très rapide. |
| Sprint Éclair (spécial) | 6 % | Court beaucoup plus vite pendant 2 s, teinté de bleu ; le premier contact avec l'adversaire le frappe, une seule fois. |

### Grondak, la brute

Brute à carapace : peau sombre, carapace d'os, épines dorsales, crâne à cornes avec une gemme
lumineuse au front, poings de métal. Lent mais très lourd et très puissant.

| Coup | Dégâts | Effet |
|---|---|---|
| Marteau-Poing (attaque) | 9 % | Coup lourd et lent. |
| Orbe de Rage (spécial) | 14 % | Crache un orbe de flux rouge à hauteur de bouche, qui traverse l'arène. Long à sortir. |

### Ormos, le sage

Vieux sage à la peau verte : longue barbe blanche, chapeau-souche d'où sortent des feuilles,
robe de lin, bâton surmonté d'un orbe de flux jaune. Léger, il tient la distance en se soignant.

| Coup | Dégâts | Effet |
|---|---|---|
| Coup de Bâton (attaque) | 6 % | Coup de bâton à bonne portée. |
| Sève de Vie (spécial) | soin | Efface 30 % des dégâts accumulés (20 au plus), avec une étincelle verte. Démarrage de 0,45 s : un coup reçu pendant ce temps annule le soin. |

### Vargo, le colosse

Guerrier du désert : bras nus, gilet de cuir, bandoulière, casque-masque à visière lumineuse,
canon lourd à flux sombre.

| Coup | Dégâts | Effet |
|---|---|---|
| Crosse (attaque) | 8 % | Coup de crosse du canon. |
| Détonation (spécial) | 11 % | Grosse charge de flux violet, lente et longue à préparer. À l'impact, éclat violet : la cible est paralysée 1,5 s (teinte violette), jusqu'au coup suivant. |

### Kragg, le patron

Chef de gang sur fauteuil volant : énorme ventre, veste de velours bordeaux, boutons dorés,
moustache, bagues. Le fauteuil flotte sur un réacteur de flux orange.

| Coup | Dégâts | Effet |
|---|---|---|
| Gifle Baguée (attaque) | 7 % | Revers de la main baguée. |
| Fiole Toxique (spécial) | 4 % + 6 % | Lance une fiole en cloche (portée moyenne, passe au-dessus d'un adversaire collé). La cible vire au vert et perd 2 % toutes les 0,5 s pendant 1,5 s. |

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
