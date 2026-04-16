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
  