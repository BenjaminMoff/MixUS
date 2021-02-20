from Enums import Liquid


class Bottle:
    def __init__(self, slot_number=None, liquid=None, volume_left=None):
        self.__slot_number = slot_number
        self.__liquid = liquid
        self.__volume_left = volume_left  # In ounces

    # Method that keeps tracks of the remaining liquid in the bottle when poured
    def pour(self, ounces=1):
        if self.__volume_left - ounces <= 0:
            return -1
        else:
            self.__volume_left -= ounces

    # Bunch of methods that sets and gets the attributes of Bottle
    def set_liquid_type(self, liquid):
        self.__liquid = liquid

    def get_liquid_type(self):
        return self.__liquid.string_name

    def set_volume_left(self, vol_left):
        self.__volume_left = vol_left

    def get_volume_left(self):
        return self.__volume_left

    def set_slot_number(self, slot_number):
        self.__slot_number = slot_number

    def get_slot_number(self):
        return self.__slot_number

    def is_alcoholized(self):
        return self.__liquid.is_alcoholized

    def is_filler(self):
        return self.__liquid.is_filler


class Drink:
    def __init__(self, name=None, ingredients_dict=None, image_path=None):
        self.name = name
        self.ingredients = ingredients_dict  # self.ingredients is a dictionnary of Liquid.string_name:Volume tuples
        self.image_path = image_path  # Path to the image for diplay use
        # self.double = False
        # self.virgin = False
        # self.liquids = list(self.ingredients) if self.ingredients is not None else []  # List of the Liquids
        self.liquids = []
        if self.ingredients is not None:
            for ingredient in list(self.ingredients):
                self.liquids.append(Liquid.get_liquid_from_string_name(ingredient))

    # Method that determines what drinks are available depending on current bottles
    def is_available(self, bottles):
        counter = 0
        for liquid in self.liquids:
            for bottle in bottles:
                # If the remaining volume in the bottle is enough to make the drink, then the counter increases
                if bottle.get_liquid_type() == liquid.string_name and bottle._Bottle__volume_left >= self.ingredients. \
                        get(liquid.string_name):
                    counter += 1
                    break
        # If the counter is equal to the number of ingredients, then the drink is available for the user
        if counter == len(self.ingredients):
            return True
        else:
            return False

    # Method that determines if the bottles have enough to make a double of this drink (double the alcohol)
    def enough_for_double(self, bottles):
        counter = 0
        alcoholized_liquids = self.__find_alcoholized()
        # Check for each alcoholized liquid if the volume left in the bottles is enough to make a double
        for alcoholized_liquid in alcoholized_liquids:
            for bottle in bottles:
                if bottle.get_liquid_type() == alcoholized_liquid.string_name and bottle.get_volume_left >= \
                        self.ingredients.get(alcoholized_liquid) * 2:
                    counter += 1
        # If the counter is equal to the number of alcoholized liquids, then the doubled drink is available for the user
        if counter == len(alcoholized_liquids):
            return True
        else:
            return False

    # Method that determines if the bottles have enough to make a virgin drink (all the alcohol is replaced by filler)
    def enough_for_virgin(self, bottles):
        # Find the total volume of alcohol in the drink
        added_volume = self.__alcohol_volume()
        total_volume = added_volume
        # Find the default volume of filler and add it to added_volume
        for liquid in self.liquids:
            for bottle in bottles:
                if bottle.get_liquid_type() == liquid.string_name and liquid.is_filler is True:
                    total_volume += self.ingredients.get(liquid)
                # Check if the total volume is higher than the remaining volume in the bottle
                if bottle.get_volume_left() >= total_volume:
                    return True
                else:
                    return False

    # Method called to make the drink
    def make(self, bottles):
        for bottle in bottles:
            for liquid in self.liquids:
                if bottle.get_liquid_type() == liquid.string_name:
                    # TODO call g-code
                    for ounces in self.ingredients.get(liquid):
                        # TODO call g-code pour
                        # When the cup uses the distributor of a liquid, we need to update the
                        # quantity remaining of that liquid.
                        # If the liquid is alcoholized and the user wants it doubled, the quantity needs to be doubled
                        if liquid.is_alcoholized is True and self.double is True:
                            bottle.pour(2 * self.ingredients.get(liquid))
                        # If the liquid is the filler and the drink is doubled, the quantity of filler needs to be
                        # reduced by the extra volume added to have the same drink volume
                        elif liquid.is_filler is True and self.double is True:
                            volume_to_remove = self.__alcohol_volume()
                            poured_ounces = self.ingredients.get(liquid) - volume_to_remove
                            bottle.pour(poured_ounces)
                        else:
                            bottle.pour(self.ingredients.get(liquid))
        self.__make_normal()

    # Method that finds the alcoholized liquids in the drink
    def __find_alcoholized(self):
        alcoholized_list = []
        # If the ingredient in the drink is alcoholized, it is added to the list
        for liquid in self.liquids:
            if liquid.is_alcoholized is True:
                alcoholized_list.append(liquid)
        return alcoholized_list

    # Method that calculates the volume of alcohol (whatever the type) in the drink
    def __alcohol_volume(self):
        alcohol_volume = 0
        alcoholized_list = self.__find_alcoholized()
        # Sum of the volumes of all the alcoholized ingredients in the drink
        for liquid in alcoholized_list:
            alcohol_volume += self.ingredients.get(liquid)
        return alcohol_volume

    # Method that is called after the drink has been made to make it normal again
    def __make_normal(self):
        self.double = False
        self.virgin = False


# TODO CHANGE THE SHIT
class BottleManager:
    def __init__(self, json_handler):
        self.json_handler = json_handler
        bottles = self.json_handler.load_bottles()
        self.number_of_bottles = len(bottles)
        self.bottles_dict = {}
        self.update(bottles)

    def change_bottle(self, bottle, slot):
        if slot > self.number_of_bottles:
            raise ValueError("slot number given exceeds the physical number of slots")
        self.bottles_dict.update({slot: bottle})

    def update(self, bottles):
        if len(bottles) > self.number_of_bottles:
            raise ValueError("Too Many bottles for the number of slots")
        for bottle in bottles:
            self.bottles_dict.update({bottle.get_slot_number(): bottle})
        self.json_handler.save_data(bottles)

    def remove_bottle(self, slot):
        self.bottles_dict.update({slot: None})

    def save_data(self):
        self.json_handler.save_data(list(self.bottles_dict.values()))


class DrinkManager:
    def __init__(self, json_handler, bottle_manager):
        self.json_handler = json_handler
        self.drinks = self.json_handler.load_drinks()
        self.bottle_manager = bottle_manager

    # Method that returns a list of the available drinks depending on the bottles
    def get_available_drinks(self):
        available_drinks = []
        for drink in self.drinks:
            if drink.is_available(list(self.bottle_manager.bottles_dict.values())) is True:
                available_drinks.append(drink)
        return available_drinks
