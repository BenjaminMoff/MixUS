from serial import *
import threading


class SerialSynchroniser:
    """
    Class responsible to communicate with the motor controller board by serial port
    """
    serial_port = None
    __instruction_done = False
    __port = threading.RLock()
    __read = False
    __serial_communication_thread = None

    def __init__(self, port_string=None):
        if port_string is not None:
            self.set_serial_port(port_string)

    def set_serial_port(self, port_string):
        if self.serial_port is not None:
            self.serial_port.close()
        self.serial_port = Serial(port_string, baudrate=9600, timeout=2)

    def begin_communication(self, instructions):
        self.__serial_communication_thread = threading.Thread(name="SerialCommunication", target=self.__send_instructions, args=(instructions,))
        self.__serial_communication_thread.start()

    def __send_instructions(self, instructions):
        if self.serial_port is None:
            raise Exception("Unable to send instructions, no serial port opened")

        for instruction in instructions:
            self.__send_instruction(instruction)
            self.__read_from_serial()

    def __send_instruction(self, instruction):
        self.serial_port.write(str.encode("88888\n"))
        # for string in instruction:
        #     self.serial_port.write(str.encode(string, "utf-8"))
        #     time.sleep(0.5)

    def __read_from_serial(self):
        self.__instruction_done = False
        while not self.__instruction_done:
            message = self.serial_port.readline().decode("utf-8")
            if message != "":
                print(message)
            if message == "Instruction completed\\n":
                self.__instruction_done = True
            time.sleep(0.5)


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
        return ["G1 X%d\n" % position, "M400\n", "M118 Instruction completed\n"]

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
            instructions.append(["G1 Z%d\n" % z_movement, "M400\n", "M118 Instruction completed\n"])

            # Wait 3 seconds to allow the liquid to escape dispenser
            instructions.append(["G4 S3\n", "M400\n", "M118 Instruction completed\n"])

            # Retract z axis to allow dispenser to recharge
            instructions.append(["G1 Z%d\n" % -z_movement, "M400\n", "M118 Instruction completed\n"])

            # TODO determine if their should be a waiting time to allow dispenser to recharge

        return instructions

    @staticmethod
    def insert_cup():
        """
        :return: List of instructions to retract the cup in the machine
        """
        position = 0
        return ["G1 Y%d\n" % position, "M400\n", "M118 Instruction completed\n"]

    @staticmethod
    def serve_cup():
        """
        :return: List of instructions to get the cup out of the machine
        """
        # TODO define actual maximum y_position of y axis
        instructions = []
        instructions.append(GCodeGenerator.move_to_slot(0))
        y_position = 100
        instructions.append(["G1 Y%d\n" % y_position, "M400\n", "M118 Instruction completed\n"])
        return instructions


if __name__ == '__main__':
    sp = SerialSynchroniser("COM4")
    instructions = []
    instructions.append(GCodeGenerator.insert_cup())
    instructions.append(GCodeGenerator.move_to_slot(2))
    instructions.append(GCodeGenerator.pour(2))
    instructions.append(GCodeGenerator.serve_cup())
    sp.begin_communication(instructions)
