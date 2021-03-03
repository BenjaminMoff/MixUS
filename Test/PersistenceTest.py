import unittest
import os
from MixUS.JsonHandler import *
from MixUS.SerialCommunication import GCodeGenerator
from MixUS.Enums import Liquid
from MixUS.DataModel import *


class PersistenceTest(unittest.TestCase):

    def setUp(self):
        self.bottles = [Bottle(1, Liquid.RUM, 25), Bottle(2, Liquid.VODKA, 16),
                        Bottle(3, Liquid.TEQUILA, 12), Bottle(4, Liquid.COKE, 32)]

        self.drinks = [Drink("Rhum_and_coke", {Liquid.RUM.string_name: 3, Liquid.COKE.string_name: 9}),
                       Drink("Vodka_jus_canneberge", {Liquid.VODKA.string_name: 3, Liquid.CRANBERRY_JUICE.string_name: 9})]

        self.json_handler = JsonHandler("PersistenceTest_bottles.json", "PersistenceTest_drinks.json")

    def tearDown(self):
        if os.path.exists("PersistenceTest_bottles.json"):
            os.remove("PersistenceTest_bottles.json")

        if os.path.exists("PersistenceTest_drinks.json"):
            os.remove("PersistenceTest_drinks.json")

    def test_save_and_load_bottles(self):
        self.json_handler.save_data(self.bottles)
        self.assertEqual(self.json_handler.load_bottles(), self.bottles)

    def test_save_and_load_drinks(self):
        self.json_handler.save_data(self.drinks)
        self.assertTrue(self.json_handler.load_drinks() == self.drinks)


if __name__ == '__main__':
    unittest.main()
