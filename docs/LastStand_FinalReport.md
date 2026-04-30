# Last Stand
## Final Course Assessment Report

**COMP 323 / 488**
Spring 2026

**Team Boatmurdered**
Michael Barrow · Mitchell Radzienda · Faris Siddiqi

---

## Table of Contents

1. [Project Participants](#1-project-participants)
2. [Abstract](#2-abstract)
3. [Project Narrative](#3-project-narrative)
4. [Design Considerations](#4-design-considerations)
5. [Design and Specification](#5-design-and-specification)
6. [Testing and Iterative Design](#6-testing-and-iterative-design)
7. [Restrictions, Limitations, and Constraints](#7-restrictions-limitations-and-constraints)
8. [Conclusion](#8-conclusion)

---

## 1. Project Participants

| Member | Role | Contributions |
|---|---|---|
| **Michael Barrow** | Input & Player Systems | Implemented the InputManager (keybindings, input polling interface, and player aim control in `managers.py`). Built all player logic in `player.py` including movement physics (constant friction / high acceleration for snappy feel), the shoot method, and dash integration. Tuned movement feel across iterative playtesting. Implemented wave spawning logic.  Compiled and edited group assignment documents. |
| **Mitchell Radzienda** | Architecture & State Machine | Established the foundational OOP architecture (Thing → Living → Enemy/Player/Projectile class hierarchy). Designed and implemented the state machine controlling Title, Play (Wave/Shop sub-states), and Game Over transitions. Built the shop/upgrade interactable system, and tuned upgrade options across iterative playtesting.  Implemented data-driven upgrade architecture with `upgrades.json`. Maintained `game.py` as the central game loop and draw manager. Produced the module ownership and state map diagrams. |
| **Faris Siddiqi** | Enemy Systems & Audio | Designed the data-driven enemy architecture: `enemies.json` for external enemy definitions, `enemy.py` with loader utilities (`load_enemy`, `load_enemies`, `spawn_from_template`) and all enemy AI. Implemented circle-vs-circle collision detection with squared-distance optimisation. Added player health, max_health, and damage cooldown/invincibility system. Built the AudioManager with folder-scanning, one-shot SFX wiring, and looping BGM. Maintained the reliability checklist. |

---

## 2. Abstract

**Last Stand** is a top-down arcade shooter built in Python using the Pygame library. The player controls a single character in an enclosed arena and must survive endless waves of increasingly difficult enemies. The core loop is: fight a wave of enemies, defeat them all to unlock the upgrade shop, choose one of two randomised upgrades, then face the next wave. The game ends when the player's health reaches zero, at which point the final wave count is displayed and the player may immediately restart.

The project was developed over a full semester by a three-person team (Team Boatmurdered) as part of COMP 323/488. Development proceeded from an initial object-oriented architecture sketch, through a mid-semester playable demo, to a release candidate featuring multiple enemy types, a data-driven upgrade system, a dash mechanic with decoupled invincibility frames, a points-budget wave scaling system, and a full audio implementation. The game targets Windows 11 and is cross-platform compatible via Python 3.10+ and Pygame.

---

## 3. Project Narrative

### 3.1 Inspiration and Goals

The initial design direction was inspired by classic arcade survival games and, specifically for the technical architecture, by modding communities for games such as *RimWorld*, which employ inheritance-based entity hierarchies to represent in-game objects of varying complexity. The team wanted to build something mechanically tight and immediately readable: a game where the challenge comes from skill at positioning and aiming rather than memorising rules.

A secondary architectural goal informed the project from the outset: to keep content extensible without requiring code changes. This led directly to the decision to externalise enemy definitions and upgrade data into JSON files, so that new enemy types and upgrade cards could be added as data entries rather than new code modules.

### 3.2 Premise and Gameplay

The player is dropped into a fixed-boundary arena and faces waves of enemies that spawn from the screen edges. Each wave is harder than the last: enemies spawn faster, in greater numbers, and from a larger pool of types as the player progresses. There is no time limit per wave; the only way to advance is to destroy every enemy.

Between waves, the game enters a Shop state. The player retains full movement and shooting ability during the shop (enabling repositioning and continued practice with any upgraded controls) and is presented with two upgrade cards to choose from. Upgrades affect player statistics such as speed, health, damage, and attack speed parameters. Some upgrades are repeatable (re-entering the pool after selection); others are one-time only.

### 3.3 Initial Player Goals

The core player goals established at the start of the project were:

- Survive as many waves as possible, the score is simply the wave count reached.
- Aim and destroy all enemies in each wave before being overwhelmed.
- Use the upgrade shop strategically to build a character suited to the player's playstyle.
- Master the dash mechanic to evade dangerous situations and navigate enemy clusters.

---

## 4. Design Considerations

### 4.1 Characters and Object Hierarchy

The game's entity model is built on a two-level abstract hierarchy. **Thing** is the foundational abstract class, providing every in-game object with a position (Vector2 of floats), colour (pygame.Color, defaulting to white), a bounding rectangle (pygame.Rect, defaulting to 32×32 pixels), and an optional multi-rect hitbox (list of pygame.Rect) for irregular shapes.

**Living** extends Thing and represents any entity that has agency in the world. It adds an `update()` abstract method, allowing all living entities to be grouped into a single list and updated in one loop, along with a speed float (enabling hazards and slow effects to work uniformly across all entity types) and a health integer (−1 signals that health mechanics do not apply to this entity).

| Class             | Parent        | Key Attributes / Methods                                                          |
|-------------------|---------------|-----------------------------------------------------------------------------------|
| `Thing`           | Abstract base | position (Vector2), color, rect (32×32), hitbox (optional multi-rect)             |
| `Living`          | `Thing`       | update(), speed (float), health (int; −1 = no health)                             |
| `Player`          | `Living`      | velocity (Vector2), acceleration, friction, shoot(), dash()                       |
| `Enemy`           | `Living`      | movement_style (enum), contact_damage, cost (wave budget), generate_projectile()  |
| `Projectile`      | `Thing`       | velocity, damage, owner reference                                                 |
| `ShapeContainer`  | `Thing`       | Utility wrapper for compound/composite shapes                                     |

### 4.2 Abstracted Attributes and Developer Patterns

Several design patterns were established to keep the codebase extensible and team-friendly across parallel workstreams:

- **Action enum**: All user inputs are routed through an Action enum rather than raw key constants. This allowed Michael to add the dash binding and Mitchell to add the shop select binding independently without either touching the other's code.
- **Data-driven content**: Enemy types are defined in `enemies.json` and upgrades in `upgrades.json`. Helper functions (`load_enemy`, `load_enemies`, `spawn_from_template`) convert raw JSON into properly-typed Python objects (pygame.Color, Movement_styles enum) at load time.
- **Manager classes**: `InputManager` and `AudioManager` encapsulate their respective subsystems behind clean public interfaces, keeping their internals isolated from game logic.
- **Multi-list object registry**: Game objects are tracked across `all_things`, `all_living`, `all_enemies`, and `all_projectiles` lists, enabling type-filtered iteration. (See Section 7 for a candid discussion of the limitations this introduced.)

### 4.3 Formal Game Elements

#### Objectives and Player Goals

The primary objective is survival: the player's score equals the number of waves completed. Secondary objectives emerge naturally through the upgrade system. Players develop implicit build strategies (e.g. prioritising speed to enable aggressive play, or health to create a tank archetype).

#### Rules and Boundaries

- The arena has fixed boundaries that the player and enemies cannot cross.
- Enemies spawn from the four edges of the playfield; spawn intervals decrease as waves progress.
- A wave is complete only when all enemies are destroyed; avoiding enemies prolongs and intensifies the wave.
- The player has a damage cooldown (invincibility window) after being hit, preventing instant multi-hits.
- Shooting has a cooldown which can be decreased with upgrades.
- The dash consumes a cooldown resource and provides a brief invincibility window independent of movement duration.

#### Conflict and Challenge

Conflict is generated through the wave scaling system: each wave increases the points budget by 200 (starting at 400), and each enemy type has an associated cost. As the budget grows, the spawner automatically assembles harder mixes of enemy types. Spawn intervals also decrease each wave, with a floor at 0.5 seconds (reached at wave 10), ensuring sustained pressure. Enemy variety (chaser, patrol, teleporting Mage types) forces the player to adapt their positioning and prioritisation.

#### Narrative Structure

Last Stand uses a minimal implied narrative: the player is the last defender, the waves represent an endless assault, and the shop represents brief respite between engagements. There is no explicit story text; the narrative is entirely mechanical and emergent, consistent with the arcade genre.

#### Outcome and End State

The game ends when the player reaches 0 health. A Game Over screen displays the final wave count (score) and prompts the player to press Space to restart immediately from Wave 1. There is no win condition; the game is designed as an endless survival loop.

---

## 5. Design and Specification

### 5.1 State Machine

The game is controlled by a hierarchical state machine. The top-level states are **Title**, **Play**, and **Game Over**. Play contains two sub-states: **Wave** (active combat) and **Shop** (upgrade selection). The reason for the Play/sub-state split is deliberate: the player retains movement and shooting during the shop, so it is more accurate to describe the shop as a mode within Play than as a separate top-level state.

| Transition            | Condition                                             |
|-----------------------|-------------------------------------------------------|
| Title → Play:Wave     | Player presses Space / Return on the title screen     |
| Play:Wave → Play:Shop | All enemies in the current wave are destroyed         |
| Play:Shop → Play:Wave | Short timer expires after upgrade selection           |
| Play → Game Over      | Player health reaches zero                            |
| Game Over → Play:Wave | Player presses Space / Return on the game over screen |

### 5.2 Module Architecture

The codebase is split across five primary Python modules, each with a defined responsibility:

| Module        | Responsibility                                                                                                                        |
|---------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `things.py`   | Defines the Thing, Living, Projectile, and ShapeContainer classes and their shared methods. Used by all other modules.                |
| `player.py`   | Contains the Player class, including shoot() and the dash implementation.                                                             |
| `enemy.py`    | Contains the Enemy class, Movement_styles enum, and the load/spawn utility functions that read from enemies.json.                     |
| `managers.py` | Contains InputManager (keybindings, input polling, aim control) and AudioManager (sound loading, one-shot SFX, looping BGM).          |
| `game.py`     | The central hub: state machine, main game loop, wave budget and spawning logic, collision detection, draw management, and shop state. |

External data files `enemies.json` and `upgrades.json` serve as the content layer, fully decoupling enemy and upgrade definitions from the Python codebase. Adding a new enemy type requires only a JSON entry and an enum addition with no changes to spawning, collision, or draw logic.

### 5.3 Procedural Outline and Game Loop

Each frame, the game loop executes the following sequence:

1. Poll events (quit, key/mouse input via InputManager).
2. Update all Living entities (player, enemies, projectiles) via the `all_living` list.
3. Run collision detection: circle-vs-circle player↔enemy (triggering damage cooldown), and projectile↔enemy (dealing damage, awarding score, consuming projectile).
4. Check wave completion: if `all_enemies` is empty, transition to Shop state.
5. Check player death: if player health ≤ 0, transition to Game Over.
6. Draw all Things via the `all_things` list, then overlay HUD and screen-shake effects.

### 5.4 Wave Scaling System

Wave difficulty is governed by a points budget rather than a hardcoded enemy count. Wave 1 allocates 400 points; each subsequent wave adds 200. Each enemy type has an associated cost value, and the spawner fills the wave by drawing from the enemy pool until the budget is exhausted. This system automatically produces harder and more varied mixes as the roster grows, with no manual scripting required per wave.

Spawn intervals decrease by 0.1 seconds per wave, with a floor of 0.5 seconds at wave 10 and beyond, maintaining sustained pressure even at high wave counts.

### 5.5 Dash and Invincibility System

The dash mechanic applies a high-speed impulse to the player for a short duration, accompanied by an invincibility window. Critically, the movement duration and invincibility duration are governed by separate variables: `_dash_duration` (0.06 s) controls how long the impulse lasts, while `_dash_invuln_time` (0.12 s) extends invincibility beyond the movement itself. This gives the player a moment to reorient after landing, making the dash feel like a deliberate dodge rather than an escape tool.

### 5.6 Collision Detection

All entity collision uses circle-vs-circle detection. Distance is computed as squared Euclidean distance (avoiding a square root) and compared against the squared sum of the two entities' radii. This approach is applied both for player↔enemy contact damage and for projectile↔enemy hits.

### 5.7 Audio Assets

The AudioManager scans the `audio/` folder at startup and maps filenames to playable sounds, silently skipping any missing files so the game never crashes over an absent asset. The following sounds are wired to game events:

| File                  | Event                                         | Source                                                        |
|-----------------------|-----------------------------------------------|---------------------------------------------------------------|
| `bgm.mp3`             | Looping background music (stops on Game Over) | "The Great Beyond" by Orboram (Freesound.org, CC)              |
| `player_damage.mp3`   | Player hit                                    | "Retro hurt 2" by Driken5482 (Pixabay)                         |
| `enemy_damage.mp3`    | Enemy hit                                     | "Hitmarker Sound Effect" by aruscio28 (Freesound.org, CC)      |
| `round_win.mp3`       | Wave cleared                                  | "Short Success Sound Glockenspiel" by FunWithSound (Pixabay)   |
| `game_over.mp3`       | Game Over screen                              | "negative_beeps" by themusicalnomad (Pixabay)                  |

---

## 6. Testing and Iterative Design

### 6.1 Playtesting at Each Stage

Playtesting was conducted informally throughout development. Each demo included a structured feedback plan with specific questions targeting different aspects of the player experience.

**Non-exhaustive demo feedback questions covered:**

- Could a first-time player understand the goal and win condition without being told?
- Could a first time player understand the shop and how to choose upgrades without being told?
- Was the damage feedback (hit flash, invincibility window) clear and readable on screen?
- Did the Game Over / restart flow feel immediate?
- Did movement feel responsive? Did the damage cooldown window feel fair?
- Did state transitions (title → play, game over → restart) reset cleanly?
- Did the dash speed, distance, and invulnerability feel helpful?
- Did the waves feel more difficult as the player progressed?
- Did any of the waves feel unfair or unfun?
- Did any particular enemy type feel unfair or unfun?
- Did the player feel like the shop let them play into their strengths or cover their weaknesses?
- Did the audio ever cut out, become corrupted, or otherwise function inappropriately?

### 6.2 Iteration Evidence: Dash Tuning

**Before playtesting:**
The initial dash used a speed of 2,800 u/s over 0.12 seconds. The invincibility window was tied directly to dash duration so when movement ended, invulnerability ended with it.

**Playtest finding:**
Testers reported that the dash covered too much distance and felt closer to a teleport than a dodge. The tied invuln window compounded the problem: by the time the dash completed, enemies had re-closed the gap, making the protection feel shorter than it actually was.

**After iteration:**
Speed was reduced to 1,600 u/s and duration to 0.06 s. The invincibility window was decoupled into its own variable (`_dash_invuln_time` = 0.12 s), extending protection beyond the movement phase. The earlier internal logs also record an intermediate step: a 1:2 ratio was tested at 0.09 s / 0.18 s before being tuned down to the final 0.06 s / 0.12 s values. The result was described by playtesters as a deliberate dodge rather than an escape tool.

### 6.3 Iteration Evidence: Mage Enemy Tuning

**Before playtesting:**
The Mage enemy (a teleporting type added in the content pass) teleported every 2.5 seconds.

**Playtest finding:**
Testers found this enemy more annoying than challenging, particularly during wave cleanup when several Mages remained. The short teleport interval meant player shots-on-target frequently missed after the enemy blinked away from the projectile mid-flight.

**After iteration:**
The teleport interval was doubled to 5 seconds. This gave players enough time to aim, fire, and have the projectile reach the target before the next teleport, making the Mage feel like a skill-testing enemy rather than a frustrating one.

### 6.4 Design Reviews and Architecture Feedback

In addition to player-facing playtesting, the team conducted informal design reviews focused on code structure. These reviews identified the accumulation of logic in `game.py` as an ongoing concern and the multi-list object registry as a source of subtle removal bugs. Both issues are documented in Section 7 with concrete proposals for future improvement.

---

## 7. Restrictions, Limitations, and Constraints

### 7.1 game.py Scope Creep

The most significant structural issue encountered was the accumulation of logic in `game.py`. Spawning logic, collision detection, wave budget calculations, shop state management, and the draw loop all grew within this single file. While the pattern was reasonable during the early thin game loop, the absence of a clear rule about what belonged in `game.py` versus its own module meant it became the natural destination for anything that touched more than one system. The file ended up significantly larger and harder to navigate than any other module.

In retrospect, a rule such as "if a block of logic exceeds 20 lines and maintains its own state, it gets its own file", enforced from week 7-8 onward, would have kept the file manageable. Collision logic, wave budget calculations, and shop logic should each have lived in dedicated modules or manager classes.

### 7.2 Object Registry Design

Tracking game objects across four parallel lists (`all_things`, `all_living`, `all_enemies`, `all_projectiles`) meant that adding or removing any object required up to four separate list operations. Missing a removal from any list caused subtle bugs that were non-trivial to trace. Each new object type inherited this awkward pattern by convention.

A single entity registry with tag-based filtering such as `get_all(tag="enemy")` established in Week 7 alongside the initial architecture would have handled all cases cleanly and been easier to extend as new types were added.

### 7.3 Communication and Collaboration

The team's workflow was largely deadline-driven, organised around assignment due dates rather than self-imposed milestones. Most work was completed in the few days preceding each submission, which created time pressure, particularly when simultaneous contributions were needed to large shared modules like `game.py`. Communication was conducted ad hoc through Discord, with no scheduled design or logistics meetings. The team acknowledges that a small number of recurring structured meetings across the semester would have distributed effort more evenly and reduced late-stage pressure.

### 7.4 Known Bugs and Missing Features

- **Mouse cursor lock**: The game locks the cursor to the window during play. If the game crashes or minimises unexpectedly, the cursor may remain locked until the process is terminated.
- **Draw order on Game Over**: Some UI elements are drawn beneath game objects on the Game Over screen due to the order of draw calls in the loop.
- **Audio file dependency**: If audio files are deleted from the `audio/` directory, the game runs silently without error (by design via the AudioManager's skip logic), but there is no in-game indication that audio is missing.
- **Shop not implemented at mid-semester demo**: The shop state existed at the G2 demo only as a placeholder animation. Full shop functionality was completed in the second half of the semester.
- **Single enemy type at mid-semester**: The Chaser was the only enemy type available at the G2 demo. Elusive and Mage were added for final build.
- **Fixed wave formula at mid-semester**: The original hardcoded wave formula was a bottleneck for content variety and was replaced with the points-budget system after the mid-semester slice. Earlier waves designed under the old system required re-balancing.

---

## 8. Conclusion

Last Stand achieved its core design goals. The game is mechanically coherent, immediately playable, and rewarding to improve at. The core loop — fight, survive, upgrade, repeat — is legible from the first wave, and the points-budget wave system produces genuine increases in difficulty and variety without manual scripting. The dash mechanic, refined through playtesting into its decoupled movement/invincibility form, gives players a high-skill tool that is satisfying to master.

The data-driven architecture was the team's strongest technical decision. Externalising enemy and upgrade definitions into JSON files from Week 7 onward meant that the content pass in Weeks 11–12 was extension work rather than refactoring. The architecture held from the G2 demo through the final build without structural changes — a meaningful outcome for a student project with shifting scope.

The primary lessons from the project are structural and organisational. The accumulation of logic in `game.py` is the clearest example of a pattern that was pragmatic early and costly later. The multi-list object registry created recurring maintenance overhead that a tag-based entity manager would have eliminated. And the team's deadline-driven communication style, while sufficient to ship a complete game, produced unnecessary late-stage pressure that scheduled meetings would have relieved.

Overall, the team is satisfied with the final product and with the process of getting there. The game is complete, playable, and fun.  The team leaves the project with a concrete and specific understanding of what to do differently on the next one.

