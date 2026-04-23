# Last Stand — Postmortem
**Team:** Boatmurdered · Michael Barrow · Mitchell Radzienda · Faris Siddiqi  
**Repo:** https://github.com/EverEggs/Comp323Project

---

## What Went Well

**1. The data-driven enemy and upgrade architecture paid off early and kept paying off.**  
Externalising enemy definitions into `enemies.json` from the start (Faris, Week 7–8) meant that adding new enemy types in Weeks 11–12 required JSON entries and enum additions only — no changes to spawning, collision, or the draw loop. The same pattern was applied to upgrades via `upgrades.json`. What could have been a series of disruptive refactors as scope grew became routine extension work. The architecture held from G2 through the final build without structural changes.

**2. The points-budget wave system unlocked content variety without manual scripting.**  
The original fixed-cap wave formula (wave N = hardcoded enemy count) was a bottleneck: adding a new enemy type required deciding by hand how many appeared in each wave. Replacing it with a per-wave points budget (wave 1 = 400 pts, +200/wave) meant enemy mix scaled automatically as the roster grew. This was identified as a problem post-Week 9 slice and fixed before the content pass — the timing was good, and the system has required no further changes since beyond balancing point costs.

**3. The modular structure and manager pattern enabled parallel work across the team.**  
While SOC discipline broke down in places (see below), the parts we did enforce made a real difference. Splitting input handling into `InputManager`, player logic into `player.py`, and enemy behaviour into `enemy.py` meant team members could work on their areas concurrently with minimal conflicts. The `Action` enum abstraction in particular meant Michael could add the dash binding and Mitchell could add the shop select binding independently without either touching the other's code. Getting the module boundaries right early — even partially — was worth the upfront design time.

---

## What Went Wrong

**1. SOC discipline held in most modules but broke down in `game.py`.**  
Spawning logic, collision detection, wave budget calculations, shop state, and the draw loop all accumulated in `game.py` as the project grew. It ended up significantly larger than any other module and harder to navigate than it needed to be. The pattern made sense early on when the game loop was thin, but without a clear rule about what belonged there versus in its own module, it became the natural destination for anything that touched more than one system.

**2. The object registry system was cumbersome and should have been designed once, early.**  
Tracking game objects across separate lists (`all_things`, `all_living`, `all_enemies`, `all_projectiles`) meant that adding or removing any object required up to four list operations, and forgetting one caused subtle bugs. A single entity registry with tag-based filtering — set up in Week 7 when the architecture was first designed — would have handled all of these cases cleanly and been easier to extend as new object types were added. Instead, each new type inherited the same awkward multi-list pattern by convention.

**3. Communication and collaboration was inconsistent.**
We operated mostly under deadlines imposed by the course assignments, which only helped us complete those goals on time.  Much of our work was done in few days leading up to an assignment due date, which strained timeboxing, especially when simultaneous work was needed on large modules like `game.py`.  While we are happy with our product, the team felt a little hurried at times.

---

## What We Would Do Differently

**Establish an entity manager in Week 7 and enforce it.**  
A single registry with tag-based lookup (`get_all(tag="enemy")`) would have replaced the four parallel lists from day one. The interface is simple enough to write in an hour and would have saved time every week thereafter, both in implementation and in debugging removal bugs.

**Set a hard line on what belongs in `game.py`.**  
`game.py` should own the game loop and state machine only — update order, event dispatch, and draw calls. Collision logic, wave budget calculations, and shop logic should each have lived in their own modules or manager classes. A rule like "if it's more than 20 lines and has its own state, it gets its own file" enforced from Week 8 would have kept the file manageable.

**Set scheduled design and logistics meetings throughout semester.**
Communication was mostly ad hoc through Discord, which did not help with item #3 above.  A few more scheduled meetings would've helped take time pressure off and stretch efforts over longer periods rather than in intense bursts.

---

## Iteration Evidence #1: Dash Tuning

**Before playtesting:**  
The initial dash implementation used a speed of 2,800 u/s over 0.12 seconds. The invuln window was tied directly to the dash duration — when the movement ended, invulnerability ended with it.

**Playtest finding:**  
Testers found the dash covered too much distance and felt more like a teleport than a dodge. The tied invuln window also felt punishing: by the time the dash ended, enemies had often already re-closed the gap, making the invuln feel shorter than it was.

**After iteration:**  
Speed was reduced to 1,600 u/s and duration to 0.06 seconds. The invuln window was decoupled into its own variable (`_dash_invuln_time`, 0.18 s) so it extends beyond the movement itself — giving players a moment to reorient after the dash landed. The result felt like a deliberate dodge rather than an escape tool.

## Iteration Evidence #2: Teleporting Enemy Tuning

**Before playtesting:**
The first iteration of the Mage enemy would teleport every 2.5s.

**Playtest finding:**
Testers found this enemy much more annoying than challenging, especially if a wave ended with several of them to "clean up".

**After iteration:**
Timer between teleports was increased to 5s.  This allowed much easier clean up at the end of a wave and led to fewer wasted shots overall as the Mage no longer teleported away before player had time to line up a shot, fire, and the projectile actually reach the target.

---