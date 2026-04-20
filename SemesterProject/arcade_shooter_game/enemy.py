from __future__ import annotations
from arcade_shooter_game.things import *
from abc import ABC, abstractmethod
import pygame
import json
import os
import random
import math
from dataclasses import dataclass, field

#This will encompass all enemies. Their behaviors will be defined by individual values
#Namely in the attributes "movement_style" and "attack_style"
class Enemy(Living):
    move_style : Movement_styles
    #How far enemies will attack from.
    attack_range : float
    contact_damage : int
    ranged_damage : int
    #Used to determine score values and how many of each enemy spawns a wave
    point_cost : int
    #Paremeters used to control the behavior of the shy and goldilocks 
    #Movement types
    movement_min_dist : float
    movement_max_dist : float
    #Reference to the target this enemy is tracking (the player)
    target : Living
   
    def __init__(self, pos: pygame.Vector2, target: Living,
                 playfield: pygame.Rect,
                 color: pygame.Color = pygame.Color("#bf616a"),
                 move_style: Movement_styles = Movement_styles.MOVEMENT_CHASER,
                 speed: float = 120.0, health: int = 1,
                 radius: int = 12, contact_damage: int = 1,
                 ranged_damage: int = 0, attack_range: float = 0.0,
                 point_cost: int = 100,
                 movement_min_dist: float = 0.0,
                 movement_max_dist: float = 0.0,
                 shoot_cooldown: float = 0.0):
        self.shape = ShapeContainer(position=pos, color=color, radius=radius)
        self._base_color = color
        self._hit_flash_timer = 0.0
        self.target = target
        self.playfield = playfield
        self.move_style = move_style
        self.speed = speed
        self.health = health
        self.contact_damage = contact_damage
        self.ranged_damage = ranged_damage
        self.attack_range = attack_range
        self.point_cost = point_cost
        self.movement_min_dist = movement_min_dist
        self.movement_max_dist = movement_max_dist
        self.shoot_cooldown = shoot_cooldown
        self._shoot_timer = 0.0

        angle = random.uniform(0, 2 * math.pi)
        self._random_dir = pygame.Vector2(math.cos(angle), math.sin(angle))
        self._random_timer = random.uniform(0.5, 1.5)

    def shoot(self) -> Projectile | None:
        if self.shoot_cooldown <= 0 or self._shoot_timer > 0:
            return None
        self._shoot_timer = self.shoot_cooldown
        direction = self.target.shape.position - self.shape.position
        if direction.length_squared() > 0:
            direction.normalize_ip()
        bullet_shape = ShapeContainer(
            radius=4,
            position=pygame.Vector2(self.shape.position),
            color=self._base_color,
        )
        return Projectile(
            internal_shape=bullet_shape,
            hostile=True,
            damage=self.ranged_damage,
            lifespan=3.0,
            direction=direction,
            speed=350.0,
        )

    def update(self, dt: float) -> None:
        super().update(dt)
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        # basic feedback on collision with projectile
        if self._hit_flash_timer > 0:
            self._hit_flash_timer -= dt
            self.shape.color = pygame.Color("#ffffff") if self._hit_flash_timer > 0 else self._base_color
        match self.move_style:
            #Chaser — move directly toward the target
            case Movement_styles.MOVEMENT_CHASER:
                direction = self.target.shape.position - self.shape.position
                if direction.length_squared() > 0:
                    direction.normalize_ip()
                self.shape.position += direction * self.speed * dt
            #Shy
            case Movement_styles.MOVEMENT_SHY:
                pass
            #Elusive — stay within a distance band from the target
            case Movement_styles.MOVEMENT_ELUSIVE:
                direction = self.target.shape.position - self.shape.position
                dist = direction.length()
                if dist > 0:
                    direction.normalize_ip()
                if dist > self.movement_max_dist:
                    self.shape.position += direction * self.speed * dt
                elif dist < self.movement_min_dist:
                    self.shape.position -= direction * self.speed * dt
            #Bouncer
            case Movement_styles.MOVEMENT_BOUNCER:
                pass
            #Mage — teleport to a random spot, avoiding the player
            case Movement_styles.MOVEMENT_MAGE:
                self._random_timer -= dt
                if self._random_timer <= 0:
                    r = self.shape.radius
                    min_player_dist = 80.0
                    for _ in range(20):
                        x = random.uniform(self.playfield.left + r, self.playfield.right - r)
                        y = random.uniform(self.playfield.top + r, self.playfield.bottom - r)
                        candidate = pygame.Vector2(x, y)
                        if (candidate - self.target.shape.position).length_squared() >= min_player_dist ** 2:
                            break
                    self.shape.position = candidate
                    self._random_timer = random.uniform(1.0, 2.5)
            #Stationary
            case Movement_styles.MOVEMENT_STATIONARY:
                pass 

        r = self.shape.radius
        self.shape.position.x = max(self.playfield.left + r, min(self.playfield.right - r, self.shape.position.x))
        self.shape.position.y = max(self.playfield.top + r, min(self.playfield.bottom - r, self.shape.position.y))

#Default path to the enemies json file
_ENEMIES_FILE = os.path.join(os.path.dirname(__file__), "enemies.json")

#Used to load a single enemy template from a dict (one entry from the json)
def load_enemy(data: dict) -> dict:
    return {
        "color":              pygame.Color(data.get("color", "#bf616a")),
        "move_style":         Movement_styles(data.get("move_style", 0)),
        "speed":              float(data.get("speed", 120.0)),
        "health":             int(data.get("health", 1)),
        "radius":             int(data.get("radius", 12)),
        "contact_damage":     int(data.get("contact_damage", 1)),
        "ranged_damage":      int(data.get("ranged_damage", 0)),
        "attack_range":       float(data.get("attack_range", 0.0)),
        "point_cost":         int(data.get("point_cost", 100)),
        "movement_min_dist":  float(data.get("movement_min_dist", 0.0)),
        "movement_max_dist":  float(data.get("movement_max_dist", 0.0)),
        "shoot_cooldown":     float(data.get("shoot_cooldown", 0.0)),
    }

#Loads all enemy templates from the json file, keyed by name
def load_enemies(path: str = _ENEMIES_FILE) -> dict[str, dict]:
    with open(path, "r") as f:
        raw = json.load(f)
    templates : dict[str, dict] = {}
    for entry in raw:
        name = entry.get("name", "unknown")
        templates[name] = load_enemy(entry)
    return templates

#Creates an Enemy instance from a loaded template
def spawn_from_template(template: dict, pos: pygame.Vector2, target: Living, playfield: pygame.Rect) -> Enemy:
    return Enemy(pos, target, playfield, **template)