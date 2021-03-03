import unittest
from MixUS.SerialCommunication import *

class SerialCommunicationTest(unittest.TestCase):

    def test_serial_communication_with_arduino(self):
        """
        To run this test, an Arduino Mega 2560 must be running test_serial_com.ino and be connected to port COM4
        """
        sp = SerialSynchroniser("COM4")
        instructions = []
        instructions.extend(GCodeGenerator.insert_cup())
        instructions.extend(GCodeGenerator.move_to_slot(2))
        instructions.extend(GCodeGenerator.pour(2))
        instructions.extend(GCodeGenerator.serve_cup())

        sp.begin_communication(instructions)
        sp.wait_end_of_communication()

        self.assertEqual(len(instructions), sp.progress_notifier)


if __name__ == '__main__':
    unittest.main()