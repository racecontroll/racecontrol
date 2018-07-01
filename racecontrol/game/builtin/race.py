# -*- coding: utf-8 -*-
"""
    racecontrol.runner.race
    ~~~~~~~~~~~~~~~~~~~~~~~

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

    async def _setup_race(self):
        """ Initializes all tasks """

        self._driver_track_mapping = {}
        for driver in range(self._num_drivers):
            # Map the track to a driver
            self._driver_track_mapping[driver] = driver

    async def _handle_request(self, request):
        """ Handles a request

        :returns: True if an event was handled, false otherwise. This is needed
                  so that the status can be updated(!!!)
        """
        if request["request"] == messages.MSG_START:
            self._ensure_future(self._on_start())
        elif request["request"] == messages.MSG_PAUSE:
            self.loop.create_task(self._on_pause())
        elif request["request"] == messages.MSG_FINISH:
            # Cleanup! Do NOT add this to the task list!
            self.loop.create_task(self._on_finish())
        elif request["request"] == messages.MSG_TRACK_EVENT:
            self._ensure_future(self._on_track_event(request))
        else:
            logger.warning(f"Could not handle {request}")
            return False

        return True

    async def _on_start(self):
        """ This method gets called on race start """
        if not self.started:
            self.started = True
            logger.info("Race started")

        # Resume
        elif self.started and self.paused:
            self.paused = False
            logger.info("Race resumed")

    async def _on_pause(self):
        """ This method gets called when the race is paused """
        if self.started and not self.paused:
            self.paused = True
            logger.info("Race paused")

    async def _on_finish(self):
        """ This method gets called when the race is paused """
        if self.started and not self.paused:
            self.finished = True
            logger.info("Race finished!")

            # Clean up and end tasks
            for task in self._tasks:
                task.cancel()
            logger.info(f"Ended {len(self._tasks)} runing tasks")

    async def _on_track_event(self, request):
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
