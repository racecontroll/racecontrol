# -*- coding: utf-8 -*-
"""
    racecontrol.__main__
    ~~~~~~~~~~~~~~

    Magic happens here!

    :copyright: (c) 2018 by Matthias Riegler.
    :license: LGPLv3, see LICENSE.md for more details.
"""


import asyncio
import logging
import multiprocessing as mp
from .comm import RedisWebsocketRelay
from .game import Race
from .webui import create_app


# Setup logging to debug mode for now!
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
        app = create_app()
        app.run()

    return mp.Process(target=serve)


def entrypoint():
    """ Entry point for racecontrol, all tasks get started here """
    loop = asyncio.get_event_loop()

    _create_redis_websocket_relay(loop)
    _create_race(loop)
    webui_task = _create_webui_task()

    logging.info("Starting racecontrol!")
    try:
        webui_task.start()
        loop.run_forever()

    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt, Shutting down!")

    except Exception as e:
        logging.error(e)

    finally:
        webui_task.terminate()
        loop.close()


# Call main
if __name__ == "__main__":
    entrypoint()
