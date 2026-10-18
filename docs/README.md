# Documentation d'Eco Clash

Retour au [README du projet](../README.md).

La documentation est en deux parties. La partie **fonctionnelle** décrit le jeu tel qu'on le joue ;
la partie **technique** décrit comment il est construit et comment le faire évoluer. Chaque page
renvoie vers la précédente et la suivante.

## Fonctionnel

| Page | Contenu |
|---|---|
| [Présentation](fonctionnel/01-presentation.md) | Le jeu, son univers, son public, ses principes de design. |
| [Règles et commandes](fonctionnel/02-regles-et-commandes.md) | Modes, déroulé d'un match, touches, sélection, pause. |
| [Personnages](fonctionnel/03-personnages.md) | Les six combattants, leurs coups et leurs statistiques. |
| [Écrans](fonctionnel/04-ecrans.md) | Menu, sélection, combat et HUD, pause, victoire. |

## Technique

| Page | Contenu |
|---|---|
| [Architecture](technique/01-architecture.md) | Pile, arborescence, scènes, autoloads, couches physiques, principes. |
| [Le combattant](technique/02-combattant.md) | Données, entrées, machine à états, mouvement, coups, sprites. |
| [Combat](technique/03-combat.md) | Timeline des coups, volumes, résolution, projection, impact, KO. |
| [IA](technique/04-ia.md) | Perception, décision, temps de réaction du bot. |
| [Arène et effets](technique/05-arene-et-effets.md) | Couches de l'arène, couches animées, effets, ombre, marqueurs. |
| [Interface](technique/06-interface.md) | Kit UI, textes, thème, écrans, police. |
| [Pipeline d'assets](technique/07-assets.md) | Générateur Python, marionnette et cinématique inverse, fichiers partagés. |
| [Tests](technique/08-tests.md) | Lancer, suites, conventions, captures d'écran. |
| [Ajouter un personnage](technique/09-ajouter-un-personnage.md) | Le guide pas à pas. |

## Documents de référence

- [`PRODUCT.md`](../PRODUCT.md) : public, personnalité, anti-références et principes de design.
  Il fait foi pour toute décision visuelle.
- [`README.md`](../README.md) : lancer le jeu, commandes, tests, vue d'ensemble.

## Tenir la doc à jour

Tout ajout, suppression ou modification met à jour la page concernée dans le même commit. La table
« ce qui change, pages à mettre à jour » est dans [`CONTRIBUTING.md`](../CONTRIBUTING.md), avec la règle d'univers
original (pas de terme d'une autre licence ; l'énergie s'appelle le flux). Les valeurs chiffrées
(statistiques, constantes) sont recopiées du code : si elles changent dans le code, elles changent
ici.

Le test `test_docs` en vérifie une partie : chaque personnage est documenté, chaque lien relatif
résout, aucun terme interdit n'apparaît.
