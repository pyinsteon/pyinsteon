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
        self._is_dimmable: bool = True

    @property
    def is_dimmable(self) -> bool:
        """Return if the state is dimmable.

        If true, the state can support values 0 - 255.
        If false, the state only supports values 0 and 255.
        """
        return self._is_dimmable

    @is_dimmable.setter
    def is_dimmable(self, value: bool) -> None:
        """Set the dimmable property of the state."""
        self._is_dimmable = bool(value)

    @property
    def value(self):
        """Return the value of the state."""
        return self._value

    @value.setter
    def value(self, value):
        """Set the value of the state."""
        try:
            value = self._type(value) if value is not None else None
            if not self._is_dimmable and value:
                value = 255
            if self._value == value:
                return
            self._value = value

        except TypeError as ex:
            raise TypeError(
                f"Error setting value of State {self._name}: Must be of type {self._type.__name__}"
            ) from ex
        self._call_subscribers(
            name=self._name,
            address=self._address.id,
            value=self._value,
            group=self._group,
        )

    # pylint: disable=arguments-differ
    def set_value(self, on_level: int):
        """Set the value of the state from the handlers."""
        self.value = on_level
