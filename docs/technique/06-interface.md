# Interface

[Sommaire](../README.md) · Précédent : [Arène et effets](05-arene-et-effets.md) · Suivant : [Pipeline d'assets](07-assets.md)

## Briques partagées

| Fichier | Rôle |
|---|---|
| `src/ui/ui_text.gd` | **Tous** les textes affichés, en constantes. Rien n'est écrit en dur ailleurs. |
| `src/ui/ui_kit.gd` | Fabrique des widgets récurrents : libellé, bouton, colonne centrée, fond d'arène, voile. |
| `src/ui/scene_paths.gd` | Chemins des scènes. |
| `assets/ui/theme.tres` | Thème global : police EcoPixel, boutons et panneaux en métal ancien. |

### Règles de `UiKit`

- **Tailles de police** : `FONT_SMALL` (12), `FONT_MEDIUM` (24), `FONT_LARGE` (36), `FONT_HUGE`
  (48). La police pixel ne s'affiche qu'à des multiples entiers de sa taille.
- **Couleurs de texte** : `TEXT_LIGHT`, `TEXT_MUTED`, `TEXT_GOLD`.
- **Voile** : `VEIL_COLOR`, un bleu nuit dont seule l'opacité varie selon l'écran.
  - `create_veil(alpha)` donne un voile plein écran ;
  - `create_veil_style(alpha, padding)` en fait un fond de panneau qui s'ajuste au contenu (bandeau
    du menu, cartes du HUD).
- **Fond de menu** : `add_backdrop(parent, alpha)` instancie l'arène vivante, masque ses
  plateformes, puis pose le voile.

## Écrans

| Script | Points notables |
|---|---|
| `main_menu.gd` | Bandeau de commandes construit avec `UiKit.format_controls`, qui affiche les vraies touches du clavier. |
| `character_select.gd` | Un `SelectionCursor` par slot. En VS BOT, le joueur 1 pilote les deux curseurs l'un après l'autre. Un `MatchConfig` sert de règles des slots (qui est bot, quel schéma de touches). |
| `fighter_info_panel.gd` | Panneau de sélection : aperçu 64 px, nom, titre, jauges, spécial, état. |
| `hud.gd` | Place les deux `FighterCard`, joue le compte à rebours, affiche la bannière de fin. |
| `fighter_card.gd` | Carte de HUD : tête 16 px, « 1P · KAEL », pourcentage (blanc puis orange puis rouge vers 150 %), un point par vie. |
| `pause_menu.gd` | `process_mode = ALWAYS` pour vivre pendant la pause de l'arbre. |
| `results.gd` | Vainqueur animé à l'échelle 1, durée, trois boutons. |

## Contraintes d'écran

L'écran fait 270 px de haut. Les mises en page ont été ajustées aux sprites de 64 px :

- les panneaux de sélection commencent juste sous les étiquettes des curseurs (`PANEL_Y`) ;
- le vainqueur est affiché à l'échelle 1, sinon le dernier bouton sort de l'écran.

## Police

EcoPixel est une police 5 x 7 en majuscules, générée avec un contour d'un pixel (voir
[Pipeline d'assets](07-assets.md)). Elle couvre l'alphabet, les chiffres, la ponctuation utile,
les flèches et les accents français courants (É È Ê Ë À Â Ô Ù Û Î Ï Ç). Le test
`test_font_draws_every_ui_string` échoue si un texte de `UiText` ou un nom de personnage contient un
caractère qu'elle ne sait pas dessiner.
