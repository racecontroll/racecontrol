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
import aioredis
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
            loop,
            num_drivers=defaults.NUM_DRIVERS,
            redis_uri=defaults.REDIS_URI,
            outgoing_event_channel=defaults.OUTGOING_EVENT_CHANNEL,
            incoming_event_channel=defaults.INCOMING_EVENT_CHANNEL
            ):
        """ Init """
        # Set the number of drivers
        self._num_drivers = num_drivers
        # Set the event loop
        self._loop = loop
        # Redis URI
        self._redis_uri = redis_uri
        # Outgoing game event channel
        self._outgoing_event_channel = outgoing_event_channel
        # Incoming game events, e.g. race start/stop
        self._incoming_event_channel = incoming_event_channel

        # Initialize game
        self._build_game_state()
        self._started = False
        self._paused = False
        self._finished = False

        # Initialize task handler
        self._tasks = []
        loop.create_task(self._ainit())
        logger.info("Created startup task for the actual race interface")

    def _ensure_future(self, future):
        """ Adds a future to the task queue, so every running task can be
        stopped whenever an error occurs or the race finished
        """
        self._tasks.append(self.loop.create_task(future))

    async def _ainit(self):
        """ Initializes connection to pubsub, starts track communicator """
        # Connect to redis
        self._redis_subscribe = await aioredis.create_redis(self.redis_uri)
        self._redis_publish = await aioredis.create_redis(self.redis_uri)

        # Create the subscriber for UI events
        self._subscribe = (await self._redis_subscribe
                                     .subscribe(
                                         self.incoming_event_channel))[0]

        # Give user code chance to setup the race
        await self._setup_race()

        # Start input event consumer
        self._ensure_future(self._input_event_consumer())
        self.loop.create_task(self._kill_pending_on_exit())

        # Push state every second
        self._ensure_future(self._periodic_state_push())

    async def _periodic_state_push(self, sleep_time=1):
        """ Pushes the game state at a given number of seconds

        :param sleep_time: Number of seconds between state push
        """
        while True:
            self._ensure_future(self._push_state())
            await asyncio.sleep(sleep_time)

    async def _kill_pending_on_exit(self):
        """ Kills remaining tasks when one of the infinite coroutines
        return or throw an Exception
        """
        # Handle all initial tasks and exit if there is an error
        done, pending = await asyncio.wait(
            self._tasks,
            return_when=asyncio.FIRST_COMPLETED
        )

        if pending:
            logger.warning("Race might have ended unexpected")

        for task in pending:
            task.cancel()

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

    @property
    def current_state(self):
        """ Current state of the race """
        copy = self._current_state.copy()
        # Ensure we do not deliver the internal state
        for driver in range(self.num_drivers):
            copy[driver] = copy[driver].copy()

        return copy

    @property
    def num_drivers(self):
        """ Number of drivers in the race """
        return self._num_drivers

    async def _push_state(self):
        """ Pushes the current state to the pubsub so it gets populated over
        the websocket connection established by the web based UI
        """
        try:
            _state_packet = {
                    **self.current_state,
                    "type": messages.REDIS_MSG_TYPE_STATE_PUSH
                    }

            _num_receivers = await self._redis_publish.publish(
                    self.outgoing_event_channel,
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

    async def _setup_race(self):
        """ Race setup goes here, should setup the racemode """
        pass

    async def _handle_request(self, request):
        """ Request handling goes here """
        logger.error("_handle_request(self, request) NOT IMPLEMETED")
        raise NotImplementedError()

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
        if val and self.started and not self.paused:
            self._finished = val
            self._current_state["status"] = race_states.FINISHED
            # DO NOT ADD THIS TO THE TASK LIST
            self.loop.create_task(self._push_state())

    @property
    def loop(self):
        """ Eventloop the relay is running on """
        return self._loop

    @property
    def redis_uri(self):
        """ Redis uri """
        return self._redis_uri

    @property
    def outgoing_event_channel(self):
        """ Outgoing event channel """
        return self._outgoing_event_channel

    @property
    def incoming_event_channel(self):
        """ incoming event channel """
        return self._incoming_event_channel
