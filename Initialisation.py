from DataModel import Bottle, Drink
from Enums import Paths, Liquid
from JsonHandler import JsonHandler

if __name__ == '__main__':
    json_handler = JsonHandler(Paths.BOTTLES.value, Paths.DRINKS.value)
    bottle_list = [Bottle(1, Liquid.RUM, 200), Bottle(2, Liquid.VODKA, 500),
                   Bottle(3, Liquid.TEQUILA, 375), Bottle(4, Liquid.VODKA, 1000),
                   Bottle(5, Liquid.TRIPLE_SEC, 750), Bottle(6, Liquid.ORANGE_JUICE, 1000)]
    json_handler.save_data(bottle_list)