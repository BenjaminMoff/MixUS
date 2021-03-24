from Enums import Liquid, BottleSize
from SerialCommunication import GCodeGenerator


class Bottle:
    """
    Class that stores current volume and liquid type of bottles on the machine
    """

    def __init__(self, slot_number=None, liquid=None, volume_left_ml=None):
        self.__slot_number = slot_number
        self.__liquid = liquid
        self.__volume_left_ml = volume_left_ml

    def __eq__(self, other):
        return self.__slot_number == other.get_slot_number() and \
               self.__liquid.string_name == other.get_liquid_name() and \
               self.__volume_left_ml == other.get_volume_left()


    def pour(self, ounces=1):
        """
        Method that keeps tracks of the remaining liquid in the bottle when poured
        :param ounces: volume to pour in ounces
        :return:
        """
        if self.__volume_left_ml - BottleSize.ounces_to_ml(ounces) <= 0:
            return -1
        else:
            self.__volume_left_ml -= BottleSize.ounces_to_ml(ounces)

    # Bunch of methods that sets and gets the attributes of Bottle
    def set_liquid(self, liquid):
        self.__liquid = liquid

    def get_liquid(self):
        return self.__liquid

    def get_liquid_name(self):
        return self.__liquid.string_name

    def set_volume_left(self, vol_left):
        self.__volume_left_ml = vol_left

    def get_volume_left(self):
        return self.__volume_left_ml

    def set_slot_number(self, slot_number):
        self.__slot_number = slot_number

    def get_slot_number(self):
        return self.__slot_number

    def is_alcoholized(self):
        return self.__liquid.is_alcoholized

    def is_filler(self):
        return self.__liquid.is_filler

    def copy(self):
        return Bottle(self.__slot_number, self.__liquid, self.__volume_left_ml)


class Drink:
    """
    Class that stores ingredients for a specific drink and image path for display
    """

    def __init__(self, name=None, ingredients_dict=None, image_path=None):
        self.name = name
        self.ingredients = ingredients_dict  # self.ingredients is a dictionary of Liquid.string_name:Volume
        self.image_path = image_path  # Path to the image for display use
        self.liquids = []
        if self.ingredients is not None:
            for ingredient in list(self.ingredients):
                self.liquids.append(Liquid.get_liquid_from_string_name(ingredient))

    def __eq__(self, other):
        return self.name == other.name and \
               self.ingredients == other.ingredients and \
               self.image_path == other.image_path and \
               self.liquids == other.liquids

    def is_available(self, bottles):
        """
        Method that determines if their is enough liquid in the bottle list provided to make the drink
        :param bottles:
        :return:
        """
        available_liquid = []
        required_liquids = list(self.ingredients.keys())

        for liquid in required_liquids:
            for bottle in bottles:
                # If the remaining volume in the bottle is enough to make the drink, then the counter increases
                if bottle.get_liquid_name() == liquid \
                        and bottle.get_volume_left() >= \
                        BottleSize.ounces_to_ml(self.ingredients.get(liquid)):
                    available_liquid.append(bottle.get_liquid_name())
        # If the counter is equal to the number of ingredients, then the drink is available for the user
        required_liquids.sort()
        available_liquid.sort()
        if available_liquid == required_liquids:
            return True
        else:
            return False

    def enough_for_double(self, bottles):
        """
        Method that determines if their is enough liquid in the bottle list provided to make a double of this drink
        (double the alcohol)
        :param bottles:
        :return:
        """
        counter = 0
        alcoholized_liquids = self.__find_alcoholized()
        # Check for each alcoholized liquid if the volume left in the bottle_manager is enough to make a double
        for alcoholized_liquid in alcoholized_liquids:
            for bottle in bottles:
                if bottle.get_liquid_name() == alcoholized_liquid.string_name and bottle.get_volume_left() >= \
                        self.ingredients.get(alcoholized_liquid.string_name) * 2:
                    counter += 1
        # If the counter is equal to the number of alcoholized liquids, then the doubled drink is available for the user
        if counter == len(alcoholized_liquids):
            return True
        else:
            return False

    def enough_for_virgin(self, bottles):
        """
        Method that determines if their is enough liquid in the bottle list provided to make a virgin of this drink
        (all the alcohol is replaced by filler)
        :param bottles:
        :return:
        """
        # Find the total volume of alcohol in the drink
        added_volume = self.alcohol_volume()
        total_volume = added_volume
        # Find the default volume of filler and add it to added_volume
        for liquid in self.liquids:
            for bottle in bottles:
                if bottle.get_liquid_name() == liquid.string_name and liquid.is_filler is True:
                    total_volume += self.ingredients.get(liquid.string_name)
                # Check if the total volume is higher than the remaining volume in the bottle
                if bottle.get_volume_left() >= total_volume:
                    return True
                else:
                    return False

    def __find_alcoholized(self):
        """
        Method that finds the alcoholized liquids in the drink
        :return:
        """
        alcoholized_list = []
        # If the ingredient in the drink is alcoholized, it is added to the list
        for liquid in self.liquids:
            if liquid.is_alcoholized is True:
                alcoholized_list.append(liquid)
        return alcoholized_list

    def alcohol_volume(self):
        """
        Method that calculates the volume of alcohol (whatever the type) in the drink
        :return:
        """
        alcohol_volume = 0
        alcoholized_list = self.__find_alcoholized()
        # Sum of the volumes of all the alcoholized ingredients in the drink
        for liquid in alcoholized_list:
            alcohol_volume += self.ingredients.get(liquid.string_name)
        return alcohol_volume


class BottleManager:
    """
    Class to manage bottles on the machine
    Load data from persistence file at instantiation and saves data when bottle list is modified
    """

    def __init__(self, json_handler):
        self.json_handler = json_handler
        bottles = self.json_handler.load_bottles()
        self.number_of_bottles = len(bottles)
        self.bottles_dict = {}
        self.update(bottles)

    def update(self, bottles):
        """
        Update the BottleManager with a new bottle
        :param bottles: bottle to update the manager with
        :return:
        """
        if len(bottles) > self.number_of_bottles:
            raise ValueError("Too many bottle_manager for the number of slots")
        for bottle in bottles:
            self.bottles_dict.update({bottle.get_slot_number(): bottle})

        # Updates persistence file every time a modification is made
        self.save_data()

    def pour(self, liquid_name, ounces):
        """
        Pour ounces of the given liquid
        :param liquid_name: string_name of the Liquid
        :param ounces: Volume to pour
        :return:
        """
        for bottle in self.bottles_dict.values():
            if bottle.get_liquid_name() == liquid_name:
                bottle.pour(ounces)
                break
        self.save_data()

    def get_bottles(self):
        """
        Get a list of the bottles in the manager
        :return:
        """
        return list(self.bottles_dict.values())

    def remove_bottle(self, slot):
        """
        Remove the bottle from the manager at the given slot
        :param slot:
        :return:
        """
        self.bottles_dict.update({slot: None})

    def save_data(self):
        """
        Save the current manager to the json file
        :return:
        """
        self.json_handler.save_data(self.get_bottles())


class DrinkManager:
    drinks = []

    def __init__(self, json_handler, bottle_manager):
        self.json_handler = json_handler
        self.drinks = self.json_handler.load_drinks()
        self.bottle_manager = bottle_manager

    # Method that returns a list of the available drinks depending on the bottles
    def get_available_drinks(self):
        """
        Method that returns a list of drink that can be made with the content of the bottles stored in bottle_manager
        :return: list of available drinks
        """
        available_drinks = []
        for drink in self.drinks:
            if drink.is_available(list(self.bottle_manager.bottles_dict.values())) is True:
                available_drinks.append(drink)
        return available_drinks

    def get_drink_from_name(self, name):
        """
        Get a drink from a given string
        :param name: string name of the drink
        :return:
        """
        for drink in self.drinks:
            if drink.name == name:
                return drink
        return None

    def add_new_drink(self, drink):
        """
        Add a new drink to the manager
        :param drink: Drink object to add
        :return:
        """
        self.drinks.append(drink)

    def remove_drink(self, drink):
        """
        Remove a drink from the manager
        :param drink: Drink object to remove
        :return:
        """
        self.drinks.remove(drink)

    def save_data(self):
        """
        Save the manager to the json file
        :return:
        """
        self.json_handler.save_data(self.drinks)

    def is_double_available(self, drink):
        """
        returns true if the current drink can be doubled based on the Liquids in the bottles
        :param drink: Drink to be doubled
        :return:
        """
        return drink.enough_for_double(self.bottle_manager.get_bottles())

    def is_virgin_available(self, drink):
        """
        returns true if the current drink can be virgin based on the Liquids in the bottles
        :param drink:
        :return:
        """
        return drink.enough_for_virgin(self.bottle_manager.get_bottles())

    def get_instructions(self, drink, is_double=False, is_virgin=False):
        """
        Returns list of g-code instructions for a specific drink
        :param drink: specified drink to make
        :param is_double: specify if the alcohol content should be doubled
        :param is_virgin: specify if the alcohol content should be removed
        :return: list of list of g-code strings to make the drink
        """
        instructions = []
        poured_liquids = []
        liquid_checkpoints = {}

        # Move the cup in the machine
        instructions.extend(GCodeGenerator.insert_cup())

        # TODO handle multiple fillers
        # Find bottles that match the drink ingredients in their order of apparition in the slots
        for bottle in self.bottle_manager.get_bottles():
            for liquid in drink.liquids:

                # Check for match in bottle liquid and drink ingredients + check if not already poured
                if bottle.get_liquid_name() == liquid.string_name and liquid.string_name not in poured_liquids:
                    poured_liquids.append(liquid.string_name)

                    # Move to the slot if their is liquid to pour
                    if not (liquid.is_alcoholized and is_virgin):
                        # Move to the slot
                        instructions.extend(GCodeGenerator.move_to_slot(bottle.get_slot_number()))

                        # Pour necessary amount of liquid
                        self.__compute_ounces_to_pour(instructions, drink, liquid, is_double, is_virgin)
                        liquid_checkpoints.update({len(instructions): liquid.string_name})

        # Move to slot 0 and get the cup out of the machine
        instructions.extend(GCodeGenerator.serve_cup())
        return instructions, liquid_checkpoints

    def __compute_ounces_to_pour(self, instructions, drink, liquid, is_double=False, is_virgin=False):
        """
        Method that computes the ounces to pour based on the type of drink, if it's doubled or virgin.
        :param instructions: List that is appended with the new instructions
        :param drink: The drink to be made
        :param liquid: The liquid to be poured in the drink
        :param is_double: True if the drink is double
        :param is_virgin: True if the drink is virgin
        :return:
        """
        # If the drink is double, the alcohol content is doubled and the filler is reduced accordingly
        if is_double:
            if liquid.is_alcoholized:
                instructions.extend(GCodeGenerator.pour(2 * drink.ingredients.get(liquid.string_name)))
            elif liquid.is_filler:
                volume_to_remove = drink.alcohol_volume()
                instructions.extend(GCodeGenerator.pour(drink.ingredients.get(liquid.string_name) - volume_to_remove))

        # If the drink is virgin, the alcohol content is removed and the filler is increased accordingly
        elif is_virgin and liquid.is_filler:
            volume_to_add = drink.alcohol_volume()
            instructions.extend(GCodeGenerator.pour(drink.ingredients.get(liquid.string_name) + volume_to_add))

        else:
            instructions.extend(GCodeGenerator.pour(drink.ingredients.get(liquid.string_name)))
