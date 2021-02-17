class Bottle:
    def __init__(self, slot_number=None, liquid_type=None, volume_left=None, is_alcoholized=False, is_filler=False):
        self.__slot_number = slot_number
        self.__liquid_type = liquid_type
        self.__volume_left = volume_left            # In ounces
        self.__is_alcooholized = is_alcoholized
        self.__is_filler = is_filler
        self.isempty = False

    # Method that load the object's attributes from a dictionnary
    def load_data_from_dict(self, dict):
        self.__dict__ = dict
        return self

    # Method that keeps tracks of the remaining liquid in the bottle when poured
    def pour(self, ounces=1):
        if self.__volume_left - ounces <= 0:
            self.isempty = True
            return -1
        else:
            self.__volume_left -= ounces

    # Bunch of methods that sets and gets the attributes of Bottle
    def set_liquid_type(self, type):
        self.__liquid_type = type

    def get_liquid_type(self):
        return self.__liquid_type

    def set_volume_left(self, vol_left):
        self.__volume_left = vol_left

    def get_volume_left(self):
        return self.__volume_left

    def set_slot_number(self, slot_number):
        self.__slot_number = slot_number

    def get_slot_number(self):
        return self.__slot_number

    def is_alcoholized(self):
        return self.__is_alcooholized

    def is_filler(self):
        return self.__is_filler


class Drink:
    def __init__(self, name=None, ingredients_dict=None, image_path=None):
        self.name = name
        self.ingredients = ingredients_dict  # self.ingredients is a dictionnary of ingredient:Volume tuples
        self.image_path = image_path  # Path to the image for diplay use
        self.double = False
        self.no_alcool = False

        self.liquids = list(self.ingredients)  # List of the name of the ingredients

    # Method that determines what drinks are available depending on current bottles
    def is_available(self, bottles):
        n = 0
        for ingredient in self.liquids:
            for bottle in bottles:
                # If the remaining volume in the bottle is enough to make the drink, then the counter increases
                if bottle.get_liquid_type() == ingredient and bottle._Bottle__volume_left >= self.ingredients.get(
                        ingredient):
                    n += 1
        # If the counter is equal to the number of ingredients, then the drink is available for the user
        if n == len(self.ingredients):
            return 1
        else:
            return 0

    # Method that determines if the bottles have enough to make a double of this drink (double the alcohol)
    def enough_for_double(self, bottles):
        alcoholized_liquid = self.__find_alcoholized(bottles)
        for bottle in bottles:
            if bottle.get_liquid_type() == alcoholized_liquid and bottle.get_volume_left >= self.ingredients.get(
                    alcoholized_liquid) * 2:
                return 1
        return 0
    # Method that determines if the bottles have enough to make a virgin drink (all the alcohol is replaced by filler)
    def enough_for_virgin(self, bottles):
        total_volume = 0
        # Find the total volume of alcohol in the drink
        added_volume = self.__alcohol_volume(bottles)
        # Find the default volume of filler and add it to added_volume
        for liquid in self.liquids:
            for bottle in bottles:
                if bottle.get_liquid_type() == liquid and bottle.is_filler() == True:
                    total_volume = added_volume + self.ingredients.get(liquid)
                # Check if the total volume is higher than the remaining volume in the bottle
                if bottle.get_volume_left() >= total_volume:
                    return 1
                else:
                    return 0

    # Method called to make the drink
    def make(self, bottles):
        for bottle in bottles:
            for liquid in self.liquids:
                if bottle.get_liquid_type() == liquid:
                    # TODO call g-code
                    for ounces in self.ingredients.get(liquid):
                        # TODO call g-code pour
                        # When the cup uses the distributor of a liquid, we need to update the
                        # quantity remaining of that liquid.
                        # If the liquid is alcoholized and the user wants it doubled, the quantity needs to be doubled
                        if bottle.is_alcoholized() is True and self.double is True:
                            bottle.pour(2 * self.ingredients.get(liquid))
                        # If the liquid is the filler and the drink is doubled, the quantity of filler needs to be
                        # reduced by the extra volume added to have the same drink volume
                        elif bottle.is_filler is True and self.double is True:
                            alcoholized_liquid = self.__find_alcoholized(bottle)
                            poured_ounces = self.ingredients.get(liquid) - self.ingredients.get(alcoholized_liquid)
                            bottle.pour(poured_ounces)
                        else:
                            bottle.pour(self.ingredients.get(liquid))

    # Method that finds the alcoholized liquids in the drink
    def __find_alcoholized(self, bottles):
        alcoholized_list = []
        for bottle in bottles:
            for liquid in self.liquids:
                if bottle.get_liquid_type() == liquid and bottle.is_alcoholized is True:
                    alcoholized_list.append(liquid)
        return alcoholized_list

    # Method that calculates the volume of alcohol (whatever the type) in the drink
    def __alcohol_volume(self, bottles):
        alcohol_volume = 0
        alcoholized_list = self.__find_alcoholized(bottles)
        for liquid in alcoholized_list:
            alcohol_volume += self.ingredients.get(liquid)
        return alcohol_volume


class BottleManager:
    def __init__(self, bottles):
        self.bottles = bottles

    def add_bottle(self, bottle):
        self.bottles.append(bottle)

    def remove_bottle(self, slot_number):
        self.bottles.pop(slot_number)
