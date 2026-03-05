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

        self.debug = False
        self.state = "title"  # title | play | gameover

        self.all_things : list[Thing] = []
        self.all_living : list[Living] = []
        self.all_enemies : list[Enemy] = []

        self.player = Player(self.playfield.center,self.palette.player)
        self.all_living.append(self.player)
        self.all_things.append(self.player)
        self.draw()
    
    def _reset_game(self, *, keep_state: bool = False) -> None:
        self.all_things : list[Thing] = []
        self.all_living : list[Living] = []
        self.all_enemies : list[Enemy] = []

        self.player = Player(self.playfield.center,self.palette.player)
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

        if self.state in {"title", "gameover"} and event.key == pygame.K_SPACE:
            self._reset_game(keep_state=True)
            self.state = "play"

    def update(self, dt: float) -> None:
        for living in self.all_living:
            living.update()

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


    





