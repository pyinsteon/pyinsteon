"""On Leve state."""
import logging

from ..address import Address
from .group_base import GroupBase

_LOGGER = logging.getLogger(__name__)


class OnLevel(GroupBase):
    """Variable On Level state."""

    def __init__(
        self, name: str, address: Address, group: int = 0, default: int = None
    ):
        """Init the OnLevel class."""
        super().__init__(name, address, group, default, value_type=int)

    # pylint: disable=arguments-differ
    def set_value(self, on_level):
        """Set the value of the state from the handlers."""
        self.value = int(on_level) if on_level else 0
