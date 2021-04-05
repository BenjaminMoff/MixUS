from Enums import HardwareConfig
from threading import Thread
from time import sleep

try:
    import RPi.GPIO as GPIO
    library_available = True
except ModuleNotFoundError:
    library_available = False
    print("Librairie RPi.GPIO indisponible")


class LimitSwitch:
    """
    A class that represents the limitSwitch that detects if the Glass is present
    The limitSwitch is normally closed
    """
    switch_pin = None
    singleton = None
    canceled = False

    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = object.__new__(cls)
        return cls.singleton

    def __init__(self):
        self.switch_pin = HardwareConfig.limit_switch_pin.value

        if library_available:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def __loop_until(self, runnable, activated):
        if library_available:
            while not GPIO.input(self.switch_pin) is not activated and self.canceled is not True:
                sleep(0.1)
            if not self.canceled:
                runnable()
            else:
                self.canceled = False
        else:
            runnable()

    def execute_when_activated(self, runnable):
        Thread(self.__loop_until(runnable, True), daemon=True).start()

    def execute_when_deactivated(self, runnable):
        Thread(self.__loop_until(runnable, False), daemon=True).start()

    def cancel(self):
        self.canceled = True

    def is_activated(self, expected=True):
        """
        Returns true if the limit switch is not activated, false if it is (Normally closed limitSwitch)
        :param expected: If the library is not available, expected is given to have the wanted answer.
        :return: bool
        """
        if library_available:
            return not GPIO.input(self.switch_pin)
        return expected
