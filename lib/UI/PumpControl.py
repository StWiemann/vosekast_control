from lib.UI.ControlField import ControlField, NoImageForIconError
from lib.Pump import Pump
import os


class PumpControl(ControlField):

    def __init__(self, text):
        super().__init__(text, default_state=Pump.STOPPED)
        self.pump = None

    def set_pump(self, pump_instance):
        self.set_control_instance(pump_instance)
        self.pump = pump_instance
        print('HALLO!!')

    def toggle_control_instance(self):
        if self.state == Pump.RUNNING:
            self.pump.stop()
        else:
            self.pump.start()

    @staticmethod
    def get_icon(state):
        # search for icon
        path = os.path.dirname(os.path.abspath(__file__))

        if state == Pump.RUNNING:
            icon_path = os.path.join(path, 'icons/pump_icons/pump_color_1.png')
        else:
            icon_path = os.path.join(path, 'icons/pump_icons/pump_sw.png')

        if not os.path.isfile(icon_path):
            raise NoImageForIconError

        return icon_path
