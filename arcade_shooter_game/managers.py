from __future__ import annotations
from enum import Enum, auto
from pathlib import Path
import pygame


class Action(Enum):
    MOVE_UP     = auto()
    MOVE_DOWN   = auto()
    MOVE_LEFT   = auto()
    MOVE_RIGHT  = auto()
    SHOOT       = auto()
    PAUSE       = auto()
    CONFIRM     = auto()
    SELECT      = auto()
    DASH        = auto()

DEFAULT_BINDINGS: dict[Action, list[int]] = {
    Action.MOVE_UP:     [pygame.K_w, pygame.K_UP],
    Action.MOVE_DOWN:   [pygame.K_s, pygame.K_DOWN],
    Action.MOVE_LEFT:   [pygame.K_a, pygame.K_LEFT],
    Action.MOVE_RIGHT:  [pygame.K_d, pygame.K_RIGHT],
    Action.SHOOT:       [pygame.K_SPACE, pygame.K_j],
    Action.PAUSE:       [pygame.K_ESCAPE],
    Action.CONFIRM:     [pygame.K_SPACE, pygame.K_RETURN],
    Action.SELECT:      [pygame.K_e],
    Action.DASH:        [pygame.K_LSHIFT, pygame.K_RSHIFT]
}

class InputManager:
    """
    Tracks per-frame action states.
    """
    def __init__(self, bindings: dict[Action, list[int]] | None = None) -> None:
        self._bindings: dict[Action, list[int]] = (
            {k: list(v) for k, v in DEFAULT_BINDINGS.items()}
            if bindings is None
            else bindings
        )
        self._held:         set[Action] = set()
        self._just_pressed: set[Action] = set()
        self._just_released: set[Action] = set()


    def held(self, action: Action) -> bool:
        """True every frame the action's key is held down."""
        return action in self._held

    def just_pressed(self, action: Action) -> bool:
        """True only on the first frame the action's key is pressed."""
        return action in self._just_pressed

    def just_released(self, action: Action) -> bool:
        """True only on the frame the action's key is released."""
        return action in self._just_released

    def movement_vector(self) -> pygame.Vector2:
        """
        Returns a (possibly zero) direction vector from the four movement
        actions. Normalized when diagonal so the speed stays consistent.
        """
        vec = pygame.Vector2(0, 0)
        if self.held(Action.MOVE_LEFT):  vec.x -= 1
        if self.held(Action.MOVE_RIGHT): vec.x += 1
        if self.held(Action.MOVE_UP):    vec.y -= 1
        if self.held(Action.MOVE_DOWN):  vec.y += 1
        if vec.length_squared() > 0:
            vec.normalize_ip()
        return vec

    def aim_vector(self, from_pos: pygame.Vector2, bounds: pygame.Rect) -> pygame.Vector2:
        """
        Returns a (possibly zero) direction vector from player to mouse pos.
        Normalized when diagonal so the speed stays consistent.
        """
        mouse = pygame.Vector2(pygame.mouse.get_pos())
        mouse.x = max(bounds.left, min(bounds.right, mouse.x))
        mouse.y = max(bounds.top, min(bounds.bottom, mouse.y))
        direction = mouse - from_pos
        if direction.length_squared() > 0:
            direction.normalize_ip()
        return direction

    def bind(self, action: Action, keys: list[int]) -> None:
        """Replace the key list for a given action."""
        self._bindings[action] = keys

    def update(self) -> None:
        """
        Reads the current pygame key state and refreshes held /
        just_pressed / just_released sets.  Call before any game logic.
        """
        prev_held = self._held.copy()
        self._held.clear()

        keys = pygame.key.get_pressed()
        for action, key_list in self._bindings.items():
            if any(keys[k] for k in key_list):
                self._held.add(action)

        self._just_pressed  = self._held  - prev_held
        self._just_released = prev_held   - self._held


_SOUND_DIR = Path(__file__).resolve().parent.parent / "audio"
_SUPPORTED_EXTENSIONS = (".mp3")


class AudioManager:
    """
    Loads sound files from the audio/ directory and exposes play() / play_loop().
    Missing files are silently ignored so the game runs without audio assets.
    """

    def __init__(self) -> None:
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._loop_channel: pygame.mixer.Channel | None = None
        self._volumes: dict[str, float] = {}  # Store per-sound volumes
        self._load_all()
        # BGM is loud by default, reduce it to 60%
        self.set_volume("bgm", 0.6)

    def _load_all(self) -> None:
        if not _SOUND_DIR.is_dir():
            return
        for ext in _SUPPORTED_EXTENSIONS:
            for path in _SOUND_DIR.glob(f"*{ext}"):
                name = path.stem
                if name not in self._sounds:
                    self._sounds[name] = pygame.mixer.Sound(str(path))

    def set_volume(self, name: str, volume: float) -> None:
        """Set volume for a specific sound (0.0 to 1.0)."""
        volume = max(0.0, min(1.0, volume))  # Clamp to 0-1
        self._volumes[name] = volume
        if name in self._sounds:
            self._sounds[name].set_volume(volume)

    def play(self, name: str) -> None:
        sound = self._sounds.get(name)
        if sound is not None:
            if name in self._volumes:
                sound.set_volume(self._volumes[name])
            sound.play()

    def play_loop(self, name: str) -> None:
        self.stop_loop()
        sound = self._sounds.get(name)
        if sound is not None:
            if name in self._volumes:
                sound.set_volume(self._volumes[name])
            self._loop_channel = sound.play(loops=-1)

    def stop_loop(self) -> None:
        if self._loop_channel is not None:
            self._loop_channel.stop()
            self._loop_channel = None