#!/usr/bin/env python3
# coding=utf-8

"""
Show the different possibilties of buttons.
"""


import pygame
from pygame.constants import *

from graphalama.buttons import Button, CarrouselSwitch
from graphalama.colors import Gradient, MultiGradient
from graphalama.constants import ORANGE, PINK, RIGHT, LEFT, TOP, BLUE, RAINBOW, BOTTOM, CENTER
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

    def nop(): ...

    wid = WidgetList([
        CarrouselSwitch(["Option 1", "A massive pizza", "Merry Christmas !"], lambda c: print(c), shape=RoundedRect(rounding=100), pos=(400, 250), anchor=CENTER),
        Button("Have fun", nop),
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
                if e.unicode == '>':
                    wid[0].arrow_color = (0, 165, 255)
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
