# Graphalama

## Aim

Pygame is a great and simple way to create basic windowed applications.
It is therfore a privilieged entry point for python learners to get out of the console.
However, people often ask for GUI features in pygame: _"How can I have a simple button ?"_ or _"How can the user enter their name ?"_.

The goal of this librairy is to answer all those questions and provide the easiest possible interface to create, update, control and manipulate what we will call widgets. (Buttons, TextBoxes, Sliders, Switches...)

### Our principles

- KISS: Keep it sweet and simple
- Simple and ugly are not synonyms
- Simple can be powerfull
- Simple should be customisable
- No code is better than ugly code

## Installation

You can install a stable version using pip
```
pip install graphalama
```
Or a developper version with
```
git clone https://gitlab.com/lama-corp/graphalama
cd graphalama
python setup.py install -U
```

## How to use

Most simple pygame applications look like this

```python
import pygame
pygame.init()

# Setup of variables, objects...
stop = False
screen = pygame.display.get((400, 400))

# Main loop
while not stop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop = True
        else:
            # Handle inputs, if the user click on some clickable places, buttons...
            # Handle the keys pressed to move players, input text...
            # It's the logic of the game that depends of inputs
            ...

    # Then you have an internal logic, applying gravity, running AIs, anything that changes itself every frame

    # And finally you render everything with some more or less advanced technics

    screen.fill((255, 255, 255))
	pygame.display.update()
```

For any widget you need to have at least 3 parts in the code to implement it: creation, handling the input, and rendering it. Some widget can have an internal logic going like clock or timer but we'll come back on that later.

Say you want to add a button in your window. A big green play button. We reduce each step to the minimun.

- Creation :
      `play_button = Button("PLAY", bg_color=GREEN, function=play)`
- Input handling (clicks):
        `play_button.update(event)`
- Rendering: `play_button.render(screen)`

A minimal hello world would look like this:
```python
import pygame
from graphalama.widgets import *

pygame.init()

screen = pygame.display.set_mode((800, 500))

# creation
hello_text = SimpleText("Hello World!")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        # a text doesn't change on input so we don't need to update it

    screen.fill((255, 255, 255))
    hello_text.render(screen)
    pygame.display.flip()
```

## Customisation

Before knowing how to cutomise your widgets so they match your style, we have to understand what *is* a widget.
A widget is made of three things:
 - a **Shadow**: optional, it provides a nice depth to our application and accentuate our widgets
 - a **Shape**: defines the shape of the background. It also defines the borders, the size and where you can click/select the widget. To list a few common: Rectangle, Circle, RoundedRect...
 - a **content**: the information of the widget, it can be the widget's own content or a child widget (did you know that we can put any widget inside a Button ?)

Those three layers are mixed together to create the widget. To customise our widgets we can therefore easily change one of those three layers.

### Common parameters

First, let's have a look to the common parameters that aren't part of the shadow, shape or content.

#### Position

With graphalama, as with pygame a position is a couple of integers, (0, 0) being the topleft corner and `(x, y)` being the `x`-st pixel on the `y`-st line of the screen.
Every time we'll need a position as an argument for a function it will be a tuple `(x, y)` of integers.

Graphalama has a powerfull positioning system for the widgets, whose goal is to be able to design resizable applications witout more effort.
A widget's position is defined by two elements: its coordinates `pos` and its `anchor`. The `anchor` defines where the widget is anchored,
that is, where it will stay when the window is resized and where it will be first put on the screen.

For instance, if the anchor ia `TOPLEFT`, the widget will always stay at the same distance of the top and the left of the screen, no matter how the window is resized.
Its `pos` will then be the topleft corner of the widget. This is the default anchor, so we can place our widgets like we would do in most frameworks.

But say, we want a widget to always stay on the right side of the screen (like a "next" button), we just need to set the anchor to `RIGHT`
and our widget will stay at say 5 pixels from the right border even if we resize the window. Here `pos` will be the middle point on the right
of the widget. Here's a small drawing to explain it:

![](assets/right_anchor.png)

This button was created in a 800x500 window with

```python
Button("Next ->", quit, (770, 250), RoundedRect((200, 100)), bg_color=GREEN, anchor=RIGHT)
```

If we resize the window, it will always stay 30px from the right edge.

Two conclude, there are four things to remember:
 - We can anchor a widget to one or more side of the window by setting the anchor to `RIGHT`, `LEFT`, `TOP` and `BOTTOM`.
 Those constants are defined in `graphalama.constants`.
 - We can combine the anchors with the pipe symbol, `|`, so we anchor a widget to the top right corner with `anchor=TOP|RIGHT`
 - Not only the position, but also the size can be controled with anchors. If `anchor=LEFT|RIGHT`, the distance from the widget
 to both side wil stay constant. Therefore the width will stretch if the window gets bigger and shrink if the window gets smaller.
 - The `pos` of a widget always reflect the anchor: if the anchor is `BOTTOM|RIGHT` the `pos` will be teh bottom right of the widget.
 If it is `LEFT`, `pos` will be the midleft of the widget. However we can always get the topleft of the widget with `widget.topleft`.
 `widget.x` and `widget.y` also work.

 That's everything for a very technical part, but it gets very intuitive once we get used to it and saves a lot of time.

#### Color

Graphalama has a great range of options for coloring widgets. No more of the common monochromatic widgets without transparency!

Usually widgets have three colors:
 - `color`, the foreground color, ie. the text of a button
 - `bg_color`, the background color, that's how the shape is filled
 - `border_color`, the color of the border

Those three colors accepts different types, and you can pass any of them at any time:
 - a RGB or RGBA tuple of integers between 0 and 255, you can find a lot of pre-defined colors in `graphalama.constants`
 - a `Gradient` from one color to another (both can be RGB or RGBA)
 - a `MultiGradient` to have a multicolored gradient
 - a `ImageBrush` to draw an image
 - a `ImageListBrush` to draw multiple images and swap between them.

![Example of differents colors and transparency](assets/color_example.PNG)
You can get the code for this example [here](assets/color_example.py).

What actually is a color ?
It is an object with a `paint` method that takes a `Surface` and colorize it.

##### RGB or RGBA tuples
Tuples like `(R, G, B)` or `(R, G, B, A)` are both valid colors, with `0 <= R, G, B, A <= 255`.
They are automatically converted to a `Color` object for ease of use. And as expected, they fill the whole area with the same color.

##### Gradients
A `Gradient(start, end, horizontal)` will fill a shape with a linear interpolation between the two colors.
`start` and `end` must be two tuples and if `horizontal == False`, the gradient will be drawn verticall,
so `start` will be at the top of the shape and `end` at the bottom.

##### Multigradients
    ):
A `Multigradient(*colors, positions=None, horizontal=True)` is like a `Gradient` but with more than two colors.

Example for an equaly spaced blue-yellow-orange-red gradient:
```
from graphalama.constants import BLUE, YELLOW, ORANGE, RED
MultiGradient(BLUE, YELLOW, ORANGE, RED)
```

You can also choose where the color points are. Here the orange-red part
will take the left half of the gradient whereas the blue-yellow and yellow-orange
would take only a fourth. The positions are between 0 and
```
MultiGradient(BLUE, YELLOW, ORANGE, RED, positions=(0, 1/4, 1/2, 1))
```
Of course, the number of positions must match the number of colors, but the positions do nat have to start at 0 and
end at 1. For instance is the positions are `(1/2, 2/3, 1)`, the first half of the surface will be exactly of the first color.

If `horizontal == False`, then the gradient is drawn top to bottom and not left to right.


### Custom Shape

Let's start again with our play button: `Button("PLAY", bg_color=GREEN, function=play)`.
The default shape is a `Rectangle`,  So that's what it would look like:
![](assets/shape_simplest.PNG)

But you're not limited to rectangles, you can have a rounded rectangle, a circle
or even any parametric shape or any custom shape (we'll come back on creating your custom shapes later)

![](assets/shapes_examples.PNG)

You can get the code for this example [here](assets/shapes_example.py).


There are quite a few things to note here.
First of all, if we don't precise the position of the widgets, the will just stack verticaly n the center of the screen.
Then, we can give any shape to a widget. Every widget can have any shape, we just need to pass it as the `shape` argument in the object initalisation.
Shapes are found in `graphalama.shapes`, they all accept the same parameters :
 - First the `size` of the widget, if none is given the widget will just fit its content
 - Then the argments for the specific shape, ie. the rounding of the rectangle, the equations of the parametric curve...
 - The `border` comes next, which specifies the width of the widget's border
 - Finally comes `min_size` and `max_size`, those are the minimum and maximum size the widget can take if the window is resized

 Finally, a shape object is a container for all the information about the size, border, shape.
 If we want to change the size of a widget at runtime, we need to set ` widget.shape.size`, `widget.shape.height` or `widget.shape.width`.

 > Therefore a shape can be set only to ONE widget. Widgets can not share references to the same shape.

### Custom content

There's gonna be some heavy work there, so I wont comment on the current system.

### Custom shadow

Shadows put a highight on our widgets, by creating a deeper contrast between the widget and the background.
Shadows are fond in `graphalama.shadows` and they are optional: you can pass `NoShadow` to any widget and...
it won't show nor calculate any shadow. Otherwise, a shadow accepts 4 optional arguments. Here's the signature

 ```python
Shadow(dx=2, dy=2, blur=2, strength=100)
```

The two firsts are the offset between the widget and the shadow,
they shift the shadow by `dx` and `dy` to the right and down respectively.

Optionnaly, you can blur the shadow, for a smoother result.
If blur is 0 the shadow will have the same shape as the widget with the same sharp borders.
If blur is positive, then a gaussian blur si applied to the shape. Note that this requires pillow.
If you don't have pillow installed, it won't blur the shadow, without raising any exception.

The strength is an integer between `0` and `255`, it's how dark the shadow is.

Here's an example from [shapes_example](assets/shapes_example.py), where the widgets are

```python
wid = WidgetList([
    Button("Random Shadow", change_shadow, (400, 250), RoundedRect((400, 250), 50, 1, 2),
           bg_color=(150, 232, 230), border_color=NICE_BLUE, shadow=NoShadow(), anchor=ALLANCHOR),
    Widget((55, 35),  RoundedRect(), bg_color=Monokai.PINK, anchor=TOP),
    Widget((150, 35), RoundedRect(), bg_color=Monokai.BLUE,   shadow=Shadow(5, 5, 0), anchor=TOP),
    Widget((245, 35), RoundedRect(), bg_color=Monokai.ORANGE, shadow=Shadow(-5, 5, 10, 200), anchor=TOP),
    Widget((340, 35), RoundedRect(), bg_color=Monokai.GREEN,  shadow=Shadow(5, 5, 5), anchor=TOP),
    Widget((435, 35), RoundedRect(), bg_color=Monokai.YELLOW, shadow=Shadow(0, 0, 10), anchor=TOP),
    Widget((530, 35), RoundedRect(), bg_color=Monokai.PURPLE, shadow=Shadow(5, 5, 0, 200), anchor=TOP),
    Widget((625, 35), RoundedRect(), bg_color=Monokai.BROWN,  shadow=Shadow(-2, -2, 5), anchor=TOP),
    Widget((720, 35), RoundedRect(), bg_color=Monokai.BLACK,  shadow=Shadow(5, 20, 5), anchor=TOP),
    SimpleText("Shadow(dx, dy, blur, strength)", (400, 490), anchor=BOTTOM)
    ])
```

![](assets/shadow_example.PNG)

## Other elements

### Animations

### Drawings

### Font

There's gonna be some heavy work there, so I wont comment on the current system.

## Widgets

### Button

### SimpleText

## Tips

### The `Pos` class

## Creating your own stuff

### Widgets

###


