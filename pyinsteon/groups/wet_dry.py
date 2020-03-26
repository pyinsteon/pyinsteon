"""Wet / Dry state."""
from .group_base import GroupBase
from ..address import Address


class WetDry(GroupBase):
    """Wet / Dry state."""

    def __init__(
        self, name: str, address: Address, group: int = 0, default: int = None
    ):
        """Init the WetDry class."""
        super().__init__(name, address, group, default, value_type=bool)

    # pylint: disable=arguments-differ
    def set_value(self, wet):
        """Set the value of the state from the handlers."""
        self.value = bool(wet)
