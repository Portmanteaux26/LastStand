from __future__ import annotations
from dataclasses import dataclass, field
import random
from enum import Enum
from abc import ABC, abstractmethod
import pygame
from arcade_shooter_game.things import *
from arcade_shooter_game.enums import *
from arcade_shooter_game.player import *
from arcade_shooter_game.enemy import *
from arcade_shooter_game.managers import InputManager, AudioManager, Action

class Upgrade():
    # Whether or not this upgrade will stay in the upgrade pool after being taken for the first time
    repeatable : bool = False
    display_name : str = "Default Upgrade"
    speed : float = 0.0
    max_health : int = 0
    damage : int = 0
    # bullet cd is percent based. a value of .8 means that the player's cooldown will be reduced to .8 of its original value. 
    bullet_cd : float = 1.0
    dash_speed : float = 0.0
    # A value added to the player's health, bringing it up to a maximum of the value of max_health after the upgrade is taken.
    healing : int = 0
    desc : str = "default value"
    # The earliest wave this upgrade can appear at
    min_wave : int = 0

    def __init__(self):
        pass

#Default path to the upgrades json file
_UPGRADES_FILE = os.path.join(os.path.dirname(__file__), "upgrades.json")

def load_upgrade(data: dict) -> dict:
    return {
        "repeatable":         bool(data.get("repeatable", False)),
        "display_name":       str(data.get("display_name", "Default Upgrade")),
        "speed":              float(data.get("speed", 0.0)),
        "max_health":         int(data.get("max_health", 0)),
        "damage":             int(data.get("damage", 0)),
        "bullet_cd":          float(data.get("bullet_cd", 1.0)),
        "dash_speed":         float(data.get("dash_speed", 0)),
        "healing":            int(data.get("healing", 0)),
        "desc":               str(data.get("desc","default value")),
        "min_wave":           int(data.get("min_wave", 0))
    }

#Loads all enemy templates from the json file, keyed by name
def load_upgrades(path: str = _UPGRADES_FILE) -> dict[str, dict]:
    with open(path, "r") as f:
        raw = json.load(f)
    templates : dict[str, dict] = {}
    for entry in raw:
        name = entry.get("name", "unknown")
        templates[name] = load_upgrade(entry)
    return templates