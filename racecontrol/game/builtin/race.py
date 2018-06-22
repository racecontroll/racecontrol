# -*- coding: utf-8 -*-
"""
    racecontrol.runner.race
    ~~~~~~~~~~~~~~~~~~~~~~~

    Race implementation, no fancy modes

    :copyright: (c) 2018 by Matthias Riegler.
    :license: aGPLv3, see LICENSE.md for more details.
"""


import asyncio
import logging
from ... import messages
from .. import race_states
from ..base_race import BaseRace


logger = logging.getLogger(__name__)


class Race(BaseRace):
    """ Standart Race, no fancy modes, just lap for lap """

    async def _setup_race(self):
        """ Initializes all tasks """

    async def _handle_request(self, request):
        """ Handles a request

        :returns: True if an event was handled, false otherwise. This is needed
                  so that the status can be updated(!!!)
        """
        if request["subject"] == messages.MSG_START:
            self._ensure_future(self._on_start())
        elif request["subject"] == messages.MSG_PAUSE:
            # @TODO
            pass
            return False
        else:
            logger.warning(f"Could not handle {request}")
            return False

        return True

    async def _on_start(self):
        """ This method gets called on race start """
        if self._current_state["status"] == race_states.STARTED:
            return

        self._current_state["status"] = race_states.STARTED

        logger.info("Race started")
        self._started = True

        # Dummy for testing @TODO
        self._ensure_future(self._tmp_player0())
        self._ensure_future(self._tmp_player1())

    async def _tmp_player0(self):
        while True:
            await self._on_lap_finished(0, 100)
            await asyncio.sleep(2)

    async def _tmp_player1(self):
        while True:
            await self._on_lap_finished(1, 100)
            await asyncio.sleep(3)
