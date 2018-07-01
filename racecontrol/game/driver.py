# -*- coding: utf-8 -*-
"""
    racecontrol.runner.driver
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Driver class

    :author: Matthias Riegler, 2018
    :license: aGPLv3, see LICENSE.md for more details.
"""


class Driver(dict):
    """ Driver class """

    def __init__(self):
        """ Init """
        self["lap_count"] = 0
        self["best_time"] = -1
        self["lap_time"] = -1
        self["best_lap"] = -1

    @property
    def lap_count(self):
        """ Lap count """
        return self["lap_count"]

    @property
    def lap_time(self):
        """ Last lap time  """
        return self["lap_time"]

    @property
    def best_time(self):
        """ Best lap time  """
        return self["best_time"]

    def add_lap(self, lap_time):
        """ Call when driver passed a new lap  """
        self["lap_count"] += 1
        self["lap_time"] = lap_time
        self._update_driver_best_lap()

    def _update_driver_best_lap(self):
        """ Updates the drivers best lap  """
        if self.best_time < 0:
            self["best_time"] = self["lap_time"]
        elif self["lap_time"] < self["best_time"]:
            self["best_time"] = self["lap_time"]
