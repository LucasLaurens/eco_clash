# Le combattant

[Sommaire](../README.md) · Précédent : [Architecture](01-architecture.md) · Suivant : [Combat](03-combat.md)

Un combattant, c'est trois choses séparées :

- **les données** : `FighterDefinition` (`.tres`) ;
- **le comportement** : `Fighter` (`src/fighters/fighter.gd`) ;
- **le pilote** : un `InputSource`.

Le combattant ne sait jamais si un humain ou un bot le contrôle.

## Données : `FighterDefinition`

`src/fighters/fighter_definition.gd`, une ressource par personnage dans `data/fighters/`.

| Champ | Rôle |
|---|---|
| `id`, `display_name`, `title` | Identité. `id` sert aussi de nom de fichier pour les sprites. |
| `accent_color` | Couleur du nom et des vies dans le HUD, teinte de l'éclat de KO. |
| `sprite_sheet`, `portrait`, `stock_icon` | Images générées (planche d'animation, portrait 48 px, tête 16 px du HUD). |
| `body_size` | Taille de la zone touchable (et de la collision), ancrée aux pieds. |
| `run_speed`, `jump_velocity`, `air_jumps`, `weight` | Déplacement et résistance aux projections. |
| `light_attack`, `special` | Deux `FighterMove`. |

Les jauges de l'écran de sélection sont calculées, jamais saisies :

```
note = clamp(1 + arrondi(ratio * 4), 1, 5)
ratio = position de la valeur dans son intervalle
  vitesse   : run_speed dans [90, 170]
  puissance : dégâts attaque + dégâts spécial dans [10, 24]
              (FighterMove.compute_rated_damage : poison compris, coup sombre pour DarkSurge,
               0 pour un soin)
  poids     : weight dans [70, 140]
```

Le `FighterRoster` (`src/fighters/fighter_roster.gd`) liste les six définitions dans l'ordre du menu.

## Entrées : `InputFrame` et `InputSource`

Un `InputFrame` est l'intention d'un tick physique, identique quelle que soit sa source :

| Champ | Sens |
|---|---|
| `move_x` | Direction horizontale, de -1 à 1. |
| `down` | Bas maintenu (chute rapide, traverser une plateforme). |
| `jump_pressed`, `attack_pressed`, `special_pressed` | Appuis du tick (front montant). |

`InputSource` est une classe abstraite à une méthode, `read_frame()`. Implémentations :

| Classe | Pilote |
|---|---|
| `HumanInputSource` | Lit les actions d'un `ControlScheme` (joueur 1 ou 2), que clavier et manette alimentent ensemble. |
| `BotInputSource` | Demande une décision au `BotBrain` (voir [IA](04-ia.md)). |
| `NullInputSource` | Ne fait rien : compte à rebours, fin de match. |

`ControlScheme` (`src/core/control_scheme.gd`) est le seul endroit où vivent les commandes. Il
associe à chaque joueur des **touches physiques** (donc ZQSD en AZERTY et WASD en QWERTY) et une
**manette**, et crée les actions `p1_left`, `p1_attack`, `p2_up`, etc. avec les deux à la fois :

| Action | Touches (`PLAYER_KEYS`) | Boutons (`PAD_BUTTONS`) | Stick gauche (`PAD_STICK`) |
|---|---|---|---|
| `LEFT` / `RIGHT` | A / D, ← / → | croix ← / → | axe X, -1 / +1 |
| `UP` | W, ↑ | croix ↑, X | axe Y, -1 |
| `DOWN` | S, ↓ | croix ↓ | axe Y, +1 |
| `ATTACK` | F, K | A | |
| `SPECIAL` | G, L | B | |

- **Appareil** : `resolve_pad_device()` donne au joueur N la N-ième manette branchée. Sans manette,
  il rend un identifiant qu'aucun matériel n'envoie (`PADLESS_DEVICE_BASE` + N, soit 1001 et 1002) :
  une manette seule ne pilote jamais les deux joueurs.
- **Zone morte** : chaque action est créée avec `STICK_DEADZONE` = 0,5.
- **Actions partagées** : `pause` (Échap, Start de n'importe quelle manette) ouvre la pause et quitte
  la sélection ; le bouton A de n'importe quelle manette est ajouté à `ui_accept`, que Godot ne lie à
  aucun bouton. La navigation `ui_up` / `ui_down` / `ui_left` / `ui_right` de Godot connaît déjà la
  croix et le stick.
- **Branchement à chaud** : `register_all_actions()` est idempotent. L'autoload `InputBindings`
  l'appelle au démarrage puis à chaque `Input.joy_connection_changed`, ce qui réattribue les
  manettes sans redémarrer.
- **Libellés** : `format_key_label` affiche la touche telle que le clavier de l'utilisateur la
  nomme ; en headless (tests, CI), sans disposition de clavier, il affiche la touche physique.
  `format_pad_label` affiche le premier bouton de `PAD_BUTTONS` (noms Xbox : A, B, flèches de la
  croix). `format_control_label` choisit l'un ou l'autre selon que le joueur a une manette
  (`has_pad()`) ; c'est lui que lisent les rappels à l'écran.

`InputSourceFactory` choisit humain (clavier et manette) ou bot pour chaque slot selon le `MatchConfig`.

## Machine à états

```mermaid
stateDiagram-v2
    [*] --> FREE
    FREE --> ACTING: attaque ou spécial
    ACTING --> FREE: fin de la timeline du coup
    FREE --> HITSTUN: coup reçu
    ACTING --> HITSTUN: coup reçu
    HITSTUN --> FREE: fin du hitstun
    FREE --> OUT: dernière vie perdue
    HITSTUN --> OUT: dernière vie perdue
```

| État | Ce qui se passe |
|---|---|
| `FREE` | Course, sauts, chute rapide, traverser une plateforme, lancer un coup. |
| `ACTING` | Un coup se déroule ; la vitesse au sol freine. L'effet du coup part à la fin du démarrage. |
| `HITSTUN` | Projeté, sans contrôle ; la vitesse horizontale freine doucement. |
| `OUT` | Plus de vies : caché, plus traité. |

## Un tick physique

Ordre dans `Fighter._physics_process` :

1. Si `OUT`, rien.
2. Lire l'`InputFrame` de la source.
3. Décompter les minuteurs (invulnérabilité, flash d'impact, traversée de plateforme) et ceux de
   `FighterStatus` ; un palier de poison ajoute ses dégâts.
4. Mettre à jour l'état courant.
5. Appliquer la gravité, puis `move_and_slide()`.
6. Si le combattant vient de toucher le sol : recharger sauts et spécial aérien, poussière si la
   chute était rapide.
7. Mettre à jour le visuel (animation, retournement, teinte d'état, clignotement, flash) et
   l'ombre.

## Constantes de mouvement

Dans `fighter.gd`, en pixels et secondes :

| Constante | Valeur | Sens |
|---|---|---|
| `GRAVITY` | 980 | Gravité. |
| `MAX_FALL_SPEED` / `FAST_FALL_SPEED` | 380 / 560 | Vitesse de chute max, normale et rapide (bas en l'air). |
| `GROUND_ACCELERATION` / `GROUND_FRICTION` | 1500 / 1700 | Accélérer et freiner au sol. |
| `AIR_ACCELERATION` | 950 | Contrôle en l'air. |
| `AIR_JUMP_RATIO` | 0,9 | Hauteur d'un saut en l'air par rapport au saut au sol. |
| `DROP_THROUGH_DURATION` | 0,25 | Durée pendant laquelle les plateformes sont ignorées. |
| `RESPAWN_INVULNERABILITY` | 2 | Invulnérabilité après réapparition. |

Une projection plus rapide que la vitesse de chute max n'est jamais ralentie par la gravité.

## Coups : `FighterMove`

`FighterMove` est une Strategy : la timeline du coup est gérée par le `Fighter`, le coup ne
décide que de son effet, dans `trigger_effect(user)`, appelé à la fin du démarrage.

| Classe | Effet |
|---|---|
| `MeleeStrike` | Applique un élan (`lunge`, x relatif à l'orientation) puis crée un volume de coup attaché au combattant. |
| `ProjectileShot` | Crée un volume de coup qui voyage (`speed`, `lifetime`) avec sa propre animation ; en cloche avec `lift` (vitesse initiale vers le haut) et `gravity`. |
| `DarkSurge` | Rend le combattant sombre : sa prochaine attaque, dans `window` secondes, est remplacée par `empowered_strike`. |
| `HasteRush` | Multiplie la vitesse de course (`speed_multiplier`) pendant `duration` et attache au corps, pour la même durée, un volume qui frappe au premier contact. |
| `Mend` | Retire `heal_ratio` des dégâts, `max_heal` au plus. |

Chaque coup porte un `AttackData` (dégâts, projection, hitbox, timeline, poison, paralysie) : voir
[Combat](03-combat.md). Le spécial a aussi un `cooldown`.

## États : `FighterStatus`

`src/fighters/fighter_status.gd`, données et minuteurs purs (testés sans scène). Le `Fighter` en a
un, remplacé par un neuf à chaque réapparition.

| État | Règle |
|---|---|
| Recharge du spécial | Démarre au lancement du spécial (`cooldown` du coup). Tant qu'elle court, l'appui spécial est ignoré. `compute_special_readiness()` va de 0 à 1 pour le HUD. |
| Emprise sombre | `select_light_attack` rend le coup sombre au lieu de l'attaque normale ; une fois lancé, l'emprise est dépensée mais l'aura sombre dure jusqu'à la fin du coup. |
| Sprint | `compute_speed_multiplier()` multiplie `run_speed`, au sol comme en l'air. |
| Poison | Réparti en paliers de 0,5 s (`POISON_TICK`) sur `poison_duration`. |
| Paralysie | Le hitstun dure au moins `paralysis` ; chaque coup reçu remplace la paralysie, donc un coup sans paralysie libère la cible. |

## Sprites

Chaque planche fait 64 px de haut, une image de 64 x 64 par pose. `FighterSpriteFrames` lit
`assets/fighters/layout.json`, écrit par le générateur, pour savoir quelles images forment chaque
animation (`idle`, `run`, `jump`, `fall`, `attack`, `special`, `hurt`), à quelle vitesse et si elle
boucle. Le même fichier donne la ligne des pieds (`feet_y`) : le sprite est décalé pour que les
pieds dessinés tombent exactement sur l'origine du corps.

Pendant un coup, l'image affichée suit la phase (démarrage, actif, récupération), pas le temps.

## Éléments visuels attachés

| Nœud | Rôle |
|---|---|
| `Shadow` | Ombre au sol : un rayon vers le bas avec le masque du combattant ; 3 tailles selon la hauteur (`compute_shadow_frame`). |
| `Sprite` | L'animation, avec le shader de flash d'impact. |
| `Marker` | L'étiquette 1P / 2P / BOT, posée au-dessus de `body_size`. |
| `Volumes` | Les volumes de coup au corps à corps en cours. |

Détails dans [Arène et effets](05-arene-et-effets.md).
