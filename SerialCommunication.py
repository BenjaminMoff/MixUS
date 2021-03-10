import serial
import serial.tools.list_ports
from serial import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import threading
from PyQt5.QtCore import QObject


class SerialSynchroniser(QObject):
    # TODO : add method to kill thread
    """
    Class responsible to communicate with the motor controller board by serial port
    """
    serial_port = None
    progress_notifier = pyqtSignal(int)
    __instruction_done = False
    __read = False
    __serial_communication_thread = None

    def __init__(self, port_string=None):
        super().__init__()
        if port_string is not None:
            self.set_serial_port(port_string)

    def set_serial_port(self, port_string):
        if self.serial_port is not None:
            self.serial_port.close()
        self.serial_port = Serial(port_string, baudrate=250000, timeout=0.1)

    def begin_communication(self, instructions):
        self.__serial_communication_thread = threading.Thread(name="SerialCommunication",
                                                              target=self.__send_instructions, args=(instructions,))
        self.__serial_communication_thread.start()

    def wait_end_of_communication(self):
        self.__serial_communication_thread.join()

    def can_start_communication(self):
        if self.serial_port is None:
            return False
        ports = []
        for p in list(serial.tools.list_ports.comports()):
            ports.extend(tuple(p))
        return self.serial_port.portstr in ports

    def __send_instructions(self, instructions):
        if self.serial_port is None:
            raise Exception("Unable to send instructions, no serial port opened")

        self.__read_from_serial("echo:  M907 X135 Y135 Z135 E135 135")

        for index, instruction in enumerate(instructions):
            self.__send_instruction(instruction)
            self.__read_from_serial("Instruction completed\r\n")
            self.progress_notifier.emit(index)

    def __send_instruction(self, instruction):
        for string in instruction:
            time.sleep(1)
            print("msg envoye: " + string)
            self.serial_port.write(str.encode(string, "utf-8"))

    def __read_from_serial(self, trigger_msg):
        self.__instruction_done = False
        while not self.__instruction_done:
            message = self.serial_port.readline().decode("utf-8")
            print(message)
            if message == trigger_msg:
                self.__instruction_done = True


class ProgressTracker(QObject):
    completed = pyqtSignal()
    checkpoint_reached = pyqtSignal(str)

    def __init__(self, progress_bar):
        super().__init__()
        self.progress_bar = progress_bar

    def start_tracking(self, signal, checkpoints, max_value):
        """
        :param signal: signal emitted when tracking value updated
        :param checkpoints: dict of significant values and string to be emitted when they're reached
        :param max_value: value at which the progress is completed

        Updates the progress_bar when provided signal is emitted
        Emits signals when checkpoints or max_value are reached
        """
        self.progress_bar.setValue(0)
        self.checkpoints = checkpoints
        self.max_value = max_value

        signal.connect(self.accept_signal)

    def accept_signal(self, value):
        self.progress_bar.setValue(value / self.max_value)
        if value in list(self.checkpoints.keys()):
            self.checkpoint_reached.emit(self.checkpoints.get(value))
        if value is self.max_value:
            self.completed.emit()


class GCodeGenerator:
    """
    Class responsible to generate g-code instructions to execute when making a drink
    """

    # TODO : method for homing at application startup

    @staticmethod
    def move_to_slot(index):
        """
        :param index: (int) slot under which the cup should move to
        :return: List of instructions to move the cup under the specified slot
        """
        # TODO define actual positions of slots
        position = index * 100
        if index != 0:
            return [["G1 X%d\n" % position, "M400\n", "M118 Instruction completed\n"]]
        return [["G28 X\n", "M400\n", "M118 Instruction completed\n"]]

    @staticmethod
    def pour(ounces):
        """
        :param ounces: (int) Number of ounces to pour in the cup
        :return: List of instructions to pour the specified amount of ounces in the cup
        """
        # TODO define actual z movement to pour
        z_movement = 15
        instructions = []
        for i in range(ounces):
            # Raise z axis to activate dispenser
            instructions.append(["G1 Z%d\n" % z_movement, "M400\n", "M118 Instruction completed\n"])

            # Wait 3 seconds to allow the liquid to escape dispenser
            instructions.append(["G4 S3\n", "M400\n", "M118 Instruction completed\n"])

            # Retract z axis to allow dispenser to recharge
            instructions.append(["G28 Z\n", "M400\n", "M118 Instruction completed\n"])

            # TODO determine if their should be a waiting time to allow dispenser to recharge

        return instructions

    @staticmethod
    def insert_cup():
        """
        :return: List of instructions to retract the cup in the machine
        """
        instructions = [["G28 Y\n", "M400\n", "M118 Instruction completed\n"],
                        ["G28 X\n", "M400\n", "M118 Instruction completed\n"],
                        ["G28 Z\n", "M400\n", "M118 Instruction completed\n"]]
        return instructions

    @staticmethod
    def serve_cup():
        """
        :return: List of instructions to get the cup out of the machine
        """
        # TODO define actual maximum y_position of y axis
        instructions = []
        instructions.extend(GCodeGenerator.move_to_slot(0))
        y_position = 120
        instructions.append(["G1 Y%d\n" % y_position, "M400\n", "M118 Instruction completed\n"])
        return instructions
