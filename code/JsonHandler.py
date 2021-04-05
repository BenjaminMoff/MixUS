import json
from DataModel import *
from Enums import *


class JsonHandler:
    """
    Class responsible to __read and write in the json persistence files
    """
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
        with open(path, 'w') as outfile:
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
    """
    Class that overrides the default JSONEncoder to allow encoding of Liquid enum class
    """
    def default(self, obj):
        return {"__enum__": str(obj)}

        # TODO : Fix if statement below
        # if type(obj) is Liquid:
        #     return {"__enum__": str(obj)}
        # return json.JSONEncoder.default(self, obj)


def as_enum(d):
    """
    Method used as hook when reading json files to decode Liquid enum class
    """
    if "__enum__" in d:
        name, member = d["__enum__"].split(".")
        return getattr(Liquid[member], member)
    else:
        return d
