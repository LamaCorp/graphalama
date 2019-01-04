#!/usr/bin/env python3
# coding=utf-8

"""
Show the different possibilties of buttons.
"""


from random import shuffle

import pygame
from pygame.constants import *

from graphalama.widgets import Button, CarrouselSwitch, CheckBox
from graphalama.colors import Gradient, MultiGradient
from graphalama.constants import ORANGE, PINK, RIGHT, LEFT, TOP, BLUE, RAINBOW, BOTTOM, CENTER, NICE_BLUE, RAINBOW, LLAMA
from graphalama.core import WidgetList
from graphalama.shapes import RoundedRect


WHITE = (255, 255, 255)
pygame.init()
# noinspection PyArgumentList
pygame.key.set_repeat(300, 40)

SCREEN_SIZE = 800, 500
FPS = 60


def new_screen():
    return pygame.display.set_mode(SCREEN_SIZE)


def gui():
    global SCREEN_SIZE

    screen = new_screen()
    pygame.display.set_caption('Buttons showcase')
    clock = pygame.time.Clock()

    def nop(*args): ...

    colors = {
        "Llama": LLAMA,
        "Blue": NICE_BLUE,
        "Pink": PINK,
    }

    # Creating a CarrouselSwitch to change the colors of the button + its own arrow. We need to set the function after creation, see below
    carrousel = CarrouselSwitch(list(colors.keys()), nop,
                                (400, 180), RoundedRect(rounding=100),
                                bg_color=(240, 240, 240, 240), arrow_spacing=30, anchor=CENTER)

    # Create a button to change the carrousel color
    def set_text_color():
        rainbow = list(RAINBOW)
        shuffle(rainbow)
        carrousel.text_widget.color = MultiGradient(*rainbow)
    button = Button("Let's party!", set_text_color, (400, 250), RoundedRect(padding=5), bg_color=NICE_BLUE+(128,), anchor=CENTER)

    # We have to set the coice function after the button and carousel creation otherwise they'll be referenced before creation
    def on_choice(option):
        carrousel.arrow_color = colors[option]
        button.bg_color = colors[option]
    carrousel.on_choice = on_choice

    # creating a few checkbox
    checkboxes = WidgetList([CheckBox(f"CheckBox{i}") for i in range(1, 5)])

    wid = WidgetList([carrousel, button, checkboxes])



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
