import unittest
import os
from MixUS.JsonHandler import *
from MixUS.SerialCommunication import GCodeGenerator
from MixUS.Enums import Liquid
from MixUS.DataModel import *


class GCodeTest(unittest.TestCase):

    def setUp(self):
        bottle = [Bottle(1, Liquid.RUM, 25), Bottle(2, Liquid.VODKA, 16),
                  Bottle(3, Liquid.TEQUILA, 12), Bottle(4, Liquid.COKE, 32)]
        self.rum_and_coke = Drink("Rum_and_coke", {Liquid.RUM.string_name: 3, Liquid.COKE.string_name: 9})
        drinks = [self.rum_and_coke]

        json_handler = JsonHandler("GCodeTest_bottles.json", "GCodeTest_drinks.json")
        json_handler.save_data(bottle)
        json_handler.save_data(drinks)

        bottle_manager = BottleManager(json_handler)
        self.drink_manager = DrinkManager(json_handler, bottle_manager)

    def tearDown(self):
        os.remove("GCodeTest_bottles.json")
        os.remove("GCodeTest_drinks.json")

    def test_get_rum_and_coke_instructions(self):
        expected_instructions = []
        expected_instructions.extend(GCodeGenerator.insert_cup())
        expected_instructions.extend(GCodeGenerator.move_to_slot(1))
        expected_instructions.extend(GCodeGenerator.pour(3))
        expected_instructions.extend(GCodeGenerator.move_to_slot(4))
        expected_instructions.extend(GCodeGenerator.pour(9))
        expected_instructions.extend(GCodeGenerator.serve_cup())

        self.assertEqual(self.drink_manager.get_instructions(self.rum_and_coke), expected_instructions)

    def test_get_rum_and_coke_virgin_instructions(self):
        expected_instructions = []
        expected_instructions.extend(GCodeGenerator.insert_cup())
        expected_instructions.extend(GCodeGenerator.move_to_slot(4))
        expected_instructions.extend(GCodeGenerator.pour(12))
        expected_instructions.extend(GCodeGenerator.serve_cup())

        self.assertEqual(self.drink_manager.get_instructions(self.rum_and_coke, is_virgin=True), expected_instructions)

    def test_get_rum_and_coke_double_instructions(self):
        expected_instructions = []
        expected_instructions.extend(GCodeGenerator.insert_cup())
        expected_instructions.extend(GCodeGenerator.move_to_slot(1))
        expected_instructions.extend(GCodeGenerator.pour(6))
        expected_instructions.extend(GCodeGenerator.move_to_slot(4))
        expected_instructions.extend(GCodeGenerator.pour(6))
        expected_instructions.extend(GCodeGenerator.serve_cup())

        self.assertEqual(self.drink_manager.get_instructions(self.rum_and_coke, is_double=True), expected_instructions)


if __name__ == '__main__':
    unittest.main()
