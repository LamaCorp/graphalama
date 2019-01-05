import pygame
from graphalama.widgets import WidgetList


class App:
    """
    A state machine that represents and manages the different screens of the app

    App is usefull for more complex applications, with different screens (ie. an app that has a menu a
    settings page and a game)
    Every part of in the app would be a Screen (so there should be one for Menu, one for Settings etc...)
    And one can easily set wich screen is actually displayed with `set_screen(SCREEN_ID)`.
    Screens are identified with their ID. A screen ID is any constant, that is a key in the `screens` dict.

    Note that one need to always pass Screen classes or function that return screen. This is for lazyness
    purposes, so there isn't a bunch of screen an widget instancited that dont exist on the screen.

    Therefore one should define every screen in that dictionary. However, for temporary screens, or secondary
    screens, one can set them with `set_temp_screen(Screen)`, effectively creating an unnamed screen.

    To properly exit an app, call App.quit().
    """

    def __init__(self, screens: dict, initial_screen, display_size=None):
        """
        A state machine that represents and manages the different screens of the app

        :param screens: a dictionary of Screen classes indexed by their ID.
        :param initial_screen: the ID of the first screen.
        """

        # evaluating defaults
        if display_size is None:
            # default s the bigger we can
            display_size = pygame.display.set_mode(pygame.display.list_modes()[0])

        self.screens = screens
        self.screen = initial_screen
        self.display = display_size
        self.clock = pygame.time.Clock()
        self.running = False

        self.current_screen = self.screens[self.screen](self)

    def quit(self):
        """Kill the app"""
        self.running = False

    def run(self):
        """The main loop of the app"""

        if self.running:
            raise RuntimeError("Tou try to run an already running app")

        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.current_screen.update(event)

            self.current_screen.internal_logic()

            rects = self.current_screen.render(self.display)

            # The screen may have implemented smart updating
            if rects is not None:
                pygame.display.update(rects)
            else:
                pygame.display.flip()

            self.clock.tick(self.current_screen.FPS)

    def set_screen(self, new_screen_id):
        """
        Change the visible screen of the app.

        :param new_screen_id: A key of the screens dictionary
        """

        self.screen = new_screen_id
        # We instantiate the screen class
        self.current_screen = self.screens[self.screen](self)

    def set_temp_screen(self, screen):
        """
        Set the App to an unnamed screen.

        :param screen: A Screen class/callable. The benefts of this function is that it allow for easily adding runtime screens that are used only once
        """

        self.screen = None
        self.current_screen = screen(self)


class Screen:
    """
    Represent a Screen of an App.

    To implement a new screen, you need to override `draw_background`, `internal_logic`,
    and pass a list of widgets to the constructor, and everything else is taken care of.
    To change screen, call `self.app.set_screen(SCREEN_ID)`
    """

    FPS = 60

    def __init__(self, app, widgets=()):
        self.app = app
        self.widgets = WidgetList(widgets)

    def __call__(self, app):
        # This way we can pass already build screens to a achine without errors
        self.app = app
        return self

    def draw_background(self, display):
        display.fill((255, 255, 255))

    def update(self, event):
        self.widgets.update(event)

    def internal_logic(self):
        """Override it if your screen has stuff to run once a frame, before rendering"""

    def render(self, display):
        self.draw_background(display)
        self.widgets.render(display)
