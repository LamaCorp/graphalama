from _dummy_thread import start_new_thread

from graphalama.colors import ImageBrush, Color, to_color
from graphalama.constants import CENTER, DEFAULT, LEFT, TRANSPARENT, WHITE, DATA_PATH, GREY, RIGHT
from graphalama.shadow import NoShadow
from graphalama.shapes import Rectangle
from .constants import ALLANCHOR
from .core import Widget, WidgetList
from .text import SimpleText
from .maths import Pos


class Button(Widget):
    ACCEPT_CLICKS = True

    def __init__(self, text, function, pos=None, shape=None, color=None, bg_color=None, border_color=None,
                 shadow=None, anchor=None):

        super().__init__(pos, shape, color, bg_color, border_color, shadow, anchor)

        self.text_widget = None  # type: SimpleText
        self.text = text
        self.function = function

        Widget.LAST_PLACED_WIDGET = self

    def __str__(self):
        return "<Button-{}>".format(self.text)

    @property
    def text(self):
        return self.text_widget.text

    @text.setter
    def text(self, value):

        assert isinstance(value, str), "Button.text is only for strings"

        if self.shape.auto_size:
            text = SimpleText(value, (0, 0), None, self.color, anchor=CENTER, shadow=NoShadow())
            new_size = Pos(self.shape.widget_size_from_content_size(text.size))
            text.pos = new_size / 2
            self.size = new_size
        else:
            size = self.shape.content_rect().size
            text = SimpleText(value, (size[0] / 2, size[1] / 2), size, self.color, anchor=ALLANCHOR)

        # we replace the previous text_widget by the new one
        if self.text_widget in self.children:
            self.children.remove(self.text_widget)
        self.text_widget = self.add_child(text)

    def on_mouse_enter(self, event):
        self.invalidate_bg()

    def on_mouse_button_down(self, event):
        self.invalidate_bg()
        self.invalidate_shadow()

    def on_click(self, event):
        start_new_thread(self.function, ())

    def on_mouse_button_up(self, event):
        self.invalidate_bg()
        self.invalidate_shadow()

    def on_mouse_exit(self, event):
        self.invalidate_bg()
        # case the user leaves the button while clicking, shadow wouldn't follow the offset
        self.invalidate_shadow()

    def pre_render_update(self):
        super(Button, self).pre_render_update()

        # we don't need to invalidate here as it's already invalidated when self.clicked changes
        self.shape.bg_offset = (1, 1) if self.clicked else (0, 0)
        self.bg_color.shade_intensity = 222 if self.clicked else 242 if self.mouse_over else None


class CheckBox(Widget):
    ACCEPT_CLICKS = True

    def __init__(self, text="", pos=DEFAULT, shape=DEFAULT, color=DEFAULT, bg_color=DEFAULT, border_color=DEFAULT,
                 shadow=DEFAULT, anchor=DEFAULT):

        if bg_color is DEFAULT:
            bg_color = TRANSPARENT
            shadow = NoShadow()

        box_size = (20, 20)
        self.box_widget = Button("", self.change_checked, (0, 0), Rectangle(box_size, 1, 0, box_size, box_size),
                                 border_color=color, anchor=LEFT)
        self.text_widget = SimpleText(text, (0, 0), color=color, shadow=NoShadow(), anchor=LEFT)

        super().__init__(pos, shape, color, bg_color, border_color, shadow, anchor)

        self.add_child(self.box_widget)
        self.add_child(self.text_widget)

        self.box_widget.pos = (self.box_widget.shadow.offset[0], self.shape.content_rect().height / 2)
        self.text_widget.pos = (self.box_widget.shadow_rect.width + 3, self.shape.content_rect().height / 2)

        self._checked = False
        self.checked = False

        Widget.LAST_PLACED_WIDGET = self

    def on_click(self, event):
        self.change_checked()

    @property
    def prefered_size(self):
        desired = (self.box_widget.shadow_rect.width + 3 + self.text_widget.shape.width,
                   max(self.box_widget.shadow_rect.height, self.text_widget.shape.height))
        return self.shape.widget_size_from_content_size(desired)

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value):
        assert isinstance(value, bool)

        if value != self.checked:
            self._checked = value

        if self.checked:
            self.box_widget.bg_color = ImageBrush(DATA_PATH + "tick.png", CENTER)
        else:
            self.box_widget.bg_color = Color(WHITE)

        self.box_widget.invalidate_bg()

    def change_checked(self):
        self.checked = not self.checked


class ImageButton(Button):

    def __init__(self, function, pos=None, shape=None, color=None, bg_color=None, border_color=None,
                 shadow=None, anchor=None):
        """A button with an image instead of a text. Set color to an ImageBrush for full control on image position and size."""

        super().__init__("", function, pos, shape, color, bg_color, border_color, shadow, anchor)

    def draw_content(self, content_surf):
        self.color.paint(content_surf)


class CarrouselSwitch(Button):

    def __init__(self, options, on_choice, pos=None, shape=None, color=None, bg_color=None, border_color=None,
                 arrow_color=None, shadow=None, anchor=None):
        """
        A widget to let the user choose between multiple options.

        This is a compact horizontal widget with arrows on each side to choose the option.
          Ex:   <-  OPTION 1  ->

        :param options: a list of string the user can choose from with the arrow
        :param on_choice: A function call every time the user chooses a new option, with an argument, the new option.
        :param arrow_color: set the color of the arrows
        """

        arrow_color = arrow_color if arrow_color is not None else GREY

        self.on_choice = on_choice
        self._options = []
        self._option_index = 0
        self._arrow_color = None

        # we set a nop function for the click as we don't utilise it
        super().__init__(options[0], lambda: 0, pos, shape, color, bg_color, border_color, shadow, anchor)

        cr = self.content_rect
        self.left_arrow = self.add_child(SimpleText("<", (0, cr.height / 2), color=arrow_color, anchor=LEFT))
        self.right_arrow = self.add_child(SimpleText(">", (cr.width, cr.height / 2), color=arrow_color, anchor=RIGHT))

        # Setting properties
        self.options = options
        self.option_index = 0
        self.arrow_color = arrow_color if arrow_color is not None else GREY



    @property
    def text(self):
        """Current selected option string"""
        return self.text_widget.text


    @text.setter
    def text(self, value):

        # in this case, the option list may no be a list of string, so we need to convert it
        s = str(value)

        # we set the position to the center of the content_rect
        size = Pos(self.shape.content_rect().size)
        text = SimpleText(s, size / 2, color=self.color, anchor=ALLANCHOR)

        # we replace the previous text_widget by the new one
        if self.text_widget in self.children:
            self.children.remove(self.text_widget)
        self.text_widget = self.add_child(text)

    @property
    def current_option(self):
        """Return the actually selected option text"""
        return self.options[self.option_index]

    @property
    def option_index(self):
        """The current selected option index in .options"""
        return self._option_index

    @option_index.setter
    def option_index(self, value):
        # we want to be able to loop through the indices so by just doing +=1
        self._option_index = value % len(self.options)
        # we use the text option of the button to display the current option
        self.text = self.current_option
        # and we call the user defined callback
        self.on_choice(self.current_option)

    def on_click(self, event):
        # we want that a click on the right side is the same as a click on the right arrow, so the user doesn't have to click exactly on the arrow
        if event.pos[0] > self.absolute_rect.centerx:
            self.option_index += 1
        else:
            self.option_index -=1

    @property
    def options(self):
        """The different options the user can go switch to with the arrows."""
        return self._options

    @options.setter
    def options(self, value):
        self._options = value
        self.option_index = 0
        self.invalidate_content()
        if self.shape.auto_size:
            self.size = self.prefered_size

    @property
    def prefered_size(self):
        if hasattr(self, "left_arrow"):
            # this is called the first time before left_arrow is created, in super().__init__()
            arrow_size = self.left_arrow.shape.width + self.right_arrow.shape.width
        else:
            # so we set a placeholer
            return super().prefered_size

        virtual_simple_text = SimpleText("")
        maxi = 0
        for option in self.options:
            # This is costless as text is not rendered until we need to
            virtual_simple_text.text = option
            maxi = max(maxi, virtual_simple_text.prefered_size[0])

        content_prefered_size = (arrow_size + maxi, self.text_widget.shape.height)
        return self.shape.widget_size_from_content_size(content_prefered_size)

    @property
    def arrow_color(self):
        """Get and set the color for both arrow"""
        return self.left_arrow.color

    @arrow_color.setter
    def arrow_color(self, value):
        self.left_arrow.color = value
        self.right_arrow.color = value
        self.invalidate_content()

