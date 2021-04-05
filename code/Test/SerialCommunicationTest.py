import unittest
from SerialCommunication import *


class SerialCommunicationTest(unittest.TestCase):

    def setUp(self):
        self.instruction_completed_counter = 0

    def test_serial_communication_with_arduino(self):
        """
        To run this test, an Arduino Mega 2560 must be running test_serial_com.ino and be connected to port COM4
        The test can also be ran with the actuak machine board
        """
        serial_synchroniser = SerialSynchroniser()
        serial_synchroniser.progress_notifier.connect(self.accept_progress_notification)
        instructions = []
        instructions.extend(GCodeGenerator.insert_cup())
        instructions.extend(GCodeGenerator.move_to_slot(2))
        instructions.extend(GCodeGenerator.pour(2))
        instructions.extend(GCodeGenerator.serve_cup())

        serial_synchroniser.begin_communication(instructions)
        serial_synchroniser.wait_end_of_communication()

    def accept_progress_notification(self, value):
        self.instruction_completed_counter += 1
        self.assertEqual(self.instruction_completed_counter, value)


if __name__ == '__main__':
    unittest.main()