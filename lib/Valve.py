import logging
from lib.Log import LOGGER

class Valve:
    # regulations
    BINARY = 'BINARY'
    ANALOG = 'ANALOG'

    # valve_types
    TWO_WAY = 'TWO_WAY'
    THREE_WAY = 'THREE_WAY'
    SWITCH = 'SWITCH'

    def __init__(self, name, control_pin, valve_type, regulation, gpio_controller):
        self.name = name
        self._pin = control_pin
        self.valve_type = valve_type
        self.regulation = regulation
        self._gpio_controller = gpio_controller
        self.logger = logging.getLogger(LOGGER)

        # init the gpio pin
        self._gpio_controller.setup(self._pin, self._gpio_controller.OUT)

    def close(self):
        """
        function close the valve or switch
        :return:
        """
        self.logger.debug(F"Close valve {self.name}")
        self._gpio_controller.output(self._pin, self._gpio_controller.LOW)
