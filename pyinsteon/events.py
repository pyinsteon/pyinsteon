"""Event class used to trigger event actions to subscribers.

Events include device triggered actions such as:
    - ON
    - OFF
    - FAST ON
    - FAST OFF

Subscribers to Event use the following interface:
    subscriber(name, address)
Where name is the name of the event and address is the address of the device
triggering the event.
"""
from .subscriber_base import SubscriberBase
from .address import Address

ON_EVENT = 'on_event'
ON_FAST_EVENT = 'on_fast_event'
OFF_EVENT = 'off_event'
OFF_FAST_EVENT = 'off_fast_event'
FAN_ON_EVENT = 'fan_on_event'
FAN_ON_FAST_EVENT = 'fan_on_fast_event'
FAN_OFF_EVENT = 'fan_off_event'
FAN_OFF_FAST_EVENT = 'fan_off_fast_event'


class Event(SubscriberBase):
    """Event class to manage triggering of events.

    Subscribers to Event use the following interface:

        subscriber(name, address)

    Where name is the name of the event and address is the address of the device
    triggering the event.
    """

    def __init__(self, name: str, address: Address, group=0):
        """Init the Event class."""
        super().__init__()
        self._name = name
        self._address = Address(address)
        self._group = group

    def _call_subscribers(self, **kwargs):
        """Call subscribers to the event."""
        super()._call_subscribers(name=self._name, address=self._address, group=self._group)

    def add_handler(self, handler):
        """Add a handler to trigger the event."""
        handler.subscribe(self._call_subscribers)
