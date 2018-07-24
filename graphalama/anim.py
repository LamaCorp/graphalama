from time import time

from graphalama.maths import Pos


# noinspection PyPep8
class Timing:
    """
    This class defines a few timing functions used for animations.

    A timing function goes from [0, 1] to [0, 1] and describe the progress of an animation.
    """

    linear = lambda x: x
    slow_in = lambda x: x ** 2
    slow_out = lambda x: 1 - (1 - x) ** 2
    slow_in_and_out = lambda x: x ** 2 * (3 - 2 * x)
    slow_middle = lambda x: 2 * x - x ** 2 * (3 - 2 * x)


class Anim:
    """
    Base class for all animations.

    To create your own animation, you need to override function(self, widget)
    `function` is the action performed every time the animation runs.
    """

    def __init__(self, duration=1, steps=255, iterations=1, timing_function=Timing.slow_in_and_out):
        self.__duration = duration
        self.__max_steps = steps
        self.__first_run = time()
        self.__timing_function = timing_function

        self.__iterations = iterations
        self.__reversed = False

        self.running = False
        self.step = 0
        """Current step of the animation. Ranges from 0 to self.__max_steps"""

    def function(self, widget):
        """Override this function to provide the animation."""

    @property
    def progress(self):
        return self.step / self.__max_steps

    @property
    def step(self):
        return round(self.__timing_function(self._step / self.__max_steps) * self.__max_steps)

    @step.setter
    def step(self, value):
        self._step = value

    def run(self, widget):
        """Performs one frame of the animation, if the time has come."""

        now = time()

        if now > self.__first_run + self.__duration:
            self.running = False
            if self.__reversed:
                self.step = 0
            else:
                self.step = self.__max_steps

        if not self.running:
            self._on_finish(widget)
            return

        time_elapsed = now - self.__first_run
        interval = self.__duration / self.__max_steps
        step = time_elapsed // interval

        if not self.__reversed:

            if step > self._step:
                self._step = step
                self.function(widget)

        else:
            step = self.__max_steps - step
            if step < self._step:  # when reversed whe want the step to decrease
                self._step = step
                self.function(widget)

    def _on_finish(self, widget):
        """Cleanly end the animation, or loops if looping enabled."""

        if self.__iterations in (0, 1):  # that's  the end
            self.function(widget)
            self.stop()

        else:
            self.__iterations -= 1
            self.__reversed = not self.__reversed
            self.start()

    def start(self):
        self.running = True
        self.__first_run = time()

    def stop(self):
        """Stop the inimation."""
        self.running = False


class FadeAnim(Anim):
    """Smoothly change the trasparency of a widget."""

    def __init__(self, duration, fade_start=255, fade_end=0, iterations=False, timing_function=Timing.slow_in_and_out):
        assert 0 <= fade_start <= 255
        assert 0 <= fade_start <= 255

        super().__init__(duration, abs(fade_start - fade_end), iterations, timing_function)
        self.fade_start = fade_start
        self.fade_end = fade_end

    def function(self, widget):
        if self.fade_start > self.fade_end:
            fade = self.fade_start - self.step + self.fade_end
        else:
            fade = self.fade_start + self.step

        widget.transparency = fade


class MoveAnim(Anim):
    """Smoothly moves a widget from a place to another."""

    def __init__(self, duration, offset, iterations=False, timing_function=Timing.slow_in_and_out):
        super().__init__(duration, max(map(abs, offset)), iterations, timing_function)
        self.offset = Pos(offset)
        self.start_pos = None

    def function(self, widget):
        if self.start_pos is None:
            self.start_pos = widget.pos

        widget.pos = self.start_pos + self.offset * self.progress
