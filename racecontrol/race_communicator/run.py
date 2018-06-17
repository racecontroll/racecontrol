import logging
import asyncio
import websockets
from redis_websocket_relay import relay


# Get the logger for this module
log = logging.getLogger("websocket_relay")


def run(host, port):
    """ Starts the websocket server """
    # Create websocket
    asyncio.ensure_future(websockets.serve(relay, host, port))
    log.info("Started websocket relay")
    asyncio.get_event_loop().run_forever()
    log.warning("Terminated websocket relay")


run("0.0.0.0", 8765)
