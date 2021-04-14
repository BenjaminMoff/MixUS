from __future__ import print_function, unicode_literals

import sys, os

import inquirer as inquirer

from DataModel import *
from Enums import Paths, Liquid
from JsonHandler import JsonHandler

from PyInquirer import style_from_dict, Token, prompt
from pprint import pprint

max_volume = 8  # Max volume (in ounces) in a drink


class CmdUI:
    drink_name = None
    drink_liquids = []
    ingredient_dict = {}
    image_path = None

    def __init__(self, drink_manager):
        self.liquids = Liquid.list()[1:]
        self.drink_manager = drink_manager
        self.__style()

    def __style(self):
        self.style = style_from_dict({
            Token.Separator: '#cc5454',
            Token.QuestionMark: '#673ab7 bold',
            Token.Selected: '#cc5454',  # default
            Token.Pointer: '#673ab7 bold',
            Token.Instruction: '',  # default
            Token.Answer: '#f44336 bold',
            Token.Question: '',
        })

    @staticmethod
    def action_inquirer():
        action = prompt([
            {
                'type': 'list',
                'message': 'Sélectionner votre choix',
                'name': 'output',
                'choices': [
                    'Ajouter une nouvelle boisson à la base de données',
                    'Retirer une boisson de la base de données',
                ],
            }
        ])['output']

        print(action)
        return action.startswith('Ajouter')


    def drink_name_inquirer(self):
        self.drink_name = prompt([
            {
                'type': 'input',
                'message': '\nNom de la nouvelle Boisson \n (Pour annuler, entrer: exit):',
                'name': 'output',
                'validate': lambda answer: \
                    'Le nom de la boisson doit avoir au moins 4 charactères' if self.__verify_drink_name(answer) == 0 \
                        else (
                        'Une boisson portant ce nom existe déjà dans la base de données' if self.__verify_drink_name(
                            answer) == 1 else True),

            }
        ], style=self.style)["output"]

        if self.drink_name == "exit":
            sys.exit("User exited app")
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        return self.drink_name

    def liquids_inquirer(self):

        self.drink_liquids = prompt([
            {
                'type': 'checkbox',
                'message': 'Sélectionner les Liquides pour la nouvelle Boisson',
                'name': 'output',
                'choices': [{'name': liquid} for liquid in self.liquids],
            }
        ], style=self.style)["output"]

        if len(self.drink_liquids) == 0:
            print('\033[1m' + '\033[4m' + "La boisson doit avoir au moins un ingrédient" + '\033[0m')
            drink_liquids = self.liquids_inquirer()
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        return self.drink_liquids

    def quantity_inquirer(self, liquid):
        volume = prompt([
            {
                'type': 'input',
                'message': '\nEntrer la quantité de ' + liquid + ' dans la boisson (en once)',
                'name': 'output',
                'validate': lambda answer: 'Le volume maximal est de ' + str(
                    max_volume) + ' onces' if self.__verify_drink_volume(answer) == 0 else (
                    'Le volume entrer doit être un nombre entier (en onces)' if self.__verify_drink_volume(
                        answer) == 1 else True),
            }
        ])["output"]
        self.ingredient_dict.update({self.drink_liquids[len(self.ingredient_dict)]: volume})
        return int(volume)

    def image_path_inquirer(self):
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        self.image_path = prompt([
            {
                'type': 'input',
                'message': '\nTout d\'abord, ajouter l\'image dans le dossier resources/ du code.\n'
                           'L\'image doit être de format .png ou .jpg\n'
                           'Ensuite, indiquer le nom du fichier de l\'image + l\'extension ex:Rhum_and_coke.png',
                'name': 'output',
                'default': 'rhum_and_coke.jpg',
                # TODO changer le default pour une vrai image par default
                'validate': lambda
                    answer: 'Le fichier ne se trouve pas dans le répertoire resources/' if self.__verify_image_path(
                    answer) == 0 else (
                    'Le type de fichier n\'est pas supporté par l\'application' if self.__verify_image_path(
                        answer) == 1 else True),
            }
        ])["output"]
        print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
        self.image_path = "resources/" + self.image_path
        return self.image_path

    def confirm_choice(self):
        display_ingredients = ''
        for ingredient in list(self.ingredient_dict):
            display_ingredients += str(self.ingredient_dict.get(ingredient)) + ' once(s) de ' + str(ingredient) + '\n'
        confirm = prompt([
            {
                'type': 'confirm',
                'message': '\nBoisson à ajouter:\n'
                           'nom: ' + self.drink_name + '\n'
                           + display_ingredients +
                           'fichier de l\'image: ' + str(self.image_path) + '\n Confirmer',
                'name': 'output',
                'default': True,
            }
        ])["output"]

        return confirm

    def remove_drink(self):
        drink_to_remove = prompt([
            {
                'type': 'list',
                'message': 'Sélectionner la Boisson à retirer de la base de données',
                'name': 'output',
                'choices': [{'name': drink.name} for drink in drink_manager.drinks]
            }
        ])["output"]
        return self.drink_manager.get_drink_from_name(drink_to_remove)

    def __verify_drink_name(self, answer):
        if len(answer) < 4:
            return 0

        for drink in self.drink_manager.drinks:
            if drink.name == answer:
                return 1
        return 2

    @staticmethod
    def __verify_drink_volume(answer):
        try:
            answer = int(answer)
        except ValueError:
            return 1

        if answer > 12:
            return 0

        return 2

    def __verify_image_path(self, answer):
        extension = ''.join(list(answer)[-4:])
        if extension != '.jpg' and extension != '.png':
            return 1

        try:
            open(os.path.join(os.path.dirname(__file__), "resources/" + answer))
        except FileNotFoundError:
            return 0

        return 2


class NewDrink:
    name = None
    ingredients = []
    ingredients_dict = {}
    image_path = None
    drink = None

    def __init__(self, cmd_ui, drink_manager):
        self.cmd_ui = cmd_ui
        self.drink_manager = drink_manager
        self.json_handler = json_handler
        self.get_action()

    def get_action(self):
        action = self.cmd_ui.action_inquirer()
        if action == 1:
            self.get_drink_parameters()
        else:
            self.remove_drink()

    def get_drink_parameters(self):
        self.name = self.cmd_ui.drink_name_inquirer()
        self.ingredients = self.cmd_ui.liquids_inquirer()
        self.get_volumes()
        self.image_path = self.cmd_ui.image_path_inquirer()

        if self.cmd_ui.confirm_choice() == 1:
            self.drink = Drink(self.name, self.ingredients_dict, self.image_path)
            self.drink_manager.add_new_drink(self.drink)
            self.drink_manager.save_data()

    def remove_drink(self):
        drink_to_remove = self.cmd_ui.remove_drink()
        self.drink_manager.remove_drink(drink_to_remove)
        self.drink_manager.save_data()

    def get_volumes(self):
        print('\033[1m' + '\033[4m' + 'Le volume de la boisson dépasse la limite de ' + str(
            max_volume) + ' onces' + '\033[0m')
        vol_tot = 0
        for ingredient in self.ingredients:
            vol = self.cmd_ui.quantity_inquirer(ingredient)
            vol_tot += vol
            if vol_tot > 12:
                self.ingredients_dict.clear()
                self.cmd_ui.ingredient_dict.clear()
                self.get_volumes()
                break
            self.ingredients_dict.update({ingredient: vol})


if __name__ == '__main__':
    json_handler = JsonHandler(Paths.BOTTLES.value, Paths.DRINKS.value)
    bottle_manager = BottleManager(json_handler)
    drink_manager = DrinkManager(json_handler, bottle_manager)

    new_drink = NewDrink(CmdUI(drink_manager), drink_manager)

#     json_handler = JsonHandler(Paths.BOTTLES.value, Paths.DRINKS.value)
#     bottle_list = [Bottle(1, Liquid.RUM, 5), Bottle(2, Liquid.VODKA, 500),
#                    Bottle(3, Liquid.TEQUILA, 375), Bottle(4, Liquid.CRANBERRY_JUICE, 1000),
#                    Bottle(5, Liquid.TRIPLE_SEC, 750), Bottle(6, Liquid.ORANGE_JUICE, 1000)]
#     json_handler.save_data(bottle_list)
