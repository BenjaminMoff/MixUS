from gpiozero import Button, BadPinFactory
from Enums import HardwareConfig
from threading import Thread
from time import sleep


class LimitSwitch:
    switch_pin = None
    button = None
    activated = False
    singleton = None
    canceled = False

    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = object.__new__(cls)
        return cls.singleton

    def __init__(self):
        self.switch_pin = HardwareConfig.limit_switch_pin.value
        try:
            self.button = Button(self.switch_pin)
            self.button.when_activated = self.__activate
            self.button.when_deactivated = self.__deactivate
        except BadPinFactory:
            self.activated = True

    def __activate(self):
        self.activated = True

    def __deactivate(self):
        self.activated = False

    def __loop_until(self, runnable, activated):
        while self.activated is not activated and self.canceled is not True:
            sleep(0.1)
        if not self.canceled:
            runnable()
        else:
            self.canceled = False

    def execute_when_activated(self, runnable):
        Thread(self.__loop_until(runnable, True), daemon=True).start()

    def execute_when_deactivated(self, runnable):
        Thread(self.__loop_until(runnable, False), daemon=True).start()

    def cancel(self):
        self.canceled = True

    def is_activated(self):
        return self.activated
