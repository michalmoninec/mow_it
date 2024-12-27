"""
This script defines enums used in the Flask application.
"""

from enum import Enum


class Status(Enum):
    INIT = "init"
    JOIN_WAIT = "join_wait"
    READY = "ready"
    FINISHED = "finished"
