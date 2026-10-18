# Règles du projet Eco Clash

## La documentation suit chaque changement

Tout ajout, suppression ou modification de comportement, de donnée ou de fichier met à jour la
documentation **dans le même commit**. Une phrase devenue fausse est supprimée ou réécrite, jamais
laissée à côté de la nouvelle.

| Ce qui change | Pages à mettre à jour |
|---|---|
| Personnage (ajout, retrait, coups, statistiques, look) | `README.md` (tableau), `docs/fonctionnel/03-personnages.md`, `docs/technique/09-ajouter-un-personnage.md` si la procédure change |
| Règles, commandes, modes, sélection | `docs/fonctionnel/02-regles-et-commandes.md`, `README.md` (commandes) |
| Écrans, HUD, textes affichés, retours visuels | `docs/fonctionnel/04-ecrans.md`, `docs/technique/06-interface.md` |
| Scènes, dossiers, autoloads, couches physiques | `docs/technique/01-architecture.md`, arborescence du `README.md` |
| `Fighter`, entrées, coups, sprites | `docs/technique/02-combattant.md` |
| Combat, projection, impact, KO | `docs/technique/03-combat.md` |
| Bot | `docs/technique/04-ia.md` |
| Arène, couches animées, effets, ombre, marqueurs | `docs/technique/05-arene-et-effets.md` |
| Générateur d'assets, palette, fichiers produits | `docs/technique/07-assets.md`, section Assets du `README.md` |
| Tests (suite ajoutée ou retirée) | `docs/technique/08-tests.md` |
| Direction visuelle, public, principes | `PRODUCT.md`, `docs/fonctionnel/01-presentation.md` |

Les valeurs chiffrées des docs (statistiques, constantes, positions) sont recopiées du code : elles
changent avec lui. Une nouvelle page est ajoutée au sommaire `docs/README.md` et chaînée à ses
voisines (liens Précédent / Suivant).

`tests/unit/test_docs.gd` vérifie une partie de ces règles : chaque personnage du roster est
documenté, chaque lien relatif des docs pointe vers un fichier existant, et aucun terme interdit
(ci-dessous) n'apparaît.

## Univers original

Le jeu ne fait référence à aucune licence existante : ni nom de jeu, de personnage, de lieu ou de
faction, ni terme propre à un autre univers. En particulier, pas de Jak, Daxter, Precursor /
Précurseur, Metal Head, Krimzon, ottsel, Samos, Sig, Krew, Haven, Spargus.

- L'énergie colorée s'appelle le **flux** (`FLUX_GREEN`, « orbe de flux »), jamais « éco ».
- La tech de l'arène est **ancienne** (`ANCIENT_METAL`, `ANCIENT_GLOW`).
- Seul le titre garde « Eco » : Eco Clash, la police EcoPixel, le dépôt `eco_clash`.

Cela vaut pour le code, les commentaires, les données, les textes affichés, la doc et les messages
de commit.
