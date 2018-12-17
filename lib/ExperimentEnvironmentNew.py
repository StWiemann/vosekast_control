import logging
from lib.Log import LOGGER
import time
import matplotlib.pyplot as plt
from enum import Enum

#from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QTimer, pyqtSlot

from lib.UI.CanvasDynamic import CanvasDynamic
import numpy as np
from numpy import arange, sin, cos, pi, log
import time

PAUSE = 0
RUNNING = 1
READY = 2
STOP = 3

class ExperimentEnvironmentNew(QObject):

    # signals
    state_changed = pyqtSignal(int, name="ExpEnvStateChanged")
    emit_data_point = pyqtSignal(float, float, name="point")

    def __init__(self, delta_t, vosekast, main_window, index=0, funcs=['sin', 'cos', 'sqrt', 'log'], update = False):
        super().__init__()

        self.logger = logging.getLogger(LOGGER)
        self.delta_t = delta_t
        self.vosekast = vosekast

        self._main_window = main_window
        self._exp_env_tab = self._main_window.tabs.tabProgramms
        self._start_pause_button = self._exp_env_tab.exp_env_buttons[index]

        # add instance to gui_elements
        self._start_pause_button.control_instance = self

        # connect signals and slots
        self.emit_data_point.connect(self._exp_env_tab.screen.new_data_point)
        self.state_changed.connect(self._start_pause_button.state_change)

        self.update = update


        self.timer = QTimer
        self.timer.timeout.connect(self.emit_new_data_point)
        self.time_count = 0
        self.change_state(READY)


    def change_state(self, new_state):
        self.state = new_state
        self.logger.debug('New State ' + str(new_state))
        self.state_changed.emit(new_state)

    def get_state(self):
        return self.state

    def start_run(self):
        self.logger.debug("Start run {}".format('Hallo'))

        self.logger.debug('Jetzt sollte geplottet werden')

        t = np.linspace(0, self.delta_t, 200)
        y = sin(t)


        self.vosekast._main_window.tabs.tabProgramms.screen.axes.cla()
        self.vosekast._main_window.tabs.tabProgramms.screen.axes.plot(t,y)
        self.vosekast._main_window.tabs.tabProgramms.screen.draw()
        self.timer.start(1000)

    def send_new_data_point(self):
        self.time_point += 1
        x = self.time_point
        y = sin(self.time_point)
        self.emit_data_point.emit(x, y)


#    @pyqtSlot()
#''    def new_data_point(self):
#        self.logger.debug('Got new point')
#        self.axes.plot(x,y, 'x' 'k')
#        self.draw_idle()

    def update_figure(self):
        self.logger.debug('Update figure')
        print('Hallo')
        self.time_count += 20/100
        self.new_data_point.emit(self.time_count, sin(self.time_count))











        #self.vosekast._main_window.tabs.tabProgramms.screen






        #self.vosekast.pump_measuring_tank.stop()

        #self.change_state(STOP)