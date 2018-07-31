"""
Show the different shape possibilties on buttons.
"""

# coding=utf-8

import ctypes
from random import randint

import pygame
from pygame.constants import *

from graphalama.buttons import Button
from graphalama.constants import ALLANCHOR, NICE_BLUE, BOTTOM
from graphalama.constants import Monokai, TOP
from graphalama.core import WidgetList, Widget
from graphalama.shadow import NoShadow, Shadow
from graphalama.shapes import RoundedRect
from graphalama.text import SimpleText

ctypes.windll.shcore.SetProcessDpiAwareness(2)

WHITE = (255, 255, 255)
pygame.init()
# noinspection PyArgumentList
pygame.key.set_repeat(300, 40)

SCREEN_SIZE = 800, 500
FPS = 60


def new_screen():
    return pygame.display.set_mode(SCREEN_SIZE, DOUBLEBUF | VIDEORESIZE)


def gui():
    global SCREEN_SIZE

    screen = new_screen()
    pygame.display.set_caption('Shadow example')
    clock = pygame.time.Clock()

    def change_shadow():
        def random_shadow():
            dx = randint(-20, 20)
            dy = randint(-20, 20)
            blur = randint(0, 10)
            strength = randint(40, 200)
            return Shadow(dx, dy, blur, strength)

        for w in wid[:-1]:
            w.shadow = random_shadow()
        wid[0].text = str(wid[0].shadow)

    wid = WidgetList([
        Button("Random Shadow", change_shadow, (400, 250), RoundedRect((400, 250), 50, 1, 2),
               bg_color=(150, 232, 230), border_color=NICE_BLUE, shadow=NoShadow(), anchor=ALLANCHOR),
        Widget((55, 35), RoundedRect(), bg_color=Monokai.PINK, anchor=TOP),
        Widget((150, 35), RoundedRect(), bg_color=Monokai.BLUE, shadow=Shadow(5, 5, 0), anchor=TOP),
        Widget((245, 35), RoundedRect(), bg_color=Monokai.ORANGE, shadow=Shadow(-5, 5, 10, 200), anchor=TOP),
        Widget((340, 35), RoundedRect(), bg_color=Monokai.GREEN, shadow=Shadow(5, 5, 5), anchor=TOP),
        Widget((435, 35), RoundedRect(), bg_color=Monokai.YELLOW, shadow=Shadow(0, 0, 10), anchor=TOP),
        Widget((530, 35), RoundedRect(), bg_color=Monokai.PURPLE, shadow=Shadow(5, 5, 0, 200), anchor=TOP),
        Widget((625, 35), RoundedRect(), bg_color=Monokai.BROWN, shadow=Shadow(-2, -2, 5), anchor=TOP),
        Widget((720, 35), RoundedRect(), bg_color=Monokai.BLACK, shadow=Shadow(5, 20, 5), anchor=TOP),
        SimpleText("Shadow(dx, dy, blur, strength)", (400, 490), anchor=BOTTOM)
    ])

    while True:
        for e in pygame.event.get():
            if e.type == QUIT:
                return 0
            elif e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    return 0
                if e.key == K_F4 and e.mod & KMOD_ALT:  # Alt+F4 --> quits
                    return e
            elif wid.update(e):
                continue
            if e.type == VIDEORESIZE:
                wid.resize(e.size, SCREEN_SIZE)
                SCREEN_SIZE = e.size
                screen = new_screen()

        screen.fill(WHITE)
        wid.render(screen)
        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    gui()
