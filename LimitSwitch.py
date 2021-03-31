from Enums import HardwareConfig
from threading import Thread
from time import sleep


class LimitSwitch:
    switch_pin = None
    singleton = None
    canceled = False

    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = object.__new__(cls)
        return cls.singleton

    def __init__(self):
        self.switch_pin = HardwareConfig.limit_switch_pin.value
        try:
            import RPi.GPIO as GPIO
            GPIO.setup(self.switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        except ModuleNotFoundError:
            print("Librairie RPi.GPIO indisponible")

    def __activate(self):
        self.activated = True

    def __deactivate(self):
        self.activated = False

    def __loop_until(self, runnable, activated):
        try:
            import RPi.GPIO as GPIO
            while GPIO.input(self.switch_pin) is not activated and self.canceled is not True:
                sleep(0.1)
            if not self.canceled:
                runnable()
            else:
                self.canceled = False
        except ModuleNotFoundError:
            print("Librairie RPi.GPIO indisponible")
            runnable()

    def execute_when_activated(self, runnable):
        Thread(self.__loop_until(runnable, True), daemon=True).start()

    def execute_when_deactivated(self, runnable):
        Thread(self.__loop_until(runnable, False), daemon=True).start()

    def cancel(self):
        self.canceled = True

    def is_activated(self):
        try:
            import RPi.GPIO as GPIO
            return GPIO.input(self.switch_pin)
        except ModuleNotFoundError:
            print("Librairie RPi.GPIO indisponible")
            return True
