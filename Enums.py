from enum import Enum
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

    # Liquors
    RUM = "Rum", True, False
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
        return list(map(lambda c: c.value, BottleSize))


class Paths(Enum):
    BOTTLES = os.path.join(os.path.dirname(__file__),
                           "persistance/bottles.json")
    DRINKS = os.path.join(os.path.dirname(__file__),
                          "persistance/drinks.json")
