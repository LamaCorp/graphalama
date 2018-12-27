"""
Show the different color possibilties on buttons.
"""

# coding=utf-8

import pygame
from pygame.constants import *

from graphalama.buttons import Button
from graphalama.colors import Gradient, MultiGradient
from graphalama.constants import ORANGE, PINK, RIGHT, LEFT, TOP, BLUE, RAINBOW, BOTTOM
from graphalama.core import WidgetList
from graphalama.shapes import RoundedRect


try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except AttributeError as e:
    # This sets the DPI only on windows
    pass

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
    pygame.display.set_caption('Shapes example')
    clock = pygame.time.Clock()

    def nop():
        ...

    wid = WidgetList([
        Button("Gradient(PINK, BLUE)", nop, (400, 80), RoundedRect((600, 100)), bg_color=Gradient(PINK, BLUE),
               anchor=TOP | LEFT | RIGHT),
        Button("Orange", nop, (5, 5), RoundedRect((162, 100)), ORANGE, ORANGE + (100,)),
        Button("MultiGradient", nop, (790, 250), RoundedRect((300, 480), border=2),
               MultiGradient(*RAINBOW[::-1]),
               WHITE + (100,),
               MultiGradient(*RAINBOW), anchor=RIGHT | TOP | BOTTOM)
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
