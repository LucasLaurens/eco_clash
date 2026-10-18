# Règles et commandes

[Sommaire](../README.md) · Précédent : [Présentation](01-presentation.md) · Suivant : [Personnages](03-personnages.md)

## Modes de jeu

| Mode | Depuis | Joueur 1 | Joueur 2 |
|---|---|---|---|
| 1 joueur contre bot | Menu « 1 JOUEUR VS BOT » | Humain | Bot |
| 2 joueurs | Menu « 2 JOUEURS » | Humain (moitié gauche du clavier) | Humain (flèches) |
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

Touches physiques : la disposition s'adapte au clavier AZERTY ou QWERTY.

| Action | Joueur 1 | Joueur 2 |
|---|---|---|
| Bouger | Q / D (A / D en QWERTY) | ← / → |
| Sauter, double saut | Z (W en QWERTY) | ↑ |
| Chute rapide (en l'air) | S | ↓ |
| Traverser une plateforme | S + Z (bas + saut) au sol | ↓ + ↑ |
| Attaque | F | K |
| Spécial | G | L |
| Pause | Échap | Échap |

Précisions :

- **Sauts** : un saut au sol, puis les sauts en l'air propres au personnage (1 pour la plupart,
  2 pour Pip et Kragg). Un saut en l'air est un peu moins haut (90 %).
- **Spécial en l'air** : utilisable une seule fois par passage en l'air ; il se recharge à
  l'atterrissage.
- **Plateformes** : les trois plateformes flottantes se traversent par en dessous ; bas + saut
  permet de redescendre à travers.

## Sélection des personnages

- En **2 joueurs**, chaque joueur déplace son propre curseur avec ses touches.
- En **1 joueur contre bot**, le joueur 1 choisit son personnage, puis celui du bot.
- Attaque valide, spécial annule (ou revient au menu si rien n'est validé en mode bot).
  Échap revient au menu.
- Le match démarre 0,7 seconde après que les deux choix sont validés.

## Pause

Échap met le combat en pause : « REPRENDRE » ou « MENU PRINCIPAL ».

## Fin de match

L'écran de victoire montre le vainqueur, son personnage et la durée du match, puis propose :
« REVANCHE » (mêmes personnages), « CHANGER DE PERSO » (retour à la sélection) ou « MENU ».
