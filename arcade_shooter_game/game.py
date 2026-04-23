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
from arcade_shooter_game.shop import *
from arcade_shooter_game.interactables import *
from arcade_shooter_game.managers import InputManager, AudioManager, Action


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

    card: pygame.Color = field(default_factory=lambda: pygame.Color("#e7e3d2"))
    card_border: pygame.Color = field(default_factory=lambda: pygame.Color("#d6a062"))
    card_text: pygame.Color = field(default_factory=lambda: pygame.Color("#000000"))


class Game:
    fps = 60

    SCREEN_W, SCREEN_H = 16 * 70, 9 * 70
    PADDING = 12

    def __init__(self) -> None:
        self.palette = Palette()

        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        self.card_font = pygame.font.SysFont(None,20)
        self.font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 40)

        self.screen_rect = pygame.Rect(0, 0, self.SCREEN_W, self.SCREEN_H)
        self.playfield = pygame.Rect(
            (self.SCREEN_W / 2) - ((self.SCREEN_H - 2 * self.PADDING) / 2),
            self.PADDING,
            self.SCREEN_H - 2 * self.PADDING,
            self.SCREEN_H - 2 * self.PADDING,
        )

        pygame.event.set_grab(True)
        self.debug = False
        self.state = "title"  # title | play | gameover
        # additional states used to control behavior of play, since we still want to control player movement, collisions, etc. while in the shop
        self.play_state = "wave"  # wave | shop
        self.choice_made = False
        self.all_things: list[Thing] = []
        self.all_living: list[Living] = []
        self.all_enemies: list[Enemy] = []
        self.all_projectiles: list[Projectile] = []
        self.interactables: list[Interactable] = []

        self._shake_timer = 0.0
        self._shake_duration = 0.2
        self._shake_magnitude = 6

        self.spawn_timer: float = 0.0
        self.spawn_interval: float = 1.5  # seconds between spawns
        self.score: int = 0

        self.wave: int = 1
        self.enemies_spawned: int = 0
        self.wave_roster: list[str] = []
        self.wave_enemy_cap: int = 0

        # Load enemy templates from json
        self.enemy_templates = load_enemies()
        self.wave_roster = self._build_wave_roster(self.wave)
        self.wave_enemy_cap = len(self.wave_roster)

        # Load upgrade templates from json
        self.upgrade_templates = load_upgrades()
        self.upgrade_pool = self.upgrade_templates

        self.input = InputManager()
        self.audio = AudioManager()

        self.player = Player(self.playfield.center, self.input, self.playfield, self.palette.player)
        self.all_living.append(self.player)
        self.all_things.append(self.player)
        self.draw()

    def _reset_game(self, *, keep_state: bool = False) -> None:
        self.all_things: list[Thing] = []
        self.all_living: list[Living] = []
        self.all_enemies: list[Enemy] = []
        self.all_projectiles: list[Projectile] = []

        self.shop_start = False
        self.play_state = "wave"
        self.spawn_timer = 0.0
        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.shop_timer = 0.0
        self.wave_roster = self._build_wave_roster(self.wave)
        self.upgrade_pool = self.upgrade_templates
        self.wave_enemy_cap = len(self.wave_roster)

        self.player = Player(self.playfield.center, self.input, self.playfield, self.palette.player)
        self.all_living.append(self.player)
        self.all_things.append(self.player)

    def _clear_hostile_projectiles(self) -> None:
        """Remove all enemy projectiles from the game."""
        projectiles_to_remove = [p for p in self.all_projectiles if p.hostile]
        for proj in projectiles_to_remove:
            self.all_projectiles.remove(proj)
            self.all_living.remove(proj)
            self.all_things.remove(proj)

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
            self.play_state = "wave"
            self.audio.play_loop("bgm")

        if self.state == "play":
            self._shake_timer = max(0.0, self._shake_timer - dt)
            # Spawn enemies on a timer, up to the wave cap
            if self.play_state == "wave":
                self.spawn_timer -= dt
                if self.spawn_timer <= 0 and self.enemies_spawned < self.wave_enemy_cap:
                    self.spawn_timer = self.spawn_interval
                    self._spawn_enemy()
                    self.enemies_spawned += 1
                # If all enemies are dead we move to the shop
                print(len(self.all_enemies))
                if self.enemies_spawned >= self.wave_enemy_cap and len(self.all_enemies) == 0:
                    print("setting play state to shop")
                    self._clear_hostile_projectiles()
                    self.play_state = "shop"
                    self.shop_start = True
                    self.shop_timer = 10
                    self.audio.play("round_win")
                # Eventually, shop will contain upgrades you can select. For now, we just count down a five second timer to break up the waves.
            if self.play_state == "shop":
                if self.shop_start:
                    self.shop_start = False
                    print("Starting shop!")
                    # Spawn in interactable "cards"
                    # First, we find the upgrades that can be used at this wave
                    valid_upgrades = {}
                    for k, v in self.upgrade_pool.items():
                        if v["min_wave"] <= self.wave:
                            valid_upgrades[k] = v
                    # Then, we grab two random ones.
                    chosen_upgrades = random.sample(list(valid_upgrades.items()),2)
                    upgrade_1 = ShopCard(chosen_upgrades[0])
                    upgrade_2 = ShopCard(chosen_upgrades[1])
                    print(upgrade_1.upgrade)
                    print(upgrade_2.upgrade)
                    upgrade_1.shape.position = (self.playfield.centerx-150,self.playfield.centery+50)
                    upgrade_1.shape.color = self.palette.card
                    upgrade_2.shape.position = (self.playfield.centerx+150,self.playfield.centery+50)
                    upgrade_2.shape.color = self.palette.card
                    self.interactables.append(upgrade_1)
                    self.interactables.append(upgrade_2)
                self.shop_timer -= dt

                # Select upgrade
                if self.input.just_pressed(Action.SELECT):
                    for i, interactable in enumerate(self.interactables):
                        shape = interactable.shape

                        if shape.shape == 0:
                            rect = pygame.Rect(0, 0, shape.width, shape.height)
                            rect.center = shape.position

                            if rect.collidepoint(self.player.shape.position):
                                self.trigger_interactable(i)
                                break

                # This will be true if the player has interacted with one of the shop's interactables
                if self.choice_made:
                    self.shop_timer = 0
                    self.choice_made = False



                if self.shop_timer <= 0:
                    self.interactables = []
                    self.wave += 1
                    self.enemies_spawned = 0
                    self.spawn_interval = self._get_spawn_interval(self.wave)
                    self.wave_roster = self._build_wave_roster(self.wave)
                    self.wave_enemy_cap = len(self.wave_roster)
                    self.play_state = "wave"

            for living in self.all_living:
                living.update(dt)

            if self.input.held(Action.SHOOT) or pygame.mouse.get_pressed()[0]:
                new_proj = self.player.shoot()
                if new_proj is not None:
                    self.all_projectiles.append(new_proj)
                    self.all_living.append(new_proj)
                    self.all_things.append(new_proj)

            for enemy in self.all_enemies:
                enemy_proj = enemy.shoot()
                if enemy_proj is not None:
                    self.all_projectiles.append(enemy_proj)
                    self.all_living.append(enemy_proj)
                    self.all_things.append(enemy_proj)

            expired = [p for p in self.all_projectiles if
                       p.lifespan <= 0 or not self.playfield.collidepoint(p.shape.position)]
            for p in expired:
                self.all_projectiles.remove(p)
                self.all_living.remove(p)
                self.all_things.remove(p)

            # Check enemy-player collisions
            self._check_collisions()
            # Check bullet-enemy collisions
            self._check_projectile_collisions()

    def _spawn_enemy(self) -> None:
        # Pick a random edge: 0=top, 1=bottom, 2=left, 3=right
        edge = random.randint(0, 3)
        match edge:
            case 0:  # top
                x = random.uniform(self.playfield.left, self.playfield.right)
                y = self.playfield.top
            case 1:  # bottom
                x = random.uniform(self.playfield.left, self.playfield.right)
                y = self.playfield.bottom
            case 2:  # left
                x = self.playfield.left
                y = random.uniform(self.playfield.top, self.playfield.bottom)
            case 3:  # right
                x = self.playfield.right
                y = random.uniform(self.playfield.top, self.playfield.bottom)

        pos = pygame.Vector2(x, y)
        name = self.wave_roster[self.enemies_spawned]
        template = self.enemy_templates[name]
        enemy = spawn_from_template(template, pos, self.player, self.playfield)
        self.all_enemies.append(enemy)
        self.all_living.append(enemy)
        self.all_things.append(enemy)

    def _check_collisions(self) -> None:
        # Check each enemy against the player (circle vs circle)
        # Only deal damage if the player's cooldown has expired
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
                # basic feedback for collision with enemy
                self._shake_timer = self._shake_duration
                self.player.health -= enemy.contact_damage
                self.player.damage_cooldown = self.player.damage_cooldown_time
                self.audio.play("player_damage")
                break  # Only one hit per cooldown window

        # Player dies when health reaches 0
        if self.player.health <= 0:
            self._shake_timer = 0.0
            self.audio.stop_loop()
            self.audio.play("game_over")
            self.state = "gameover"

    def _check_projectile_collisions(self) -> None:
        # Check each player bullet against each enemy (circle vs circle)
        projectiles_to_remove: list[Projectile] = []
        enemies_to_remove: list[Enemy] = []

        for proj in self.all_projectiles:
            # Only player bullets hurt enemies
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
                    enemy._hit_flash_timer = 0.1
                    projectiles_to_remove.append(proj)
                    self.audio.play("enemy_damage")
                    if enemy.health <= 0:
                        enemies_to_remove.append(enemy)
                        self.score += enemy.point_cost
                    break  # Bullet is consumed on first hit

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

        # Check hostile (enemy) bullets against the player
        if self.player.damage_cooldown <= 0:
            for proj in list(self.all_projectiles):
                if not proj.hostile:
                    continue
                p_pos = proj.shape.position
                p_r = proj.shape.radius
                pl_pos = self.player.shape.position
                pl_r = self.player.shape.radius
                dist_sq = (p_pos - pl_pos).length_squared()
                touch_dist = p_r + pl_r
                if dist_sq <= touch_dist * touch_dist:
                    self.player.health -= proj.damage
                    self.player.damage_cooldown = self.player.damage_cooldown_time
                    self._shake_timer = self._shake_duration
                    self.audio.play("player_damage")
                    if proj in self.all_projectiles:
                        self.all_projectiles.remove(proj)
                    if proj in self.all_living:
                        self.all_living.remove(proj)
                    if proj in self.all_things:
                        self.all_things.remove(proj)
                    break

            if self.player.health <= 0:
                self._shake_timer = 0.0
                self.audio.stop_loop()
                self.audio.play("game_over")
                self.state = "gameover"

    # ----Wave calculation methods

    def _get_wave_budget(self, wave: int) -> int:
        """Points budget available to spend on enemies each wave. Grows steadily."""
        return 400 + (wave - 1) * 200

    def _build_wave_roster(self, wave: int) -> list[str]:
        """
        Randomly fill a wave roster by spending the points budget.
        Picks enemy types by name, weighted so cheaper enemies are more common
        early on, while more expensive ones appear as the budget allows.
        Returns a shuffled list of template names to spawn in order.
        """
        budget = self._get_wave_budget(wave)
        # Sort templates cheapest-first so we can always try the cheapest fallback
        affordable = sorted(
            self.enemy_templates.items(),
            key=lambda kv: kv[1]["point_cost"]
        )
        cheapest_cost = affordable[0][1]["point_cost"]
        roster: list[str] = []

        while budget >= cheapest_cost:
            # Only consider enemies we can still afford
            choices = [(name, data) for name, data in affordable
                       if data["point_cost"] <= budget]
            if not choices:
                break
            name, data = random.choice(choices)
            roster.append(name)
            budget -= data["point_cost"]

        random.shuffle(roster)
        return roster

    def _get_spawn_interval(self, wave: int) -> float:
        if wave < 10:
            return 1.5 - (wave * 0.1)
        return 0.5

    def trigger_interactable(self, index: int):
        interactable = self.interactables[index]
        interactable.interaction(self.player)

        if isinstance(interactable, ShopCard):
            if not interactable.upgrade[1]["repeatable"]:
                del self.upgrade_pool[interactable.upgrade[0]]

        del self.interactables[index]
        self.choice_made = True

    def draw(self) -> None:
        self.screen.fill(self.palette.hud)

        shake_offset = pygame.Vector2(0, 0)
        if self._shake_timer > 0:
            shake_offset = pygame.Vector2(
                random.uniform(-self._shake_magnitude, self._shake_magnitude),
                random.uniform(-self._shake_magnitude, self._shake_magnitude)
            )
        shaken_playfield = self.playfield.move(shake_offset)
        pygame.draw.rect(self.screen, self.palette.panel, shaken_playfield)

        if self.state == "title":
            self._draw_centered("Press Space to Start", y=self.playfield.centery, color=self.palette.text)
            return
        elif self.state == "gameover":
            self._draw_centered("Game Over — Press Space", y=self.playfield.centery, color=self.palette.text)
            self._draw_centered(f"Highest Wave Reached: {self.wave}", y=self.playfield.centery + 40,
                                color=self.palette.text)
        elif self.state == "play":
            if self.play_state == "shop":
                
                for interactable in self.interactables:
                    obj = interactable.shape
                    pos = pygame.Vector2(obj.position) + shake_offset
                    match obj.shape:
                        case 0:
                            if isinstance(interactable, ShopCard):
                                rect = pygame.Rect(0, 0, obj.width+15, obj.height+15)
                                rect.center = pos
                                pygame.draw.rect(self.screen, self.palette.card_border, rect)
                                rect.width-=15
                                rect.height-=15
                                rect.center = pos
                                pygame.draw.rect(self.screen, obj.color, rect)
                                self._draw_text_center_align((interactable.upgrade[1]["display_name"]),(pos.x,pos.y+15-obj.height/2),self.palette.card_text)
                                self._draw_multiline((interactable.upgrade[1]["desc"]),(pos.x-obj.width/2,pos.y),self.palette.card_text)

                        case 1:
                            pygame.draw.circle(self.screen, obj.color, pos, obj.radius)

                bullets_per_second = 1/self.player.shoot_cooldown

                self._draw_centered(f"Choose an upgrade.",
                                    y=50, color=self.palette.text)
                self._draw_centered(f"{self.shop_timer:.1f} seconds until next wave.",
                                    y=80, color=self.palette.text)
                self._draw_multiline(f"Health: {self.player.health}/{self.player.max_health}\nDamage: {self.player.bullet_damage}\nBullets/Second: {bullets_per_second:.2f}\nSpeed: {self.player.max_speed}",(5,5),self.palette.text)

            if self.play_state == "wave":
                self._draw_text(f"Wave: {self.wave}", (10, 10), color=self.palette.text)
                self._draw_text(f"Enemies Left: {(self.wave_enemy_cap - self.enemies_spawned) + len(self.all_enemies)}",
                                (10, 30), color=self.palette.text)
                self._draw_text(f"Health: {self.player.health}/{self.player.max_health}", (10, 50), color=self.palette.text)
        for thing in self.all_things:
            obj = thing.shape
            pos = pygame.Vector2(obj.position) + shake_offset
            match obj.shape:
                case 0:
                    rect = pygame.Rect(0, 0, obj.width, obj.height)
                    rect.center = pos
                    pygame.draw.rect(self.screen, obj.color, rect)
                case 1:
                    pygame.draw.circle(self.screen, obj.color, pos, obj.radius)

    def _draw_text(self, text: str, pos: tuple[int, int], color: pygame.Color) -> None:
        s = self.font.render(text, True, color)
        self.screen.blit(s, pos)

    def _draw_text_center_align(self, text: str, pos: tuple[int, int], color: pygame.Color) -> None:
        s = self.font.render(text, True, color)
        self.screen.blit(s, (pos[0]-s.get_width()/2,pos[1]))

    #Draws a multiline with the topleft of the text at pos
    def _draw_multiline(self, text: str, pos: tuple[int, int], color: pygame.Color) -> None:
        lines = []
        for i, line in enumerate(text.split('\n')):
            txt_surf = self.card_font.render(line, True, color)
            self.screen.blit(txt_surf, (pos[0], pos[1]+20*i))


    def _draw_centered(self, text: str, *, y: int, color: pygame.Color) -> None:
        s = self.big_font.render(text, True, color)
        r = s.get_rect(center=(self.playfield.centerx, y))
        self.screen.blit(s, r)