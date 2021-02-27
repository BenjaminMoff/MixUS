from enum import Enum
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
import os


class Liquid(Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 2
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, string_name, is_alcoholized, is_filler):
        super().__init__()
        self.string_name = string_name
        self.is_alcoholized = is_alcoholized
        self.is_filler = is_filler

    # Used to describe an empty slot
    NONE = "Aucun", False, False

    # Liquors
    RUM = "Rhum", True, False
    VODKA = "Vodka", True, False
    TEQUILA = "Tequila", True, False
    GIN = "Gin", True, False

    # Mixers
    TRIPLE_SEC = "Triple sec", True, False
    LIMONCELLO = "Limoncello", True, False

    # Alcohol-free
    ORANGE_JUICE = "Jus d'orange", False, True
    CRANBERRY_JUICE = "Jus de canneberge", False, True
    COKE = "Coke", False, True
    SPRITE = "Sprite", False, True

    @staticmethod
    def list():
        return list(map(lambda c: c.string_name, Liquid))

    @staticmethod
    def get_liquid_from_string_name(string_name):
        for liquid in Liquid:
            if liquid.string_name == string_name:
                return Liquid[liquid.name]
        raise ValueError("No Liquid contains this string_name: " + string_name)


class BottleSize(Enum):
    ML_500 = 500
    ML_750 = 750
    ML_1000 = 1000
    ML_1140 = 1140

    @staticmethod
    def list():
        return list(map(lambda c: str(c.value), BottleSize))


# Paths to persistence files
class Paths(Enum):
    BOTTLES = os.path.join(os.path.dirname(__file__),
                           "persistence/bottles.json")
    DRINKS = os.path.join(os.path.dirname(__file__),
                          "persistence/drinks.json")
    MAIN_MENU = os.path.join(os.path.dirname(__file__),
                             "ui/MainMenu.ui")
    BOTTLE_MENU = os.path.join(os.path.dirname(__file__),
                               "ui/BottleMenu.ui")
    DRINK_OPTION_MENU = os.path.join(os.path.dirname(__file__),
                                     "ui/DrinkOptionMenu.ui")
    MAINTENANCE_MENU = os.path.join(os.path.dirname(__file__),
                                    "ui/MaintenanceMenu.ui")
    MIXING_MENU = os.path.join(os.path.dirname(__file__),
                               "ui/MixingMenu.ui")


class GUI(Enum):
    window_background_color = "background-color: rgb(0, 167, 89);"
    button_color = "background-color: rgb(255, 255, 255);"
    layout_contour_color = "border: 1px solid;" \
                           "border-color: rgb(0, 0, 0);"
    layout_background_color = "background-color: rgb(0, 0, 0);"

    drink_image_size = QSize(200, 350)
