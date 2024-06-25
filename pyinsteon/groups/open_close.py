"""Open / Close sensor groups."""

from ..address import Address
from .group_base import GroupBase


class NormallyOpen(GroupBase):
    """Normally open sensor state."""

    def __init__(
        self,
        name: str,
        address: Address,
        group: int = 0,
        default: int = None,
        status_type: int = 0,
    ):
        """Init the OnLevel class."""
        super().__init__(
            name, address, group, default, value_type=int, status_type=status_type
        )
        self._is_dimmable = False

    # pylint: disable=arguments-differ
    def set_value(self, on_level):
        """Set the value of the state from the handlers."""
        # Off is a Open state and On is an Closed state
        self.value = 0xFF if on_level else 0


class NormallyClosed(GroupBase):
    """Normally closed sensor state."""

    def __init__(
        self,
        name: str,
        address: Address,
        group: int = 0,
        default: int = None,
        status_type: int = 0,
    ):
        """Init the NormallyClosed class."""
        super().__init__(
            name, address, group, default, value_type=int, status_type=status_type
        )
        self._is_dimmable = False
        self._is_reversed = True

    # pylint: disable=arguments-differ
    def set_value(self, on_level):
        """Set the value of the state from the handlers."""
        # Off is a Closed state and On is an Open state
        self.value = 0 if on_level else 0xFF
