import logging
from lib.Log import LOGGER
import asyncio
from lib.utils.Msg import StatusMessage
from datetime import datetime

class TankFillingTimeout(Exception):
    pass

class Tank():
    # tank states
    UNKNOWN = -1
    DRAINED = -0.1
    EMPTY = 0
    FILLED = 1
    BETWEEN = 0.5

    IS_DRAINING = "IS_DRAINING"
    IS_FILLING = "IS_FILLED"

    def __init__(
        self,
        name,
        capacity,
        level_sensor,
        drain_sensor,
        overflow_sensor,
        drain_valve,
        source_pump,
        vosekast,
        protect_draining=True,
        protect_overflow=True,
    ):

        super().__init__()
        self.name = name
        self.capacity = capacity
        self.level_sensor = level_sensor
        self.drain_sensor = drain_sensor
        self.overflow_sensor = overflow_sensor
        self.drain_valve = drain_valve
        self.source_pump = source_pump
        self.vosekast = vosekast
        self.state = self.UNKNOWN
        self.progress = None
        self.logger = logging.getLogger(LOGGER)
        self.protect_draining = protect_draining
        self.protect_overflow = protect_overflow
        self.mqtt = self.vosekast.mqtt_client

        # register callback for overfill if necessary
        if overflow_sensor is not None:
            self.overflow_sensor.add_callback(self._up_state_changed)

        if drain_sensor is not None:
            self.drain_sensor.add_callback(self._low_position_changed)

    def drain_tank(self):
        if self.drain_valve is not None:
            self.drain_valve.open()
            self.progress = self.IS_DRAINING
        else:
            self.logger.warning(
                "No valve to drain the tank {}".format(self.name))

    def prepare_to_fill(self):
        if self.drain_valve is not None:
            self.drain_valve.close()
        else:
            self.logger.debug(
                "No drain valve on the tank {}".format(self.name))
            mqttmsg = StatusMessage(self.name, 'Drain valve missing.', None, None, None)
            self.mqtt.publish_message(mqttmsg)
            return
        self.logger.info("Ready to fill the tank {}".format(self.name))

        mqttmsg = StatusMessage(
            self.name, 'Ready to fill the tank.', None, None, None)
        self.mqtt.publish_message(mqttmsg)

    async def _up_state_changed(self, pin, alert):
        if alert:
            self._on_full()
        else:
            self._on_draining()

    async def fill(self):
        #get time
        time_filling_t0 = datetime.now()
        #close valves, start pump
        self.vosekast.prepare_measuring()

        #check if stock_tank full
        while not self.vosekast.stock_tank.is_filled:
            time_filling_t1 = datetime.now()
            time_filling_passed = time_filling_t1 - time_filling_t0
            delta_time_filling = time_filling_passed.total_seconds()
            
            #if filling takes longer than 600s
            if delta_time_filling >= 6:
                self.logger.error(
                "Filling takes too long. Please make sure that all valves are closed and the pump is working. Aborting.")
                raise TankFillingTimeout("Tank Filling Timeout.")

            print(str(delta_time_filling) + 's < time allotted (6s)')
            await asyncio.sleep(1)
                       
        return

    def _on_draining(self):
        """
        internal function to register that the tank gets drained from highest position
        :return:
        """
        self.state = self.BETWEEN
        mqttmsg = StatusMessage(self.name, 'DRAINING', None, None, None)

        self.logger.info("Tank {} is being drained.".format(self.name))
        self.mqtt.publish_message(mqttmsg)

    def _on_full(self):
        """
        internal function to register that the tank is filled
        :return:
        """
        self.state = self.FILLED
        mqttmsg = StatusMessage(self.name, 'FULL', None, None, None)

        self.logger.warning("Tank {} is full.".format(self.name))
        self.mqtt.publish_message(mqttmsg)

        if self.source_pump is not None and self.protect_overflow:
            self.source_pump.stop()

    async def _low_position_changed(self, pin, alert):
        if alert:
            self._handle_drained()
        else:
            self._handle_filling()

    def _handle_filling(self):
        """
        internal function to register that the tank gets filled
        :return:
        """
        self.state = self.BETWEEN
        mqttmsg = StatusMessage(self.name, 'FILLING', None, None, None)

        self.logger.warning("Tank {} is being filled".format(self.name))
        self.mqtt.publish_message(mqttmsg)

    def _handle_drained(self):
        """
        internal function to register that the tank is drained
        :return:
        """
        self.state = self.DRAINED
        mqttmsg = StatusMessage(self.name, 'DRAINED', None, None, None)

        self.logger.warning("Tank {} is drained".format(self.name))
        self.mqtt.publish_message(mqttmsg)

        if self.drain_valve is not None and self.protect_draining:
            self.drain_valve.close()

    @property
    def is_filled(self):
        return self.state == self.FILLED

    @property
    def is_drained(self):
        return self.state == self.DRAINED    
