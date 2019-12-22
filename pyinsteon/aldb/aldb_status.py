"""ALDB Status representation."""
from enum import Enum


class ALDBStatus(Enum):
    """All-Link Database load status."""

    EMPTY = 0
    LOADING = 1
    LOADED = 2
    FAILED = 3
    PARTIAL = 4
