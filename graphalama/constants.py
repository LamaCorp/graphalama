
DEFAULT = None

# Anchors

CENTER = NOANCHOR = 0
TOP = 1
LEFT = 2
TOPLEFT = TOP|LEFT
BOTTOM = 4
BOTTOMLEFT = BOTTOM|LEFT
RIGHT = 8
TOPRIGHT = TOP|RIGHT
BOTTOMRIGHT = BOTTOM|RIGHT
ALLANCHOR = TOP|RIGHT|BOTTOM|LEFT

# Colors

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (30, 144, 255)
TRUE_BLUE = (0, 0, 255)
PURPLE = (155, 89, 182)
RED = (255, 0, 0)
GREEN = (60, 179, 113)
DK_GREEN = (46, 139, 87)
ORANGE = (253, 151, 31)
GREY = (128, 128, 128)
LIGHT_GREY = (192, 192, 192)
PINK = (255, 51, 153)
FLASH_GREEN = (153, 255, 0)
NAVY = (0, 0,  128)
GOLD = (255, 214, 0)
WHITESMOKE = (245, 245, 245)
LLAMA = (255, 165, 0)
LIGHT_BLUE = (73, 209, 244)

TRANSPARENT = (255, 255, 255, 0)

# from https://flatuicolors.com/ :D
TURQUOISE = (26, 188, 156)
YELLOW = (241, 196, 15)
CONCRETE = (149, 165, 166)
PUMPKIN = (211, 84, 0)
NICE_BLUE = (52, 152, 219)
MIDNIGHT_BLUE = (44, 62, 80)

RAINBOW = (BLUE, GREEN, YELLOW, ORANGE, RED, PINK, PURPLE)


class Monokai:
    """Colors of the beautiful Monokai color theme. Acording to Sublime."""
    YELLOW = 230, 219, 116
    BLUE = 102, 217, 239
    PINK = 249, 38, 114
    PURPLE = 174, 129, 255
    BROWN = 117, 113, 94
    ORANGE = 253, 151, 31
    GREEN = 166, 226, 46
    BLACK = 39, 40, 34

COLORS = (
    BLACK, WHITE, GREY, LIGHT_GREY, CONCRETE, WHITESMOKE,
    BLUE, TRUE_BLUE, TURQUOISE, NICE_BLUE, MIDNIGHT_BLUE, NAVY,
    PURPLE,
    RED, PINK,
    GREEN, DK_GREEN, FLASH_GREEN,
    ORANGE, YELLOW, PUMPKIN, GOLD,
)

# Propagation
UP = 1
DOWN = 2

# Image resizing
FIT = 1
FILL = 2
STRETCH = 3
