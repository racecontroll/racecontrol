# -*- coding: utf-8 -*-
"""
    racecontrol.game.builtin.race
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Race implementation, no fancy modes

    :author: Matthias Riegler, 2018
    :license: aGPLv3, see LICENSE.md for more details.
"""


import logging
from ... import messages
from pprint import pformat
from ..base_race import BaseRace


logger = logging.getLogger(__name__)


class Race(BaseRace):
    """ Standart Race, no fancy modes, just lap for lap """

    async def setup_race(self):
        """ Initializes all tasks """

        self._driver_track_mapping = {}
        for driver in range(self._num_drivers):
            # Map the track to a driver
            self._driver_track_mapping[driver] = driver

    async def on_start(self):
        """ This method gets called on race start """
        if not self.started:
            self.started = True
            logger.info("Race started")

        # Resume
        elif self.started and self.paused:
            self.paused = False
            logger.info("Race resumed")

    async def on_pause(self):
        """ This method gets called when the race is paused """
        if self.started and not self.paused:
            self.paused = True
            logger.info("Race paused")

    async def on_finish(self):
        """ This method gets called when the race is paused """
        logger.info("Race finished!")

    async def on_track_event(self, request):
        """ This method gets called when a track event is registered """
        try:
            if request["type"] == messages.MSG_TRACK_EVENT_LAP_FINISHED:
                if self.started and not self.paused and not self.finished:
                    # Register the driver
                    await self._on_lap_finished(
                            self._driver_track_mapping[
                                int(request["track_id"])],
                            int(request["time"]))
                else:
                    logger.warning(
                            "Registered track event with no running, finished"
                            + " or paused race \n" + pformat(request))
            else:
                logger.warning(
                        f"Unknown track event occured: {request['type']}")

        except KeyError as ke:
            logging.error(f"Could not find {ke} in a seemingly valid request")
