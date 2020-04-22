"""Base class for all group value entities."""

from abc import ABC, abstractmethod
from ..address import Address
from ..subscriber_base import SubscriberBase


class GroupBase(SubscriberBase):
    """Device group base class."""

    __meta__ = ABC

    def __init__(
        self, name: str, address: Address, group=0, default=None, value_type: type = int
    ):
        """Init the StateBase class."""
        self._address = address
        topic = "state_{}_{}_{}".format(self._address.id, name, group)
        super().__init__(subscriber_topic=topic)
        self._name = name
        self._group = group
        self._value = int(default) if default is not None else None
        self._type = value_type

    @property
    def name(self):
        """Return the name of the state."""
        return self._name

    @property
    def group(self):
        """Return the group number."""
        return self._group

    @property
    def value(self):
        """Return the value of the state."""
        return self._value

    @value.setter
    def value(self, value):
        """Set the value of the state."""
        try:
            value = self._type(value) if value is not None else None
            if self._value == value:
                return
            self._value = value
        except TypeError:
            raise TypeError(
                "Error setting value of State {}: "
                "Must be of type {}".format(self._name, self._type.__name__)
            )
        else:
            self._call_subscribers(
                name=self._name,
                address=self._address.id,
                value=self._value,
                group=self._group,
            )

    @abstractmethod
    def set_value(self, **kwargs):
        """Set the value of the state from a Handler."""
