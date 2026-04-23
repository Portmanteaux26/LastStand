# Last Stand

## 1. Title and Description

**Last Stand** is a top-down arcade shooter where you survive endless waves of increasingly difficult enemies. The core loop is simple: fight enemies, dodge attacks, defeat all enemies in a wave to unlock the upgrade shop, choose your upgrades, then face the next, harder wave. How long can you last before the arena overwhelms you?

## 2. Setup Instructions

**Requirements:**
- Python 3.10 or higher

**Quick Start:**

```bash
# Clone and navigate to repo
git clone https://github.com/EverEggs/Comp323Project.git
cd Comp323Project

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate

# Install and run
pip install -r requirements.txt
python main.py
```

## 3. Controls

| Input                | Action |
|----------------------|--------|
| W / Up Arrow         | Move Up |
| S / Down Arrow       | Move Down |
| A / Left Arrow       | Move Left |
| D / Right Arrow      | Move Right |
| Mouse Movement       | Aim |
| Left Click / Space   | Shoot |
| Shift (Left/Right)   | Dash (high-speed evasion) |
| E                    | Select Upgrade (in shop) |
| Space / Return       | Confirm/Start Game (title screen) |
| Escape               | Quit |

## 4. Known Issues

- **Audio file dependency**: The game will silently skip missing audio files in the `audio/` folder. If audio files are deleted, the game will still run but without sound effects.
- **Mouse grab**: The game locks your mouse cursor to the window during play. If the game crashes or minimizes unexpectedly, your cursor may remain locked.
- **Draw order**: Some UI elements may be drawn under game objects during game over screen

## 5. Credits

**Audio Assets:**
- `enemy_damage.mp3` - "Hitmarker Sound Effect" by aruscio28 ([Freesound.org](https://freesound.org/people/aruscio28/sounds/322640/), Creative Commons license)
- `game_over.mp3` - "negative_beeps" by themusicalnomad ([Pixabay](https://pixabay.com/sound-effects/film-special-effects-negative-beeps-6008/), Pixabay License)
- `player_damage.mp3` - "Retro hurt 2" by Driken5482 ([Pixabay](https://pixabay.com/sound-effects/film-special-effects-retro-hurt-2-236675/), Pixabay License)
- `round_win.mp3` - "Short Success Sound Glockenspiel Treasure Video Game" by FunWithSound ([Pixabay](https://pixabay.com/sound-effects/film-special-effects-short-success-sound-glockenspiel-treasure-video-game-6346/), Pixabay License)

**Libraries & Tools:**
- [Pygame](https://www.pygame.org/) - Game engine and rendering (LGPL v2.1)
- Python system fonts - Text rendering via `pygame.font.SysFont`

**Development:**
- Game developed as a semester-long group project for Comp 323
