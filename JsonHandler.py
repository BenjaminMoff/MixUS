import json
from DataModel import Bottle, Drink


class JsonHandler:
    def __init__(self, bottle_file_path, drink_file_path):
        self.bottle_file_path = bottle_file_path
        self.drink_file_path = drink_file_path

    def load_data_from_dict(self, dict, obj):
        obj.__dict__ = dict
        return obj

    def save_data(self, item_list):
        path = self.bottle_file_path if isinstance(item_list[0], Bottle) else self.drink_file_path

        serialized_list = []

        for item in item_list:
            serialized_list.append(item.__dict__)
        with open(path, 'w') as outfile:  # Clears the bottle file
            json.dump(serialized_list, outfile)

    def load_bottles(self):
        with open(self.bottle_file_path, 'r') as infile:
            encrypted_list = json.load(infile)

        bottles = []
        for encrypted_item in encrypted_list:
            bottles.append(self.load_data_from_dict(encrypted_item, Bottle()))
        return bottles

    def load_drinks(self):
        with open(self.drink_file_path, 'r') as infile:
            encrypted_list = json.load(infile)

        drinks = []
        for encrypted_item in encrypted_list:
            drinks.append(self.load_data_from_dict(encrypted_item, Drink()))
        return drinks


if __name__ == '__main__':
    bottle_list = [Bottle(1, "Rhum", 750), Bottle(2, "Vodka", 500),
                   Bottle(3, "Tequila", 375), Bottle(4, "Coke", 1000)]

    drink_list = [Drink({'Rhum': 100, 'Coke': 300}, "image1.png"),
                  Drink({'Vodka': 100, 'Orange Juice': 300}, "image2.png")]

    Json = JsonHandler("data_bottle.json", "data_drink.json")

    Json.save_data(bottle_list)
    bottle_list2 = Json.load_bottle()
    Json.save_data(drink_list)
    drink_list2 = Json.load_drink()

    pass
