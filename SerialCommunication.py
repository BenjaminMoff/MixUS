import serial
import threading


class SerialSynchroniser:
    """
    Class responsible to communicate with the motor controller board by serial port
    """
    serial_port = None
    instruction_done = threading.Condition()
    read = False
    writer_thread = None
    reader_thread = None

    def set_serial_port(self, port_string):
        if self.serial_port is not None:
            self.serial_port.close()

        self.serial_port = serial.Serial(port_string, baudrate=9600, timeout=0.5)

    def start_writer_thread(self, instructions):
        self.writer_thread = threading.Thread(name="SerialWriter", target=self.__send_instructions, args=instructions)
        self.__start_reading_thread()
        self.writer_thread.start()

    def __send_instructions(self, instructions):
        if self.serial_port is None:
            raise Exception("Unable to send instructions, no serial port opened")

        for instruction in instructions:
            self.__send_instruction(instruction)
            self.instruction_done.wait()

        self.read = False

    def __send_instruction(self, instruction):
        for string in instruction:
            self.serial_port.write(string)

    def __start_reading_thread(self):
        self.reader_thread = threading.Thread(name="SerialReader", target=self.__read_from_serial)
        self.reader_thread.start()

    def __read_from_serial(self):
        while self.read:
            # TODO validate if lines can be read more than once
            if self.serial_port.readline() == "Instruction completed":
                self.instruction_done.notify_all()


class GCodeGenerator:
    """
    Class responsible to generate g-code instructions to execute when making a drink
    """
    @staticmethod
    def move_to_slot(index):
        """
        :param index: (int) slot under which the cup should move to
        :return: List of instructions to move the cup under the specified slot
        """
        # TODO define actual positions of slots
        position = index * 100
        return ["G1 X%d Y0 Z0\n" % position, "M400\n", "M118 Instruction completed\n"]

    @staticmethod
    def pour(ounces):
        """
        :param ounces: (int) Number of ounces to pour in the cup
        :return: List of instructions to pour the specified amount of ounces in the cup
        """
        # TODO define actual z movement to pour
        z_movement = 100
        instructions = []
        for i in range(ounces):
            # Raise z axis to activate dispenser
            instructions.append(["G1 X0 Y0 Z%d\n" % z_movement, "M400\n", "M118 Instruction completed\n"])

            # Wait 3 seconds to allow the liquid to escape dispenser
            instructions.append(["G4 S3\n", "M400\n", "M118 Instruction completed\n"])

            # Retract z axis to allow dispenser to recharge
            instructions.append(["G1 X0 Y0 Z%d\n" % -z_movement, "M400\n", "M118 Instruction completed\n"])

            # TODO determine if their should be a waiting time to allow dispenser to recharge

        return instructions

    @staticmethod
    def insert_cup():
        """
        :return: List of instructions to retract the cup in the machine
        """
        position = 0
        return ["G1 X0 Y%d Z0\n" % position, "M400\n", "M118 Instruction completed\n"]

    @staticmethod
    def serve_cup():
        """
        :return: List of instructions to get the cup out of the machine
        """
        # TODO define actual maximum y_position of y axis
        instructions = []
        instructions.append(GCodeGenerator.move_to_slot(0))
        y_position = 100
        instructions.append(["G1 X0 Y%d Z0\n" % y_position, "M400\n", "M118 Instruction completed\n"])
        return instructions


if __name__ == '__main__':
    instructions = []
    instructions.append(GCodeGenerator.move_to_slot(1))
    instructions.append(GCodeGenerator.pour(2))
    instructions.append(GCodeGenerator.move_to_slot(3))
    instructions.append(GCodeGenerator.pour(1))
    for instruction in instructions:
        pass
