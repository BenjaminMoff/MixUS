import json


class Bottle:
    def __init__(self, slot_number=None, liquid_type=None, volume_left=None):
        self.__slot_number = slot_number
        self.__liquid_type = liquid_type
        self.__volume_left = volume_left

    # Method that load the object's attributes from a dictionnary
    def load_data_from_dict(self, dict):
        self.__dict__ = dict
        return self

    # Method that keeps tracks of the remaining liquid in the bottle when poured
    def pour(self, qty):
        if  self.volume_left - qty <= 0:
            return -1
        else:
            self.volume_left -= qty

    # Bunch of methods that sets and gets the attributes of Bottle
    def set_liquid_type(self, type):
        self.__liquid_type = type

    def get_liquid_type(self):
        return self.__liquid_type

    def set_volume_left(self, vol_left):
        self.__volume_left = vol_left

    def get_volume_left(self):
        return self.__volume_left

    def set_slot_number(self, n):
        self.__slot_number = n

    def get_slot_number(self):
        return self.__slot_number

class Drink:
    def __init__(self, ingredients_dict=None, image_path=None):
        self.ingredients = ingredients_dict  # self.ingredients is a dictionnary of ingredient:Volume tuples
        self.image_path = image_path         # Path to the image for diplay use

    # Method that determines what drinks are available depending on current bottles
    def is_available(self, bottles):
        pass

    # Method called when the drink going to be made
    def make(self, bottles):
        pass

