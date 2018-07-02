# -*- coding: utf-8 -*-
"""
    racecontrol.game.race_manager
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Manages the different race classes and handlest start/stop/finish

    :author: Matthias Riegler, 2018
    :license: aGPLv3, see LICENSE.md for more details.
"""

import logging
import aioredis
from json import JSONDecodeError
from .. import defaults
from .. import messages
from .builtin import Race


logger = logging.getLogger(__name__)


class GameManager:
    """ Game manager, spins up race instances """

    def __init__(
            self,
            loop,
            redis_uri=defaults.REDIS_URI,
            outgoing_event_channel=defaults.OUTGOING_EVENT_CHANNEL,
            incoming_event_channel=defaults.INCOMING_EVENT_CHANNEL
            ):
        """ Init """
        # Set the event loop
        self._loop = loop
        # Redis URI
        self._redis_uri = redis_uri
        # Outgoing game event channel
        self._outgoing_event_channel = outgoing_event_channel
        # Incoming game events, e.g. race start/stop
        self._incoming_event_channel = incoming_event_channel

        # Async code init
        self.loop.run_until_complete(self._ainit())

        logger.info("Created game manager")

        # Create a race
        self._current_race = Race(game_manager=self,
                                  num_drivers=4)

    async def _ainit(self):
        """ Initializes connection to pubsub, starts track communicator """
        # Connect to redis
        self._redis_subscribe = await aioredis.create_redis(self.redis_uri)
        self._redis_publish = await aioredis.create_redis(self.redis_uri)

        # Create the subscriber for UI events
        self._subscribe = (await self._redis_subscribe
                                     .subscribe(
                                         self.incoming_event_channel))[0]

        # Start input event consumer
        self.loop.create_task(self._input_event_consumer())

    async def _input_event_consumer(self):
        """ Input handler for incoming redis requests  """
        while await self._subscribe.wait_message():

            try:
                request = await self._subscribe.get_json()
                if self.current_race:
                    if request["request"] == messages.MSG_FINISH:
                        await self.current_race.handle_finish(request)
                        self.current_race = Race(game_manager=self,
                                                 num_drivers=4)
                    else:
                        # Pass every other message over to the actual game
                        await self.current_race.handle_request(request)
                else:
                    logger.error("No game instance is running, this should" +
                                 "NEVER happen!")

            except TypeError as te:
                logger.warning(te)

            except JSONDecodeError:
                logger.warning("invalid json request")

    async def push(self, msg):
        """ Pushes a message to the outgoing pubsub channel

        :param msg: Message to send, string or bytestring
        :returns: Receiver count
        """
        return await self._redis_publish.publish(self.outgoing_event_channel,
                                                 msg)

    @property
    def current_race(self):
        """ Current race """
        return self._current_race

    @current_race.setter
    def current_race(self, newrace):
        """ Current race setter """
        if newrace and self.current_race.finished:
            self._current_race = newrace
        else:
            logger.error("Coroutines probably not canceled" +
                         "Leaving old race intact")

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
