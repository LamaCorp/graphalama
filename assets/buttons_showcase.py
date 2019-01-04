#!/usr/bin/env python3
# coding=utf-8

"""
Show the different possibilties of buttons.
"""


from random import randint

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
         rot = randint(0, len(RAINBOW))
         carrousel.text_widget.color = MultiGradient(*RAINBOW[rot:], *RAINBOW[:rot])
    button = Button("Let's party!", set_text_color, (400, 250), bg_color=NICE_BLUE+(128,), anchor=CENTER)

    # We have to set the coice function after the button and carousel creation otherwise they'll be referenced before creation
    def on_choice(option):
        carrousel.arrow_color = colors[option]
        button.bg_color = colors[option]
    carrousel.on_choice = on_choice

    # creating a few checkbox
    checkboxes = WidgetList([CheckBox(f"CheckBox{i}") for i in range(1, 4)])

    wid = WidgetList([carrousel, button, checkboxes])

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return 0
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return 0
                if event.key == K_F4 and event.mod & KMOD_ALT:  # Alt+F4 --> quits
                    return event
            elif wid.update(event):
                continue
            if event.type == VIDEORESIZE:
                wid.resize(event.size, SCREEN_SIZE)
                SCREEN_SIZE = event.size
                screen = new_screen()

        screen.fill(WHITE)
        wid.render(screen)
        pygame.display.update()
        clock.tick(FPS)


if __name__ == '__main__':
    gui()
