# Règles et commandes

[Sommaire](../README.md) · Précédent : [Présentation](01-presentation.md) · Suivant : [Personnages](03-personnages.md)

## Modes de jeu

| Mode | Depuis | Joueur 1 | Joueur 2 |
|---|---|---|---|
| 1 joueur contre bot | Menu « 1 JOUEUR VS BOT » | Humain (clavier ou manette) | Bot |
| 2 joueurs | Menu « 2 JOUEURS » | Humain (moitié gauche du clavier ou 1re manette) | Humain (flèches ou 2e manette) |
| Démo | Ligne de commande `-- --demo` | Bot | Bot |

En mode démo, la scène de combat se lance directement avec deux bots (Kael contre Grondak) :

```bash
godot --path . res://scenes/fight.tscn -- --demo
```

## Règles d'un match

- Chaque combattant commence avec **3 vies** et **0 %** de dégâts.
- Chaque coup reçu ajoute ses dégâts au pourcentage, puis projette la cible. La force de projection
  grandit avec le pourcentage et diminue avec le poids du personnage touché
  (détail : [Combat](../technique/03-combat.md)).
- Un combattant projeté est un instant sans contrôle (hitstun), plus long quand le coup est fort.
- Sortir de la zone d'éjection (un rectangle plus large que l'écran) coûte une vie.
- Après une vie perdue, le combattant réapparaît au-dessus de son point de départ avec 0 % et
  **2 secondes d'invulnérabilité** (il clignote).
- Quand un combattant n'a plus de vie, le match s'arrête : « FIN DU COMBAT ! » au ralenti,
  puis l'écran de victoire.

## Commandes

Chaque joueur joue au clavier ou à la manette (Xbox, DualSense et toute manette reconnue par Godot),
au choix : clavier + manette ou deux manettes. Les deux marchent en même temps pour un même joueur.

Touches physiques : la disposition s'adapte au clavier AZERTY ou QWERTY.

| Action | Joueur 1 | Joueur 2 | Manette (chaque joueur) |
|---|---|---|---|
| Bouger | Q / D (A / D en QWERTY) | ← / → | Stick gauche ou croix ← / → |
| Sauter, double saut | Z (W en QWERTY) | ↑ | Stick ou croix ↑, ou X (Carré sur DualSense) |
| Chute rapide (en l'air) | S | ↓ | Stick ou croix ↓ |
| Traverser une plateforme | S + Z (bas + saut) au sol | ↓ + ↑ | Bas + saut |
| Attaque | F | K | A (Croix) |
| Spécial | G | L | B (Rond) |
| Pause | Échap | Échap | Start (Options) |

Manettes :

- La 1re manette branchée pilote le joueur 1, la 2e le joueur 2. Une manette branchée ou débranchée
  en cours de partie est prise en compte aussitôt, sans redémarrer.
- Le stick ne compte qu'à partir de la moitié de son inclinaison : un stick au repos ne fait pas
  marcher, et un stick à peine penché vers le bas ne fait pas traverser une plateforme.
- Les rappels de commandes à l'écran montrent les boutons de la manette pour un joueur qui en a une,
  ses touches sinon.

Précisions :

- **Sauts** : un saut au sol, puis les sauts en l'air propres au personnage (1 pour la plupart,
  2 pour Pip et Kragg). Un saut en l'air est un peu moins haut (90 %).
- **Spécial en l'air** : utilisable une seule fois par passage en l'air ; il se recharge à
  l'atterrissage.
- **Plateformes** : les trois plateformes flottantes se traversent par en dessous ; bas + saut
  permet de redescendre à travers.

## Sélection des personnages

- En **2 joueurs**, chaque joueur déplace son propre curseur avec ses touches ou sa manette.
- En **1 joueur contre bot**, le joueur 1 choisit son personnage, puis celui du bot.
- Attaque valide, spécial annule (ou revient au menu si rien n'est validé en mode bot).
  Échap ou Start revient au menu.
- Le match démarre 0,7 seconde après que les deux choix sont validés.

## Pause

Échap ou Start (Options) met le combat en pause et l'enlève : « REPRENDRE » ou « MENU PRINCIPAL ».
Dans les menus, la croix ou le stick de n'importe quelle manette change de bouton et A valide.

## Fin de match

L'écran de victoire montre le vainqueur, son personnage et la durée du match, puis propose :
« REVANCHE » (mêmes personnages), « CHANGER DE PERSO » (retour à la sélection) ou « MENU ».
