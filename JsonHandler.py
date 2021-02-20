import json
from DataModel import *
from Enums import *


class JsonHandler:
    def __init__(self, bottle_file_path, drink_file_path):
        self.bottle_file_path = bottle_file_path
        self.drink_file_path = drink_file_path

    def load_data_from_dict(self, d, obj):
        obj.__dict__ = d
        return obj

    def save_data(self, item_list):
        path = self.bottle_file_path if isinstance(item_list[0], Bottle) else self.drink_file_path

        serialized_list = []

        for item in item_list:
            serialized_list.append(item.__dict__)
        with open(path, 'w') as outfile:  # Clears the bottle file
            json.dump(serialized_list, outfile, cls=LiquidEncoder)

    def load_bottles(self):
        with open(self.bottle_file_path, 'r') as infile:
            encrypted_list = json.load(infile, object_hook=as_enum)

        bottles = []
        for encrypted_item in encrypted_list:
            bottles.append(self.load_data_from_dict(encrypted_item, Bottle()))
        return bottles

    def load_drinks(self):
        with open(self.drink_file_path, 'r') as infile:
            encrypted_list = json.load(infile, object_hook=as_enum)

        drinks = []
        for encrypted_item in encrypted_list:
            drinks.append(self.load_data_from_dict(encrypted_item, Drink()))
        return drinks


class LiquidEncoder(json.JSONEncoder):
    def default(self, obj):
        if type(obj) is Liquid:
            return {"__enum__": str(obj)}
        return json.JSONEncoder.default(self, obj)


def as_enum(d):
    if "__enum__" in d:
        name, member = d["__enum__"].split(".")
        return getattr(Liquid[member], member)
    else:
        return d


if __name__ == '__main__':
    bottle_list = [Bottle(1, Liquid.RUM, 25), Bottle(2, Liquid.VODKA, 16),
                   Bottle(3, Liquid.TEQUILA, 12), Bottle(4, Liquid.COKE, 32)]

    drink_list = [Drink("Rhum_and_coke", {Liquid.RUM.string_name: 3, Liquid.COKE.string_name: 9}, "test"),
                  Drink("Vodka_jus_canneberge", {Liquid.VODKA.string_name: 3, Liquid.CRANBERRY_JUICE.string_name: 9},
                        "test")]

    Json = JsonHandler(Paths.BOTTLES.value, Paths.DRINKS.value)
    Json.save_data(bottle_list)
    bottle_list2 = Json.load_bottles()
    Json.save_data(drink_list)
    drink_list2 = Json.load_drinks()
    #print(drink_list2[0].is_available(bottle_list2))
    #print(drink_list2[1].is_available(bottle_list2))

    butt_manager = BottleManager(Json)
    drink_manager = DrinkManager(Json, butt_manager)
    print(drink_manager.get_available_drinks())
    pass
