from gpiozero import Button
from Enums import HardwareConfig


class LimitSwitch:
    switch_pin = None
    button = None

    def __init__(self, action):
        self.switch_pin = HardwareConfig.limit_switch_pin.value
        self.button = Button(self.switch_pin)
        self.button.when_activated = action

