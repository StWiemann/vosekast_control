from lib.Pump import Pump
from lib.Tank import Tank
from lib.LevelSensor import LevelSensor
from lib.Valve import Valve

# Vorsekast States
INITED = 'INITED'
MEASURING = 'MEASURING'
TIME_start = 'time_start'
TIME_stop = 'time_stop'
WAS_MEASURE = 'was_measure'
WEIGHT_start = 'weight_start'
WEIGHT_stop = 'weight_stop'

# GPIO Assignment
PIN_PUMP_BASE = 17
PIN_PUMP_MEASURING = 27
PIN_VALVE_MEASURING_SWITCH = 12
PIN_VALVE_MEASURING_DRAIN = 18
PIN_LEVEL_MEASURING_HIGH = 24
PIN_LEVEL_MEASURING_LOW = 25
PIN_LEVEL_BASE_LOW = 5


class Vosekast:

    def __init__(self, gpio_controller):
        try:
            self._gpio_controller = gpio_controller
            # define how the pins a numbered on the board
            self._gpio_controller.setmode(self._gpio_controller.BCM)

            # valves
            self.measuring_drain_valve = Valve('MEASURING_TANK_VALVE', PIN_VALVE_MEASURING_DRAIN, Valve.TWO_WAY, Valve.BINARY, self._gpio_controller)
            self.measuring_tank_switch = Valve('MEASURING_TANK_SWITCH', PIN_VALVE_MEASURING_SWITCH, Valve.SWITCH, Valve.BINARY, self._gpio_controller)
            self.valves = [self.measuring_drain_valve, self.measuring_tank_switch]

            # throttle
            # self.volume_flow_throttle = Valve('VOLUME_FLOW_THROTTLE', PIN, Valve.SWITCH, Valve.BINARY, self._gpio_controller)

            # level_sensors
            self.level_measuring_high = LevelSensor('LEVEL_MEASURING_UP', PIN_LEVEL_MEASURING_HIGH, bool, LevelSensor.HIGH, self._gpio_controller)
            self.level_measuring_low = LevelSensor('LEVEL_MEASURING_LOW', PIN_LEVEL_MEASURING_LOW, bool, LevelSensor.LOW, self._gpio_controller)
            self.level_base_low = LevelSensor('LEVEL_BASE_LOW', PIN_LEVEL_BASE_LOW, bool, LevelSensor.LOW, self._gpio_controller)

            # tanks
            self.stock_tank = Tank('STOCK_TANK', 100, None, None, None, None)
            self.base_tank = Tank('BASE_TANK', 100, None, self.level_base_low, None, None)
            self.measuring_tank = Tank('MEASURING_TANK', 100, None, self.level_measuring_low, self.level_measuring_high, self.measuring_drain_valve)
            self.tanks = [self.stock_tank, self.base_tank, self.measuring_tank]

            # pumps
            self.pump_stock_tank = Pump('STOCK_PUMP', PIN_PUMP_BASE, self.stock_tank, self.base_tank, self._gpio_controller)
            self.pump_measuring_tank = Pump('MEASURING_PUMP', PIN_PUMP_MEASURING, self.base_tank, self.measuring_tank, self._gpio_controller)
            self.pumps = [self.pump_measuring_tank, self.pump_stock_tank]

            self.state = INITED

        except NoGPIOControllerError:
            print('You have to add a gpio controller to control or simulate the components.')

    def clean(self):
        # shutdown pumps
        for pump in self.pumps:
            pump.stop()

        # close valves
        for valve in self.valves:
            valve.close()

class NoGPIOControllerError(Exception):
    pass
