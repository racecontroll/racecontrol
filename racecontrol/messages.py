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

# A message should look like this:
# {
#     "request": (MSG_START|MSG_PAUSE|MSG_RESET|MSG_FINISH|MSG_TRACK_EVENT),
#     "type": e.g. MSG_TRACK_EVENT_LAP_FINISHED
#     ...
# }

MSG_START = "start"
MSG_PAUSE = "pause"
MSG_RESET = "reset"
MSG_FINISH = "finish"
MSG_TRACK_EVENT = "track_event"

# lap_finished passes {"track_id": ..., "time"}
MSG_TRACK_EVENT_LAP_FINISHED = "lap_finished"


# Redis messages
REDIS_MSG_TYPE_STATE_PUSH = "update_positions"
