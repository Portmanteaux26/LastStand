from __future__ import annotations
from abc import ABC, abstractmethod
import pygame
from arcade_shooter_game.enums import *
from arcade_shooter_game.player import *
from arcade_shooter_game.shop import *
from arcade_shooter_game.things import *

# This file provides utility for objects which can be interacted with using the interact button

class Interactable(ABC):
    shape : ShapeContainer = square_10
    interacted : bool = False
    def interaction(self, player : Player):
        pass
class ShopCard(Interactable):
    def __init__(self, upgrade : Upgrade = Upgrade()):
        self.shape = ShapeContainer(shape=0, radius=-1, width = 200, height = 280)
        self.upgrade = upgrade
        self.interacted = False

    def interaction(self, player : Player):
        if not self.interacted:
            # On interaction we need to read and apply all the values associated with the card to the player.
            player.max_health = max(1,self.upgrade.max_health + player.max_health)
            player.speed = max(100,self.upgrade.speed + player.speed)
            player.shoot_cooldown = max(.01, self.upgrade.bullet_cd * player.shoot_cooldown)
            player.bullet_damage = max(1, self.upgrade.damage + player.bullet_damage)
            player.health = min(player.max_health, self.upgrade.healing + player.health)
        else:
            print("Hey this one has already been interacted with")
class Button(Interactable):
    def interaction(self, player: Player):
        print("This thing was interacted with")
        self.interacted = True


