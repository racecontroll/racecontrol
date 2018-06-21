# -*- coding: utf-8 -*-
"""
    race_communicator.track_communicator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Communicates with the track communicator

    :copyright: (c) 2018 by Matthias Riegler.
    :license: aGPLv3, see LICENSE.md for more details.
"""


import aioredis
import asyncserial

# ======================================================================
#                             Protocol description
#
#           <magic> <trackid> <byte0> <byte1> <byte2> <byte3> <checksum>
#
#       magic     ->  0xbe
#       trackid   ->  0-3 for the tracks
#       byte0-3   ->  round time
#       checksum  ->  xor of <trackid> to <byte3>
#
# ======================================================================
