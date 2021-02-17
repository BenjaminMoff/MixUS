from enum import Enum


class Liquid(Enum):
    # Liquors
    RUM = "Rum"
    VODKA = "Vodka"
    TEQUILA = "Tequila"
    GIN = "Gin"

    # Mixers
    TRIPLE_SEC = "Triple sec"
    LIMONCELLO = "Limoncello"

    # Alcohol-free
    ORANGE_JUICE = "Jus d'orange"
    CRANBERRY_JUICE = "Jus de canneberge"
    COKE = "Coke"
    SPRITE = "Sprite"

    @staticmethod
    def list():
        return list(map(lambda c: c.value, Liquid))


class BottleSize(Enum):
    ML_500 = 500
    ML_750 = 750
    ML_1000 = 1000
    ML_1140 = 1140

    @staticmethod
    def list():
        return list(map(lambda c: c.value, BottleSize))