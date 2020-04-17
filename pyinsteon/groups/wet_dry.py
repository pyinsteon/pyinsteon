"""Wet / Dry state."""
from .group_base import GroupBase
from ..address import Address


class Dry(GroupBase):
    """Dry state."""

    def __init__(
        self, name: str, address: Address, group: int = 0, default: int = None
    ):
        """Init the WetDry class."""
        super().__init__(name, address, group, default, value_type=bool)

    # pylint: disable=arguments-differ
    def set_value(self, dry):
        """Set the value of the state from the handlers."""
        self.value = bool(dry)


class Wet(GroupBase):
    """Wet state."""

    def __init__(
        self, name: str, address: Address, group: int = 0, default: int = None
    ):
        """Init the WetDry class."""
        super().__init__(name, address, group, default, value_type=bool)

    # pylint: disable=arguments-differ
    def set_value(self, dry):
        """Set the value of the state from the handlers."""
        self.value = not bool(dry)
