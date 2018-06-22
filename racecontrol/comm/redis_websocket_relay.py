# -*- coding: utf-8 -*-
"""
    racecontrol.comm.redis_websocket_relay
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Redis <-> Websocket relay for the realtime communication between the web
    based user interface and the actual game backend

    :copyright: (c) 2018 by Matthias Riegler.
    :license: aGPLv3, see LICENSE.md for more details.
"""


import logging
import asyncio
import aioredis
import websockets
import functools
from .. import defaults


logger = logging.getLogger(__name__)


class RedisWebsocketRelay(object):
    """ Redis <-> Websocket relay to ensure realtime communication between the
    web based user interface and the actual game backend.
    """

    def __init__(
            self,
            loop,
            host=defaults.WEBSOCKET_HOST,
            port=defaults.WEBSOCKET_PORT,
            redis_uri=defaults.REDIS_URI,
            outgoing_event_channel=defaults.OUTGOING_EVENT_CHANNEL,
            incoming_event_channel=defaults.INCOMING_EVENT_CHANNEL,
            outgoing_websocket_path=defaults.WEBSOCKET_STREAM_PATH,
            incoming_websocket_path=defaults.WEBSOCKET_INPUT_PATH
            ):
        """ Initializes the Redis websocket Relay """
        # Event loop
        self._loop = loop
        # Redis URI
        self._redis_uri = redis_uri
        # Outgoing game event channel
        self._outgoing_event_channel = outgoing_event_channel
        # Incoming game events, e.g. race start/stop
        self._incoming_event_channel = incoming_event_channel
        # Websocket host
        self._host = host
        # Websocket port
        self._port = port
        # Websocket stream path
        self._outgoing_websocket_path = outgoing_websocket_path
        # Websocket input path
        self._incoming_websocket_path = incoming_websocket_path

        # Create Websocket server
        self.loop.run_until_complete(
                websockets.serve(
                    functools.partial(RedisWebsocketRelay.relay, self),
                    self.host,
                    self.port))

        logger.info("Created websocket server")

    async def get_pubsub(self, channel):
        """ Actual relay for gameserver events """
        # Connect to the local running redis server
        redis = await aioredis.create_redis(self.redis_uri)

        # Return the pubsub channel
        return (await redis.subscribe(channel))[0]

    async def dead_end_checker(self, ws):
        """ Helper for detecting closed connections """
        while True:
            try:
                pong_waiter = await ws.ping()
                await asyncio.wait_for(pong_waiter, timeout=5)
            except asyncio.TimeoutError:
                # Dead end, return
                break
            except websockets.exceptions.ConnectionClosed:
                # Connection closed
                break

            # Check every 10 seconds
            await asyncio.sleep(10)

    async def game_event_producer(self, ws):
        """ Actual relay for gameserver events """
        # Get the pubsub channel
        pubsub = await self.get_pubsub(self.outgoing_event_channel)

        # Just relay json messages to the ws
        while await pubsub.wait_message():
            msg = (await pubsub.get()).decode()
            try:
                await ws.send(msg)
            except websockets.exceptions.ConnectionClosed:
                break

    async def input_event_consumer(self, ws):
        """ Relays incoming messages to a pubsub channel """
        while True:
            await asyncio.sleep(1000)

    async def relay(self, ws, path):
        """ Most basic real time websocket relay for game events pushed by the
        `game_runner` and receiving user interface input

        :param ws: websocket
        :param path: Connection path
        """
        if path != self.outgoing_websocket_path:
            logger.warning(f"{ws.remote_address} tried to connect to {path}")
        else:
            logger.info(f"{ws.remote_address} connected to {path}")

        logger.debug(f"Client connected to path: {path}")

        logger.debug("Startup game event producer")
        event_producer = self.loop.create_task(
                self.game_event_producer(ws))

        logger.debug("Start input event consumer")
        input_consumer = self.loop.create_task(
                self.input_event_consumer(ws))

        logger.debug("Start input event consumer")
        dead_end_watcher = self.loop.create_task(
                self.dead_end_checker(ws))

        # wait for one of the two to terminate
        done, pending = await asyncio.wait(
            [
                event_producer,
                input_consumer,
                dead_end_watcher
            ],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Terminate the remaining tasks
        for task in pending:
            task.cancel()

        logger.info(f"{ws.remote_address} disconnected")

    @property
    def loop(self):
        """ Eventloop the relay is running on """
        return self._loop

    @property
    def host(self):
        """ IP of the websocket relay """
        return self._host

    @property
    def port(self):
        """ Port of the websocket relay """
        return self._port

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

    @property
    def outgoing_websocket_path(self):
        """ outgoing websocket stream path"""
        return self._outgoing_websocket_path

    @property
    def incoming_websocket_path(self):
        """ incoming websocket stream path"""
        return self._incoming_websocket_path
