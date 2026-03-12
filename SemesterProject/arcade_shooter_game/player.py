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
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 20000.0
        self.friction = 0.5
        self.max_speed = 1000.0
        self._shoot_cooldown = 0.15
        self._shoot_timer = 0.0
        self.health = 10
        self.max_health = 10
        self.damage_cooldown : float = 0.0
        self.damage_cooldown_time : float = .25  # seconds of invincibility after a hit

    def update(self, dt: float) -> None:
        super().update(dt)
        self._shoot_timer = max(0.0, self._shoot_timer - dt)
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
        move_vec = self.input.movement_vector()
        self.velocity += move_vec * self.acceleration * dt
        self.velocity *= self.friction
        if self.velocity.length_squared() > self.max_speed ** 2:
            self.velocity.scale_to_length(self.max_speed)
        self.shape.position += self.velocity * dt

        # clamp to playfield, accounting for radius
        r = self.shape.radius
        self.shape.position.x = max(self.playfield.left + r, min(self.playfield.right - r, self.shape.position.x))
        self.shape.position.y = max(self.playfield.top + r, min(self.playfield.bottom - r, self.shape.position.y))

    def shoot(self):
        if self._shoot_timer > 0.0:
            return None
        self._shoot_timer = self._shoot_cooldown
        aim = self.input.aim_vector(self.shape.position, self.playfield)
        bullet_shape = ShapeContainer(radius=5, position=pygame.Vector2(self.shape.position), color=pygame.Color("#ffffff"))
        return Projectile(internal_shape=bullet_shape, hostile=False, damage=1, lifespan=2.0, direction=aim, speed=700.0)