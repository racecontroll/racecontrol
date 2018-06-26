# -*- coding: utf-8 -*-
"""
    racecontrol.__main__
    ~~~~~~~~~~~~~~~~~~~~

    Magic happens here!

    :author: Matthias Riegler, 2018
    :license: aGPLv3, see LICENSE.md for more details.
"""


import asyncio
try:
    # Try to import uvloop, provides _MUCH_ better performance compared to the
    # standart epoll based event loop
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    # No uvloop installed on the system; the default eventloop works as well!
    pass
import logging
import multiprocessing as mp
from .comm import RedisWebsocketRelay
from .game import Race
from .webui import create_app, db


logger = logging.getLogger(__name__)

# Setup logging to debug mode for now!
# @TODO
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)


def _create_redis_websocket_relay(loop):
    """ Creates the Redis <-> Websocket relay tasks """
    # We are fine with the default ports!
    ws_relay = RedisWebsocketRelay(loop=loop)
    return ws_relay


def _create_race(loop):
    """ Creats the Race """
    race = Race(loop, num_drivers=2)
    return race


def _create_webui_task():
    """ Creats the task for the web based user interface """
    def serve():
        webui = create_app()

        # @TODO only do one
        with webui.app_context():
            db.create_all()

        # @TODO use wsgi backend
        webui.run(host="0.0.0.0",
                  port=5000,
                  debug=True,
                  use_reloader=False,
                  use_debugger=False)

    return mp.Process(target=serve)


def entrypoint():
    """ Entry point for racecontrol, all tasks get started here """
    loop = asyncio.get_event_loop()

    logger.info("Setting up tasks")

    _create_redis_websocket_relay(loop)
    _create_race(loop)
    webui_task = _create_webui_task()

    logger.info("Starting racecontrol")
    try:
        webui_task.start()
        loop.run_forever()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, Shutting down!")

    except Exception as e:
        logger.error(e)

    finally:
        logger.info("Killing webui thread")
        webui_task.terminate()  # @TODO clean shutdown of the webui
        logger.info("Stopping event loop")
        loop.stop()
        # loop.close()


# Call main
if __name__ == "__main__":
    entrypoint()
