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


class Event(SubscriberBase):
    """Event class to manage triggering of events.

    Subscribers to Event use the following interface:

        subscriber(name, address)

    Where name is the name of the event and address is the address of the device
    triggering the event.
    """

    def __init__(self, name: str, address: Address, handlers: list, group=0):
        """Init the Event class."""
        super().__init__()
        self._name = name
        self._address = Address(address)
        self._group = group

    def _call_subscribers(self, **kwargs):
        """Call subscribers to the event."""
        super()._call_subscribers(name=self._name, address=self._address, group=self._group)
