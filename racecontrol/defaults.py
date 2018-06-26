# -*- coding: utf-8 -*-
"""
    racecontrol.defaults
    ~~~~~~~~~~~~~~~~~~~~

    Default parameters

    :author: Matthias Riegler, 2018
    :license: aGPLv3, see LICENSE.md for more details.
"""


NUM_DRIVERS = 2
REDIS_URI = "redis://localhost"
OUTGOING_EVENT_CHANNEL = "game_events"
INCOMING_EVENT_CHANNEL = "input_events"
WEBSOCKET_STREAM_PATH = "/gamestream"
WEBSOCKET_INPUT_PATH = "/input"
WEBSOCKET_HOST = "0.0.0.0"
WEBSOCKET_PORT = 8765
