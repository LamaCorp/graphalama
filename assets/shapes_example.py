"""
Show the different shape possibilties on buttons.
"""

# coding=utf-8

from math import sin, cos

import pygame
from pygame.constants import *

from graphalama.buttons import Button
from graphalama.constants import GREEN
from graphalama.core import WidgetList
from graphalama.shapes import RoundedRect, Circle, PolarCurve

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

    def play():
        ...

    wid = WidgetList([
        Button("Play", play, bg_color=GREEN),
        Button("Rounded", play, shape=RoundedRect(), bg_color=GREEN),
        Button("Very round", play, shape=RoundedRect(rounding=100), bg_color=GREEN),
        Button("Big", play, shape=RoundedRect((182, 100)), bg_color=GREEN),
        Button("Circle", play, shape=Circle(), bg_color=GREEN),
        Button("Polar", play, shape=PolarCurve((200, 200),
                                               lambda t: 16 * sin(t) ** 3,
                                               lambda t: -13 * cos(t) + 6 * cos(2 * t) + 2 * cos(
                                                   3 * t) + cos(4 * t)), bg_color=GREEN),
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
