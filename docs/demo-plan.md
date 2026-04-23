# Last Stand — Demo Plan
**Team:** Boatmurdered · **Target runtime:** 7–10 min (gameplay + iteration story + Q&A)

---

## Roles

| Who | Role |
|-----|------|
| Michael | Player (entire demo); narrates controls and wave spawning |
| Mitchell | Narrates architecture and shop; hosts Q&A |
| Faris | Narrates enemies and audio; closes with enemies.json |

---

## Demo Flow

1. **Mitchell — Architecture (~ 1 min, before launching)**  
   Module map, state machine, JSON-driven design. Frame the key idea: enemy types and upgrades are data, not code.

2. **Michael launches — Controls (~ 1.5 min)**  
   Talk through movement, mouse aim, shoot cooldown, and dash with invuln frames on a live early wave. Point out HUD and screen-shake feedback.

3. **Faris — Enemies and audio (~ 1.5 min)**  
   Restart to wave 1, turn up volume. Faris calls out enemy behaviours, JSON definitions, and audio cues as they appear. Michael lands a deliberate dash through a cluster — **best moment #1**.  Turn down volume.

4. **Mitchell — Shop and upgrades (~ 1.5 min)**  
   Play through to the first wave clear to trigger the shop naturally. Mitchell walks through the interactables system. Michael makes a narrated upgrade choice — **best moment #2**: the loop closing and reopening with a stronger player.

5. **Michael — Wave scaling (~ 1 min)**  
   Continue the same run. Michael narrates the points budget (+200 pts/wave) and spawn interval floor over whatever wave has been reached. The system is visible from wave 1 so it lands regardless of wave count.

6. **Faris — Close (~ 1 min)**  
   Pull up enemies.json and upgrades.json. Hand to Mitchell for Q&A.

---

## Best Moments

1. **Clutch dash** — Michael dashes through a dense cluster, surviving contact that would otherwise kill. Practise this; don't leave it to chance.
2. **Wave clear → shop → upgrade** — the full loop in ~20 seconds. The clearest argument the game is complete.
3. **High-wave density** — a busy mixed-enemy screen if the run gets there naturally; the budget narration covers it either way.

---

## Backup Plan

| Problem | Response |
|---------|----------|
| Crash on launch | Mitchell narrates architecture from repo/IDE while Michael troubleshoots. Move on after 60 seconds if unresolved. |
| Crash mid-demo | Restart to wave 1 and continue from the nearest segment. Treat it as a natural transition. |
| Shop or upgrade bug | Mitchell narrates from code rather than live. |
| Audio not working | Faris acknowledges it as a known open item and continues. |

**Morning-of:** fresh run on the demo machine · confirm audio output · test wave 1 restart command · confirm enemies.json is on screen and readable.

