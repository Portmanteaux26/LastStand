from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
from arcade_shooter_game.enums import *

#Base abstract class. Everything the player can interact with (including the player itself)
#will be a "Thing"
class Thing(ABC):
    shape : ShapeContainer

#Defines things with that move and have updates. Walls, for example, would not be living
#but would still be things. This will include both players and enemies
class Living(Thing):
    speed : float
    health : int
    def update(self, dt : float):
        pass

#Contains all the info for an object's base shape
class ShapeContainer:
    shape : Shape
    radius : int
    width : int
    height : int
    position : pygame.Vector2
    color : pygame.Color
    def __init__(self, shape : Shape = 1, radius : int = 10, width : int = -1, height : int = -1, position : pygame.Vector2 = (0,0), color : pygame.Color = pygame.Color("#ffffff")):
        self.shape = shape
        self.radius = radius
        self.width = width
        self.height = height
        self.color = color
        self.position = position
    #This function is used to create a shape_container as a copy of an existing template
    def clone(template : ShapeContainer) -> ShapeContainer:
        return ShapeContainer(template.shape, template.radius, template.width, template.height, template.position, template.color)
    
#Below are some predefined shapes to use for convenience and efficiency
#For circles, the number denotes radius. For squares, it's the side length.
circle_5 = ShapeContainer(radius = 5)
circle_10 = ShapeContainer() #Just the default actually
circle_20 = ShapeContainer(radius = 20)
square_10 = ShapeContainer(shape=0, radius=-1, width = 10, height = 10)
square_20 = ShapeContainer(shape=0, radius=-1, width = 20, height = 20)

#Projectiles can be owned by the player (hostile = false) or owned by enemies
#(hostile = true)
class Projectile(Living):
    #controls what "team" the projectile belongs to
    hostile : bool
    damage : int
    #direction the projectile is heading, decided on spawning
    direction : pygame.Vector2
    #how long the projectile will last before despawning
    lifespan : float

    def __init__(self, internal_shape: ShapeContainer = None, hostile: bool = True, damage: int = 1,
                 lifespan: float = 10, direction: pygame.Vector2 = pygame.Vector2(1, 0), speed: float = 600.0):
        self.shape = internal_shape if internal_shape is not None else ShapeContainer(radius=5)
        self.hostile = hostile
        self.damage = damage
        self.direction = direction
        self.lifespan = lifespan
        self.speed = speed

    #This function is used to create a projectile as a copy of an existing template
    def clone(template: Projectile, direction: pygame.Vector2, hostile: bool = True):
        return Projectile(template.shape, hostile, template.damage, template.lifespan, direction, template.speed)

    def update(self, dt: float):
        super().update(dt)
        self.shape.position += self.direction * self.speed * dt
        self.lifespan -= dt

