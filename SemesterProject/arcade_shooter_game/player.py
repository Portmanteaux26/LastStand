from __future__ import annotations
from arcade_shooter_game.things import *
from arcade_shooter_game.managers import InputManager, Action


#Standard player class. Inherits from living (and thus thing) to ensure consistency across
#Objects
class Player(Living):
    def __init__(self, pos: pygame.Vector2, input_mgr: InputManager, playfield: pygame.Rect,
                 pal_color: pygame.Color = "#ffffff"):
        self.input = input_mgr
        self.playfield = playfield
        self.shape = ShapeContainer(position=pos, color=pal_color, radius=16)
        self._base_color = pal_color
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 20000.0
        self.friction = 0.5
        self.max_speed = 1000.0
        self.shoot_cooldown = 0.15
        self._shoot_timer = 0.0
        self.health = 10
        self.max_health = 10
        self.bullet_damage = 1
        self.damage_cooldown : float = 0.0
        self.damage_cooldown_time : float = .25  # seconds of invincibility after a hit

        # dash
        self._dash_speed : float = 1600.0        # peak velocity during dash
        self._dash_duration : float = 0.06       # how long the dash lasts (seconds)
        self._dash_invuln_time : float = 0.12    # how long invuln lasts (can exceed dash duration)
        self._dash_cooldown_time : float = 0.6   # minimum gap between dashes (seconds)
        self._dash_timer : float = 0.0           # > 0 while currently dashing
        self._dash_cooldown : float = 0.0        # > 0 while on cooldown
        self._dash_direction : pygame.Vector2 = pygame.Vector2(0, -1)  # last known facing dir

    def update(self, dt: float) -> None:
        super().update(dt)
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        self._dash_cooldown = max(0.0, self._dash_cooldown - dt)

        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

        move_vec = self.input.movement_vector()

        # keep _dash_direction in sync with actual movement so the dash
        # always fires in the direction the player last walked
        if move_vec.length_squared() > 0:
            self._dash_direction = pygame.Vector2(move_vec)

        # --- initiate dash ---
        if (self.input.just_pressed(Action.DASH)
                and self._dash_cooldown <= 0.0
                and self._dash_timer <= 0.0):
            self._dash_timer = self._dash_duration
            self._dash_cooldown = self._dash_cooldown_time
            self.velocity = self._dash_direction * self._dash_speed
            # grant invincibility for the full dash window
            self.damage_cooldown = max(self.damage_cooldown, self._dash_invuln_time)

        # --- tick active dash ---
        if self._dash_timer > 0.0:
            self._dash_timer -= dt
            # lock out friction and acceleration so the burst carries through
            self.shape.position += self.velocity * dt
        else:
            # normal movement
            self.velocity += move_vec * self.acceleration * dt
            self.velocity *= self.friction
            if self.velocity.length_squared() > self.max_speed ** 2:
                self.velocity.scale_to_length(self.max_speed)
            self.shape.position += self.velocity * dt

        # --- colour feedback ---
        dashing = self._dash_timer > 0.0
        if dashing:
            self.shape.color = pygame.Color("#aaddff")   # blue-white flash while dashing
        elif self.damage_cooldown > 0:
            self.shape.color = pygame.Color("#ffffff")   # white flash while hurt
        else:
            self.shape.color = self._base_color

        # clamp to playfield, accounting for radius
        r = self.shape.radius
        self.shape.position.x = max(self.playfield.left + r, min(self.playfield.right - r, self.shape.position.x))
        self.shape.position.y = max(self.playfield.top + r, min(self.playfield.bottom - r, self.shape.position.y))

    def shoot(self):
        if self._shoot_timer > 0.0:
            return None
        self._shoot_timer = self.shoot_cooldown
        aim = self.input.aim_vector(self.shape.position, self.playfield)
        bullet_shape = ShapeContainer(radius=5, position=pygame.Vector2(self.shape.position), color=pygame.Color("#ffffff"))
        return Projectile(internal_shape=bullet_shape, hostile=False, damage = self.bullet_damage, lifespan=2.0, direction=aim, speed=700.0)