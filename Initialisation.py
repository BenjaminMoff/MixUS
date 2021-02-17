from DataModel import Bottle, Drink
from Enums import Paths
from JsonHandler import JsonHandler

if __name__ == '__main__':
    json_handler = JsonHandler(Paths.BOTTLES.value, Paths.DRINKS.value)
    bottle_list = [Bottle(1, "Rum", 750), Bottle(2, "Vodka", 500),
                   Bottle(3, "Tequila", 375), Bottle(4, "Coke", 1000),
                   Bottle(5, "Triple sec", 750), Bottle(6, "Jus d'orange", 1000)]
    json_handler.save_data(bottle_list)