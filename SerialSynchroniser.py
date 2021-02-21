import serial
import threading


class SerialSynchroniser:
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
        self.writer_thread = threading.Thread(name="SerialWriter", target=self.send_instructions(instructions))
        self.start_reading_thread()
        self.writer_thread.start()

    def send_instructions(self, instructions):
        if self.serial_port is None:
            raise Exception("Unable to send instructions, no serial port opened")

        for instruction in instructions:
            self.send_instruction(instruction)
            self.instruction_done.wait()

        self.read = False

    def send_instruction(self, instruction):
        for string in instruction:
            self.serial_port.write(string)

    def start_reading_thread(self):
        self.reader_thread = threading.Thread(name="SerialReader", target=self.read_from_serial)
        self.reader_thread.start()

    def read_from_serial(self):
        while self.read:
            # TODO validate if lines can be read more than once
            if self.serial_port.readline() == "Instruction completed":
                self.instruction_done.notify_all()


class GCodeGenerator:
    @staticmethod
    def move_to_slot(index):
        # TODO define actual positions of slots
        position = index * 100
        return ["G1 X%d Y0 Z0\n" % position, "M400\n", "M118 Instruction completed\n"]

    @staticmethod
    def pour(ounces):
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
        # Retract y axis to insert cup in the machine
        position = 0
        return ["G1 X0 Y%d Z0\n" % position, "M400\n", "M118 Instruction completed\n"]

    @staticmethod
    def serve_cup():
        # Deploy y axis to get the cup out of the machine
        # TODO define actual maximum position of y axis
        position = 100
        return ["G1 X0 Y%d Z0\n" % position, "M400\n", "M118 Instruction completed\n"]


if __name__ == '__main__':
    instructions = []
    instructions.append(GCodeGenerator.move_to_slot(1))
    instructions.append(GCodeGenerator.pour(2))
    instructions.append(GCodeGenerator.move_to_slot(3))
    instructions.append(GCodeGenerator.pour(1))
    for instruction in instructions:
        pass
