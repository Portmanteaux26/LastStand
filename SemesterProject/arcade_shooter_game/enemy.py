from __future__ import annotations
from arcade_shooter_game.things import *
from abc import ABC, abstractmethod
import pygame
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
    #Load an enemy from file. Used to create enemies using external file types
    #to give modularity to the game and to prevent numerous enemy type classes
    #from arising and bloating the py files
   
    def __init__(self):
        pass
    def Update(self):
        super()
        match self.move_style:
            #Chaser
            case 0:
                pass
            #Shy
            case 1:
                pass
            #Goldilocks
            case 2:
                pass
            #Bouncer
            case 3:
                pass
            #Random
            case 4:
                pass
            #Stationary
            case 5:
                pass 

#Used to load enemies from file
def load_enemy() -> Enemy:
    pass
#Loads all enemies in the given file
def load_enemies() -> list[Enemy]:
    pass