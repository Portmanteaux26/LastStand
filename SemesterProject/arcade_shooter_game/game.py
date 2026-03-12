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
from arcade_shooter_game.managers import InputManager, Action

@dataclass(frozen=True)
class Palette:
    hud: pygame.Color = field(default_factory=lambda: pygame.Color("#000000"))
    panel: pygame.Color = field(default_factory=lambda: pygame.Color("#0F0B31"))
    text: pygame.Color = field(default_factory=lambda: pygame.Color("#e5e9f0"))
    subtle: pygame.Color = field(default_factory=lambda: pygame.Color("#a3adbf"))

    player: pygame.Color = field(default_factory=lambda: pygame.Color("#88c0d0"))
    coin: pygame.Color = field(default_factory=lambda: pygame.Color("#ebcb8b"))
    hazard: pygame.Color = field(default_factory=lambda: pygame.Color("#bf616a"))
    particle: pygame.Color = field(default_factory=lambda: pygame.Color("#a3be8c"))
    wall: pygame.Color = field(default_factory=lambda: pygame.Color("#4c566a"))

class Game:

    fps = 60

    SCREEN_W, SCREEN_H = 16*70, 9*70
    PADDING = 12

    def __init__(self) -> None:
        self.palette = Palette()

        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self.font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 40)

        self.screen_rect = pygame.Rect(0, 0, self.SCREEN_W, self.SCREEN_H)
        self.playfield = pygame.Rect(
            (self.SCREEN_W/2)-((self.SCREEN_H - 2 * self.PADDING)/2),
            self.PADDING,
            self.SCREEN_H - 2 * self.PADDING,
            self.SCREEN_H - 2 * self.PADDING,
            )

        pygame.event.set_grab(True)
        self.debug = False
        self.state = "title"  # title | play | gameover

        self.all_things : list[Thing] = []
        self.all_living : list[Living] = []
        self.all_enemies : list[Enemy] = []
        self.all_projectiles: list[Projectile] = []

        self.spawn_timer : float = 0.0
        self.spawn_interval : float = 1.5  # seconds between spawns
        self.score : int = 0

        self.wave : int = 1
        self.enemies_spawned : int = 0
        self.wave_enemy_cap : int = 5  # round 1 cap

        #Load enemy templates from json
        self.enemy_templates = load_enemies()

        self.input = InputManager()

        self.player = Player(self.playfield.center, self.input, self.playfield, self.palette.player)
        self.all_living.append(self.player)
        self.all_things.append(self.player)
        self.draw()

    def _reset_game(self, *, keep_state: bool = False) -> None:
        self.all_things : list[Thing] = []
        self.all_living : list[Living] = []
        self.all_enemies : list[Enemy] = []
        self.all_projectiles: list[Projectile] = []

        self.spawn_timer = 0.0
        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.wave_enemy_cap = 5

        self.player = Player(self.playfield.center, self.input,self.playfield, self.palette.player)
        self.all_living.append(self.player)
        self.all_things.append(self.player)

    def handle_event(self, event: pygame.event.Event) -> None:

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        if event.key == pygame.K_F1:
            self.debug = not self.debug
            return

        if event.key == pygame.K_r:
            self._reset_game(keep_state=(self.state == "title"))
            return

    def update(self, dt: float) -> None:
        self.input.update()
        if self.input.just_pressed(Action.CONFIRM) and self.state in {"title", "gameover"}:
            self._reset_game(keep_state=True)
            self.state = "play"

        if self.state == "play":
            #Spawn enemies on a timer, up to the wave cap
            self.spawn_timer -= dt
            if self.spawn_timer <= 0 and self.enemies_spawned < self.wave_enemy_cap:
                self.spawn_timer = self.spawn_interval
                self._spawn_enemy()
                self.enemies_spawned += 1

            #TODO: When all enemies for this wave are dead, advance to next wave
            # if self.enemies_spawned >= self.wave_enemy_cap and len(self.all_enemies) == 0:
            #     self.wave += 1
            #     self.enemies_spawned = 0
            #     self.wave_enemy_cap = _get_wave_cap(self.wave)
            #     self.spawn_interval = _get_wave_interval(self.wave)
            #     — also change enemy types, count, etc. based on wave

            for living in self.all_living:
                living.update(dt)

            if self.input.held(Action.SHOOT) or pygame.mouse.get_pressed()[0]:
                new_proj = self.player.shoot()
                if new_proj is not None:
                    self.all_projectiles.append(new_proj)
                    self.all_living.append(new_proj)
                    self.all_things.append(new_proj)

            expired = [p for p in self.all_projectiles if p.lifespan <= 0 or not self.playfield.collidepoint(p.shape.position)]
            for p in expired:
                self.all_projectiles.remove(p)
                self.all_living.remove(p)
                self.all_things.remove(p)

            #Check enemy-player collisions
            self._check_collisions()
            #Check bullet-enemy collisions
            self._check_projectile_collisions()

    def _spawn_enemy(self) -> None:
        #Pick a random edge: 0=top, 1=bottom, 2=left, 3=right
        edge = random.randint(0, 3)
        match edge:
            case 0:  #top
                x = random.uniform(self.playfield.left, self.playfield.right)
                y = self.playfield.top
            case 1:  #bottom
                x = random.uniform(self.playfield.left, self.playfield.right)
                y = self.playfield.bottom
            case 2:  #left
                x = self.playfield.left
                y = random.uniform(self.playfield.top, self.playfield.bottom)
            case 3:  #right
                x = self.playfield.right
                y = random.uniform(self.playfield.top, self.playfield.bottom)

        pos = pygame.Vector2(x, y)
        #For now, always spawn a chaser. Future waves can pick different template names based on wave
        template = self.enemy_templates["chaser"]
        enemy = spawn_from_template(template, pos, self.player)
        self.all_enemies.append(enemy)
        self.all_living.append(enemy)
        self.all_things.append(enemy)

    def _check_collisions(self) -> None:
        #Check each enemy against the player (circle vs circle)
        #Only deal damage if the player's cooldown has expired
        if self.player.damage_cooldown > 0:
            return

        p_pos = self.player.shape.position
        p_r = self.player.shape.radius

        for enemy in self.all_enemies:
            e_pos = enemy.shape.position
            e_r = enemy.shape.radius
            dist_sq = (p_pos - e_pos).length_squared()
            touch_dist = p_r + e_r
            if dist_sq <= touch_dist * touch_dist:
                self.player.health -= enemy.contact_damage
                self.player.damage_cooldown = self.player.damage_cooldown_time
                break  #Only one hit per cooldown window

        #Player dies when health reaches 0
        if self.player.health <= 0:
            self.state = "gameover"

    def _check_projectile_collisions(self) -> None:
        #Check each player bullet against each enemy (circle vs circle)
        projectiles_to_remove : list[Projectile] = []
        enemies_to_remove : list[Enemy] = []

        for proj in self.all_projectiles:
            #Only player bullets hurt enemies
            if proj.hostile:
                continue
            p_pos = proj.shape.position
            p_r = proj.shape.radius
            for enemy in self.all_enemies:
                if enemy in enemies_to_remove:
                    continue
                e_pos = enemy.shape.position
                e_r = enemy.shape.radius
                dist_sq = (p_pos - e_pos).length_squared()
                touch_dist = p_r + e_r
                if dist_sq <= touch_dist * touch_dist:
                    enemy.health -= 4
                    projectiles_to_remove.append(proj)
                    if enemy.health <= 0:
                        enemies_to_remove.append(enemy)
                        self.score += enemy.point_cost
                    break  #Bullet is consumed on first hit

        for proj in projectiles_to_remove:
            if proj in self.all_projectiles:
                self.all_projectiles.remove(proj)
            if proj in self.all_living:
                self.all_living.remove(proj)
            if proj in self.all_things:
                self.all_things.remove(proj)

        for enemy in enemies_to_remove:
            self.all_enemies.remove(enemy)
            self.all_living.remove(enemy)
            self.all_things.remove(enemy)

    def draw(self) -> None:
        self.screen.fill(self.palette.hud)

        pygame.draw.rect(self.screen, self.palette.panel, self.playfield)

        if self.state == "title":
            self._draw_centered("Press Space to Start", y=self.playfield.centery, color=self.palette.text)
        elif self.state == "gameover":
            self._draw_centered("Game Over — Press Space", y=self.playfield.centery, color=self.palette.text)

        for thing in self.all_things:
            obj = thing.shape
            match obj.shape:
                #rectangle
                case 0:
                    rect = pygame.Rect(0,0,obj.width,obj.height)
                    rect.center = obj.position
                    pygame.draw.rect(self.screen, obj.color, rect )
                #circle
                case 1:
                    pygame.draw.circle(self.screen, obj.color, obj.position, obj.radius)
    def _draw_text(self, text: str, pos: tuple[int, int], color: pygame.Color) -> None:
        s = self.font.render(text, True, color)
        self.screen.blit(s, pos)

    def _draw_centered(self, text: str, *, y: int, color: pygame.Color) -> None:
        s = self.big_font.render(text, True, color)
        r = s.get_rect(center=(self.playfield.centerx, y))
        self.screen.blit(s, r)


    





