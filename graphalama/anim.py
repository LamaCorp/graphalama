from time import time


class Anim:
    """
    Base class for all animations.

    To create your own animation, you need to override function(self, widget)
    `function` is the action performed every time the animation runs.
    """

    def __init__(self, duration=1, steps=255, loop=False):
        self.__duration = duration
        self.__max_steps = steps
        self.__first_run = time()

        self.__loop = loop
        self.__reversed = False

        self.finished = False
        self.step = 0
        """Current step of the animation. Ranges from 0 to self.__max_steps"""

    def function(self, widget):
        """Override this function to provide the animation."""

    def run(self, widget):
        """Performs one frame of the animation, if the time has come."""

        now = time()

        if now > self.__first_run + self.__duration:
            self.finished = True

        if self.finished:
            self._on_finish(widget)
            return

        time_elapsed = now - self.__first_run
        interval = self.__duration / self.__max_steps
        step = time_elapsed // interval

        if not self.__reversed:

            if step > self.step:
                self.step = step
                self.function(widget)

        else:
            step = self.__max_steps - step
            if step < self.step:  # when reversed whe want the step to decrease
                self.step = step
                self.function(widget)

    def _on_finish(self, widget):
        """Cleanly end the animation, or loops if looping enabled."""
        if self.__loop:
            self.__reversed = not self.__reversed
            self.finished = False
            self.__first_run = time()
        else:
            self.step = self.__max_steps
            self.function(widget)
            self.finished = True

    def stop(self):
        """Stop the inimation."""
        self.__loop = False
        self.finished = True


class FadeAnim(Anim):
    """Smoothly change the trasparency of a widget."""

    def __init__(self, duration, fade_start=255, fade_end=0, loop=False):
        assert 0 <= fade_start <= 255
        assert 0 <= fade_start <= 255

        super().__init__(duration, abs(fade_start - fade_end), loop)
        self.fade_start = fade_start
        self.fade_end = fade_end

    def function(self, widget):
        if self.fade_start > self.fade_end:
            fade = self.fade_start - self.step + self.fade_end
        else:
            fade = self.fade_start + self.step

        widget.transparency = fade
