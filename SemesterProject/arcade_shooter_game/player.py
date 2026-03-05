from __future__ import annotations
import pygame
from arcade_shooter_game.enums import *
from arcade_shooter_game.things import *


#Standard player class. Inherits from living (and thus thing) to ensure consistency across
#Objects
class Player(Living):
    def __init__(self, pos : pygame.Vector2, pal_color : pygame.color = "#ffffff"):
        self.shape = Shape_Container(position = pos,color=pal_color, radius=16)
        self.velocity = pygame.Vector2(0,0)
        self.acceleration : 100.0
        self.friction : 5.0
        self.max_speed = 300.0
    def Update():
        super()