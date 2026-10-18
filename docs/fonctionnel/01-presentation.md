# Présentation

[Sommaire](../README.md) · Suivant : [Règles et commandes](02-regles-et-commandes.md)

## Le jeu

Eco Clash est un jeu de combat 1 contre 1 en pixel art, dans l'esprit de Smash Bros. On ne vide pas
une barre de vie : chaque coup fait monter un pourcentage de dégâts, et plus ce pourcentage est
élevé, plus le combattant touché est projeté loin. Sortir de l'écran coûte une vie. Le dernier
combattant qui a encore des vies gagne.

## Univers

L'arène est une dalle de tech ancienne qui flotte au crépuscule au-dessus d'une mer de nuages :
métal patiné, flux d'énergie qui luit dans les objets (conduits, cristaux, anneaux), grandes formes
simples. L'univers, ses termes et ses six combattants sont originaux.

## Public et contexte

- Deux personnes côte à côte, au clavier (une moitié chacune) ou à la manette, ou une personne seule contre le bot.
- Parties courtes, sur un écran de laptop ou une TV.
- On veut entrer en combat vite et comprendre à chaque instant ce qui se passe.

## Principes de design

Ils sont écrits dans [`PRODUCT.md`](../../PRODUCT.md), qui fait foi :

1. On sait toujours qui est qui, même quand les deux joueurs ont le même personnage.
2. Chaque coup se sent : l'impact se voit sur la cible, pas seulement dans le chiffre.
3. Le décor vit mais ne gêne jamais la lecture : peu d'éléments, palette réduite, un seul accent de
   flux (cyan) pour la tech ; les couleurs vives sont réservées aux personnages.
4. Le pixel reste net, sur une seule grille : pas de flou, pas de résolutions mélangées.

Anti-référence : le néon et le cyberpunk (glow partout, scanlines, fond noir et fluo).

## Plateforme

Godot 4.7, rendu 480 x 270 agrandi x3 dans une fenêtre de 1440 x 810. Lancement et commandes
détaillés dans le [README](../../README.md).
