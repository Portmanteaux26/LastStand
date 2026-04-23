## dash
- initially used same timer for dash duration and invincibility
  - at desired impulse, short duration (0.03s) was too unforgiving on invincibility
  - but long duration (0.12s) went way too far across playfield
- decoupled dash duration from invincibility
  - initial ratio of 1:2 felt reasonable, adjusted down from 0.09s/0.18s to 0.06s/0.12s to achieve desired dash distance

## audio
- added AudioManager that scans a folder for sound files and maps each filename to a playable sound
  - silently skips missing files so the game never crashes over a missing asset
- wired one-shot effects to game events: player hit, round win, game over
- added a looping channel for background music, stopped on game over
  

### shop
- Fleshed out the shop state so it's actually functional
  - Added "shop.py" and "upgrades.json" to control the loading of upgrades and store precreated upgrade cards
  - Upgrades can effect all sorts of player stats, and can be repeatable (will show up in upgrade pool again after being taken) or not (will disappear after being taken once)
  - Upgrades are displayed to the player as a pair of "cards" which can be taken using the interact button implemented this version