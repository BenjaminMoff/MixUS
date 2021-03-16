import serial
import serial.tools.list_ports
from serial import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, Qt
from PyQt5.QtCore import QObject


class Flag:
    def __init__(self, value):
        self.value = value

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


class SerialSynchroniser(QObject):
    # TODO : add method to kill thread
    """
    Class responsible to communicate with the motor controller board by serial port
    """
    serial_port = None
    progress_notifier = pyqtSignal(int)
    parent = None
    checkpoints = None
    __serial_communication_thread = None
    singleton = None

    def __new__(cls, port_string=None):
        if cls.singleton is None:
            cls.singleton = QObject.__new__(cls, port_string)
        return cls.singleton

    def __init__(self, port_string=None):
        super().__init__()
        if port_string is not None:
            self.set_serial_port(port_string)
        self.__serial_communication_thread = SerialCommunicator(self)
        self.singleton = self

    def set_serial_port(self, port_string):
        if self.serial_port is not None:
            self.serial_port.close()
        self.serial_port = Serial(port_string, baudrate=250000, timeout=0.1)

    def begin_communication(self, instructions):
        self.communicate = Flag(True)
        self.__serial_communication_thread.update(self.serial_port, instructions, self.communicate)
        self.__serial_communication_thread.start()
        self.__serial_communication_thread.wait(1)

    def track_progress(self, parent, checkpoints=None, max_value=None):
        self.parent = parent
        if checkpoints is not None and max_value is not None:
            self.checkpoints = checkpoints
            self.max_value = max_value
            self.progress_notifier.connect(self.on_progress)
        else:
            self.__serial_communication_thread.finished.connect(self.on_end_of_communication)

    @pyqtSlot(int)
    def on_progress(self, value):
        self.parent.progress.emit(int(value / self.max_value * 100))
        if value in list(self.checkpoints.keys()):
            self.parent.checkpoint_reached.emit(self.checkpoints.get(value))
        if value is self.max_value:
            self.parent.drink_completed.emit()
            self.progress_notifier.disconnect()

    @pyqtSlot()
    def on_end_of_communication(self):
        self.parent.instruction_completed.emit()

    def wait_end_of_communication(self):
        self.__serial_communication_thread.wait()

    def abort_communication(self):
        self.communicate.set(False)
        self.__serial_communication_thread.wait()

    def can_start_communication(self):
        if self.serial_port is None:
            return False
        ports = []
        for p in list(serial.tools.list_ports.comports()):
            ports.extend(tuple(p))
        return self.serial_port.portstr in ports


class SerialCommunicator(QThread):
    progress_notifier = pyqtSignal(int)

    def __init__(self, parent):
        super(SerialCommunicator, self).__init__()
        self.parent = parent

    def update(self, serial_port, instructions, communicate):
        self.instructions = instructions
        self.serial_port = serial_port
        self.communicate = communicate

    def run(self):
        self.__send_instructions()

    def __send_instructions(self):
        self.__read_from_serial("echo:  M907 X135 Y135 Z135 E135 135")

        for index, instruction in enumerate(self.instructions):
            if not self.communicate.get():
                return
            self.__send_instruction(instruction)
            self.__read_from_serial("Instruction completed\r\n")
            self.progress_notifier.emit(self.parent.progress_notifier.emit(index + 1))

    def __send_instruction(self, instruction):
        for string in instruction:
            time.sleep(1)
            self.serial_port.write(str.encode(string, "utf-8"))

    def __read_from_serial(self, trigger_msg):
        self.__instruction_done = False
        while not self.__instruction_done and self.communicate.get():
            message = self.serial_port.readline().decode("utf-8")
            if message == trigger_msg:
                self.__instruction_done = True


class GCodeGenerator:
    """
    Class responsible to generate g-code instructions to execute when making a drink
    """
    max_x = 700
    max_y = 120
    max_z = 30

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

        instructions = []
        for i in range(ounces):
            # Raise z axis to activate dispenser
            instructions.append(["G1 Z%d\n" % GCodeGenerator.max_z, "M400\n", "M118 Instruction completed\n"])

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
        instructions.append(["G1 Y%d\n" % GCodeGenerator.max_y, "M400\n", "M118 Instruction completed\n"])
        instructions.append(["G1 Z%d\n" % GCodeGenerator.max_z, "M400\n", "M118 Instruction completed\n"])
        return instructions

    @staticmethod
    def home():
        """
        Method that homes each axis
        :return:
        """
        instructions = [["G28 Z\n", "M400\n", "M118 Instruction completed\n"],
                        ["G28 Y\n", "M400\n", "M118 Instruction completed\n"],
                        ["G28 X\n", "M400\n", "M118 Instruction completed\n"]]
        return instructions

    @staticmethod
    def move_axis(pos, axis):
        """
        :param pos:
        :param axis:
        :return:
        """
        if (axis == "X" and pos and GCodeGenerator.max_x) or (axis == "Y" and pos > GCodeGenerator.max_y) or (axis == "Z" and pos > GCodeGenerator.max_z):
            raise ValueError("position given for the current axis is greater than the max distance on the physical axis")
        instructions = [["G1 " + str(axis) + "%d" % pos + "\n", "M400\n", "M118 Instruction completed\n"]]
        return instructions
