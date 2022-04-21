"""Patch for 3.7 where AsyncMock does not exist."""
from unittest.mock import MagicMock


class AsyncMock(MagicMock):
    """Patch for 3.7 where AsyncMock does not exist."""

    def __init__(self, *arg, **kwarg):
        """Init the AsyncMock class."""
        pass
