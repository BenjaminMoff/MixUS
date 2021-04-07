import serial
import serial.tools.list_ports
import time
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


class ListUSB:

    def get_usb_devices(self):
        """
        Method that gets all the usb devices connected to the computer
        :return: A list of ports
        """
        ports = []
        for p in list(serial.tools.list_ports.comports()):
            ports.append(list(p))

        com_port = []
        for port in ports:
            com_port.append(port[0])

        return com_port

    def find_usb_device(self):
        """
        Method that gets the port name that has a marlin firmware connected to it
        :return: USB port name
        """
        ports = self.get_usb_devices()
        string = "M118 marlin_detected\n"
        for port in ports:
            ser = serial.Serial(port, 250000, 8, 'N', 1, timeout=1, write_timeout=1)
            time.sleep(1)
            ser.flushInput()
            try:
                ser.write(str.encode(string, 'utf-8'))

                elapsed_time = 0
                start_time = time.time()

                while elapsed_time < 0.5:
                    message = ser.readline().decode(errors='replace')
                    if message == "marlin_detected\r\n":
                        return port
                    elapsed_time = time.time() - start_time
            except Exception:
                pass

        return None


class SerialSynchroniser(QObject):
    """
    Class responsible to communicate with the motor controller board by serial port
    """
    serial_port = None
    progress_notifier = pyqtSignal(int)
    parent = None
    checkpoints = None
    __serial_communication_thread = None
    singleton = None

    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = QObject.__new__(cls)
        return cls.singleton

    def __init__(self):
        super().__init__()
        self.set_serial_port()
        self.__serial_communication_thread = SerialCommunicator(self)
        self.singleton = self

    def set_serial_port(self):
        """
        Set the serial port of the SerialSynchroniser
        """
        if self.serial_port is not None:
            self.serial_port.close()
        list_usb = ListUSB()
        port_string = list_usb.find_usb_device()
        self.serial_port = Serial(port_string, baudrate=250000, timeout=0.1)

    def begin_communication(self, instructions):
        """
        Begin communication with Marlin
        :param instructions: () parent with slots linked to emited signals
        """
        self.communicate = Flag(True)
        self.__serial_communication_thread.update(self.serial_port, instructions, self.communicate)
        self.__serial_communication_thread.start()
        self.__serial_communication_thread.wait(1)

    def track_progress(self, parent, checkpoints=None, max_value=None):
        """
        Track the progress of the current operation with checkpoints
        :param parent: parent with slots linked to emited signals
        :param checkpoints: (dict{int: string}) checkpoints at which a signal is emited
        :param max_value: (int) maximum value of the progress
        """
        self.parent = parent
        if checkpoints is not None and max_value is not None:
            self.checkpoints = checkpoints
            self.max_value = max_value
            self.progress_notifier.connect(self.on_progress)
        else:
            self.__serial_communication_thread.finished.connect(self.on_end_of_communication)

    @pyqtSlot(int)
    def on_progress(self, value):
        """
        Receives signal when progress detected and notify parent
        :param value: (int) value emited by the signal
        """
        self.parent.progress.emit(int(value / self.max_value * 100))
        if value in list(self.checkpoints.keys()):
            self.parent.checkpoint_reached.emit(self.checkpoints.get(value))
        if value is self.max_value:
            self.parent.drink_completed.emit()

    @pyqtSlot()
    def on_end_of_communication(self):
        """
        Receives signal at end of communication and notify parent
        """
        self.parent.instruction_completed.emit()

    def wait_end_of_communication(self):
        """
        Wait for the communication thread to end
        """
        if self.__serial_communication_thread is not None:
            self.__serial_communication_thread.wait()

    def abort_communication(self):
        """
        Stop sending instructions
        """
        if self.__serial_communication_thread is not None:
            self.communicate.set(False)
            self.__serial_communication_thread.wait()

    def can_start_communication(self):
        """
        Verifies if the serial port is still available
        """
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
        """
        Updates the thread's parameters before running
        :param serial_port: (Serial) serial port that host communication
        :param instructions: (list of list of string) instructions to send
        :param communicate: (Flag) flag that indicates if the communication should continue
        """
        self.instructions = instructions
        self.serial_port = serial_port
        self.communicate = communicate

    def run(self):
        """
        Executes communication protocol
        """
        for index, instruction in enumerate(self.instructions):
            if not self.communicate.get():
                return
            self.__send_instruction(instruction)
            self.__read_from_serial("Instruction completed\r\n")
            self.progress_notifier.emit(self.parent.progress_notifier.emit(index + 1))

    def __send_instruction(self, instruction):
        """
        Sends an instruction trough serial port
        :param instruction: (list of string) instruction to be sent
        """
        for string in instruction:
            time.sleep(1)
            self.serial_port.write(str.encode(string, "utf-8"))

    def __read_from_serial(self, trigger_msg):
        """
        Reads the serial port's buffer until trigger message is read
        :param trigger_msg: (string) string to look for in the serial port's buffer
        """
        self.__instruction_done = False
        while not self.__instruction_done and self.communicate.get():
            message = self.serial_port.readline().decode("utf-8")
            if message == trigger_msg:
                self.__instruction_done = True


class GCodeGenerator:
    """
    Class responsible to generate g-code instructions to execute when making a drink
    """
    max_x = 790
    max_y = 150
    max_z = 20

    speed_x = 5000
    speed_y = speed_x
    speed_z = 1000

    position_dict = {
        1: 7,
        2: 155,
        3: 303,
        4: 490,
        5: 640,
        6: 790}

    @staticmethod
    def move_to_slot(index):
        """
        :param index: (int) slot under which the cup should move to
        :return: (list of list of string) List of instructions to move the cup under the specified slot
        """
        position = GCodeGenerator.position_dict.get(index)
        if index != 0:
            return [["G1 X%d F%d\n" % (position, GCodeGenerator.speed_x), "M400\n", "M118 Instruction completed\n"]]
        return [["G28 X\n", "M400\n", "M118 Instruction completed\n"]]

    @staticmethod
    def pour(ounces):
        """
        :param ounces: (int) Number of ounces to pour in the cup
        :return: (list of list of string) List of instructions to pour the specified amount of ounces in the cup
        """
        instructions = []
        for i in range(ounces):
            # Raise z axis to activate dispenser
            instructions.append(["G1 Z%d F%d\n" % (GCodeGenerator.max_z, GCodeGenerator.speed_z), "M400\n", "M118 Instruction completed\n"])

            # Wait 3 seconds to allow the liquid to escape dispenser
            instructions.append(["G4 S3\n", "M400\n", "M118 Instruction completed\n"])

            # Retract z axis to allow dispenser to recharge
            instructions.append(["G28 Z\n", "M400\n", "M118 Instruction completed\n"])

        return instructions

    @staticmethod
    def insert_cup():
        """
        :return: (list of list of string) List of instructions to retract the cup in the machine
        """
        instructions = [["G28 Y\n", "M400\n", "M118 Instruction completed\n"]]
        return instructions

    @staticmethod
    def serve_cup():
        """
        :return: (list of list of string) List of instructions to get the cup out of the machine
        """
        instructions = []
        instructions.extend(GCodeGenerator.move_to_slot(0))
        instructions.append(["G1 Y%d F%d\n" % (GCodeGenerator.max_y, GCodeGenerator.speed_y), "M400\n", "M118 Instruction completed\n"])
        return instructions

    @staticmethod
    def wait_for_cup():
        """
        :return: (list of list of string) List of instructions to deploy y axis in order to get the cup from the user
        """
        return [["G1 Y%d F%d\n" % (GCodeGenerator.max_y, GCodeGenerator.speed_y), "M400\n", "M118 Instruction completed\n"]]

    @staticmethod
    def home():
        """
        :return: (list of list of string) List of instructions to home each axis
        """
        instructions = [["G28 Z\n", "M400\n", "M118 Instruction completed\n"],
                        ["G28 Y\n", "M400\n", "M118 Instruction completed\n"],
                        ["G28 X\n", "M400\n", "M118 Instruction completed\n"]]
        return instructions

    @staticmethod
    def move_axis(pos, axis):
        """
        :param pos: (int) Position to move the axis to
        :param axis: (str) Axis X, Y or Z to be moved
        :return: (list of list of string) set of instructions to send to Marlin
        """
        a = str(axis)
        speed = GCodeGenerator.speed_x if a == "X" else GCodeGenerator.speed_y if a == "Y" else GCodeGenerator.speed_z
        if (a == "X" and pos > GCodeGenerator.max_x) or (a == "Y" and pos > GCodeGenerator.max_y) or (
                a == "Z" and pos > GCodeGenerator.max_z):
            raise ValueError(
                "position given for the current axis is greater than the max distance on the physical axis")
        instructions = [["G1 " + a + "%d F%d" % (pos, speed) + "\n", "M400\n", "M118 Instruction completed\n"]]
        return instructions

    @staticmethod
    def disable_steppers():
        """
        :return: (list of list of string) set of instructions to deactivate steppers
        """
        return [["M18\n", "M400\n", "M118 Instruction completed\n"]]

    @staticmethod
    def setup_accelerations():
        """
        :return: (list of list of string) set of instructions to setup the motors accelerations
        """
        return [["M201 X50 Y50\n", "M400\n", "M118 Instruction completed\n"]]
