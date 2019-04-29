"""Device state definitions."""
from abc import ABC, abstractmethod


class StateBase(ABC):
    """Device state base class."""

    def __init__(self, name: str, handlers, group=0, default=None, value_type: type = int):
        """Init the StateBase class."""
        self._name = name
        self._group = group
        self._value = int(default) if default is not None else None
        self._type = value_type
        self._subscribers = []
        self._subscribe_handlers(handlers)

    @property
    def name(self):
        """Return the name of the state."""
        return self._name

    @property
    def value(self):
        """Return the value of the state."""
        return self._value

    @value.setter
    def value(self, value):
        """Set the value of the state."""
        try:
            self._value = self._type(value) if value is not None else None
            for subscriber in self._subscribers:
                subscriber(self._name, self._value, self._group)
        except TypeError:
            raise TypeError('Error setting value of State {}: '
                            'Must be of type {}'.format(self._name, self._type.__name__))

    def subscribe(self, callback):
        """Subscribe to state changes."""
        self._subscribers.append(callback)

    @abstractmethod
    def _set_value(self, **kwargs):
        """Set the value of the state from a Handler."""

    def _subscribe_handlers(self, handlers):
        for handler in handlers:
            handler.subscribe(self._set_value)
