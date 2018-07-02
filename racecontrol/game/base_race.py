# -*- coding: utf-8 -*-
"""
    raceonctrol.runner.base_race
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Race baseclass providing basic functionality

    :author: Matthias Riegler, 2018
    :license: aGPLv3, see LICENSE.md for more details.
"""

import logging
import asyncio
import json
from pprint import pformat
from json.decoder import JSONDecodeError
from .. import defaults
from . import race_states
from .driver import Driver
from .. import messages


logger = logging.getLogger(__name__)


class BaseRace(object):
    """ Basis for the different race modes """

    def __init__(
            self,
            game_manager,
            num_drivers=defaults.NUM_DRIVERS,
            ):
        """ Init """
        # Set the number of drivers
        self._num_drivers = num_drivers
        # Race manager
        self._game_manager = game_manager

        # Initialize game
        self._build_game_state()
        self._started = False
        self._paused = False
        self._finished = False

        # Initialize task handler
        self._tasks = []
        self._ensure_future(self._ainit())
        logger.info("Created startup task for the actual race interface")

    def _ensure_future(self, future):
        """ Adds a future to the task queue, so every running task can be
        stopped whenever an error occurs or the race finished
        """
        self._tasks.append(self.loop.create_task(future))

    async def _garbage_collector(self):
        """ Removes finished coroutines from the task list """
        while True:
            for task in self._tasks:
                if task.done():
                    self._tasks.remove(task)
            await asyncio.sleep(1)

    async def _ainit(self):
        """ Initializes connection to pubsub, starts track communicator """
        # Give user code chance to setup the race
        await self.setup_race()
        self._ensure_future(self._periodic_state_push())
        # self._ensure_future(self._garbage_collector())

    async def _periodic_state_push(self, sleep_time=1):
        """ Pushes the game state at a given number of seconds

        :param sleep_time: Number of seconds between state push
        """
        while True:
            self._ensure_future(self._push_state())
            await asyncio.sleep(sleep_time)

    def _build_game_state(self):
        """ Initializes the game state """
        #: Stores the current state of the race
        self._current_state = {}

        #: Stores the status
        self._current_state["status"] = race_states.NOT_STARTED

        #: Stores the current driver positions
        self._current_state["positions"] = \
            [(driver, 0) for driver in range(self.num_drivers)]

        # Populate all driver entries
        for driver in range(self.num_drivers):
            self._current_state[driver] = Driver()

    async def _push_state(self):
        """ Pushes the current state to the pubsub so it gets populated over
        the websocket connection established by the web based UI
        """
        try:
            _state_packet = {
                    **self.current_state,
                    "type": messages.REDIS_MSG_TYPE_STATE_PUSH
                    }

            _num_receivers = await self.game_manager.push(
                    json.dumps(_state_packet))

            # Debug output for the current state and receiver count
            logger.debug(f"Current game state received by {_num_receivers} " +
                         "clients")
            logger.debug("Current game state:\n" +
                         f"{pformat(_state_packet)}")
        except Exception as e:
            logger.error(e)

    async def _get_driver_lap_count(self):
        """ Get the lap count for each driver

        :returns: [(driver, lap_count), ...]
        """
        return [(driver, self._current_state[driver].lap_count)
                for driver in range(self.num_drivers)]

    async def _update_positions(self):
        """ Update the player positions and publish the new state """
        self._current_state["positions"] = await self._get_driver_lap_count()
        self._current_state["positions"].sort(key=lambda d_lc: d_lc[1])
        self._current_state["positions"].reverse()

        # Update the UI
        await self._push_state()

    async def _on_lap_finished(self, id, lap_time):
        """ Called when a driver finishes a lap """

        # Only perform when the game is running
        if self._current_state["status"] != race_states.STARTED:
            return

        self._current_state[id].add_lap(lap_time)
        # Update the driver positions
        await self._update_positions()

    async def _input_event_consumer(self):
        """ Input handler for incoming redis requests  """
        while await self._subscribe.wait_message():

            try:
                request = await self._subscribe.get_json()
                if await self._handle_request(request):
                    self._ensure_future(self._push_state())

            except TypeError as te:
                logger.warning(te)

            except JSONDecodeError:
                logger.warning("invalid json request")

    async def handle_request(self, request):
        """ Handles a request

        :returns: True if an event was handled, false otherwise. This is needed
                  so that the status can be updated(!!!)
        """
        if request["request"] == messages.MSG_START:
            self._ensure_future(self.on_start())
        elif request["request"] == messages.MSG_PAUSE:
            self._ensure_future(self.on_pause())
        elif request["request"] == messages.MSG_TRACK_EVENT:
            self._ensure_future(self.on_track_event(request))
        else:
            logger.warning(f"Could not handle {request}")
            return False

        await self._push_state()

    async def handle_finish(self, request):
        """ This method gets called when the race is finished, it should clean
        up all running tasks!

        :param request: Request which triggered on_finish
        """
        self.finished = True

        # Give the race code the chance to cleanup!
        await self.on_finish()

        # Nuke running coroutines
        counter = 0
        for task in self._tasks:
            if not task.done():
                task.cancel()
                counter += 1

        logger.info(f"Nuked {counter} running tasks")

    async def _on_track_event(self, request):
        """ This method gets called when a track event is registered """
        raise NotImplementedError()

    async def setup_race(self):
        """ Race setup goes here, should setup the racemode """
        pass

    async def on_start(self):
        """ This method gets called on race start """
        raise NotImplementedError()

    async def on_pause(self):
        """ This method gets called when the race is paused """
        raise NotImplementedError()

    async def on_finish(self):
        """ This method gets called when the race is paused """
        raise NotImplementedError()

    @property
    def num_drivers(self):
        """ Number of drivers in the race """
        return self._num_drivers

    @property
    def game_manager(self):
        """ Race manager """
        return self._game_manager

    @property
    def loop(self):
        """ Event loop """
        return self.game_manager.loop

    @property
    def started(self):
        """ True if the race is started """
        return self._started

    @started.setter
    def started(self, val):
        if val and not self._started and not self.paused and not self.finished:
            self._started = val
            self._current_state["status"] = race_states.STARTED
            self._ensure_future(self._push_state())

    @property
    def paused(self):
        """ True if the race is paused """
        return self._paused

    @paused.setter
    def paused(self, val):
        if self.started and not self.finished:
            self._paused = val
            if val:
                self._current_state["status"] = race_states.PAUSED
                self._ensure_future(self._push_state())
            else:
                self._current_state["status"] = race_states.STARTED
                self._ensure_future(self._push_state())

    @property
    def finished(self):
        """ True if the race is finished """
        return self._finished

    @finished.setter
    def finished(self, val):
        self._finished = val
        self._current_state["status"] = race_states.FINISHED
        # DO NOT ADD THIS TO THE TASK LIST
        self.loop.create_task(self._push_state())

    @property
    def current_state(self):
        """ Current state of the race """
        copy = self._current_state.copy()
        # Ensure we do not deliver the internal state
        for driver in range(self.num_drivers):
            copy[driver] = copy[driver].copy()

        return copy
