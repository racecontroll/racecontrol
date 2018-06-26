# -*- coding: utf-8 -*-
"""
    racecontrol.messages
    ~~~~~~~~~~~~~~~~~~~~

    Messages send over the pubsub channel that are registered by the running
    game server

    :author: Matthias Riegler, 2018
    :license: aGPLv3, see LICENSE.md for more details.



*Packets* are send in json format, the MSG_* field should be in the request
field!
"""


# Single events, no other information required
MSG_START = "start"
MSG_PAUSE = "pause"
MSG_RESET = "pause"

# a request should look like:
#       {type, **typeargs}
MSG_TRACK_EVENT = "track"
# lap_finished passes {"track_id": ..., "time"}
MSG_TRACK_EVENT_LAP_FINISHED = "lap_finished"

REDIS_MSG_TYPE_STATE_PUSH = "update_positions"
