"""Manage outbound ON command to a device."""
from ... import pub
from .. import status_handler
from .direct_command import DirectCommandHandlerBase
from ...topics import (STATUS_REQUEST, STATUS_REQUEST_ALTERNATE_1,
                       STATUS_REQUEST_ALTERNATE_2, STATUS_REQUEST_ALTERNATE_3)

class StatusRequestCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(address, STATUS_REQUEST)

    #pylint: disable=arguments-differ, useless-super-delegation
    def send(self):
        """Send the ON command."""
        super().send()

    #pylint: disable=arguments-differ, useless-super-delegation
    async def async_send(self):
        """Send the ON command async."""
        return await super().async_send()

    @status_handler
    def handle_response(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Handle the ON response direct ACK."""
        cmd2 = kwargs.get('cmd2')
        if cmd2 is not None:
            self._call_subscribers(status=cmd2)


class StatusRequest1Command(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(address, STATUS_REQUEST_ALTERNATE_1)

    #pylint: disable=arguments-differ, useless-super-delegation
    def send(self):
        """Send the ON command."""
        super().send()

    #pylint: disable=arguments-differ
    async def async_send(self):
        """Send the ON command async."""
        return await super().async_send()

    @status_handler
    def handle_response(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Handle the ON response direct ACK."""
        cmd2 = kwargs.get('cmd2')
        if cmd2 is not None:
            self._call_subscribers(status=cmd2)


class StatusRequest2Command(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(address, STATUS_REQUEST_ALTERNATE_2)

    #pylint: disable=arguments-differ, useless-super-delegation
    def send(self):
        """Send the ON command."""
        super().send()

    #pylint: disable=arguments-differ, useless-super-delegation
    async def async_send(self):
        """Send the ON command async."""
        return await super().async_send()

    @status_handler
    def handle_response(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Handle the ON response direct ACK."""
        cmd2 = kwargs.get('cmd2')
        if cmd2 is not None:
            self._call_subscribers(status=cmd2)


class StatusRequest3Command(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(address, STATUS_REQUEST_ALTERNATE_3)

    #pylint: disable=arguments-differ, useless-super-delegation
    def send(self):
        """Send the ON command."""
        super().send()

    #pylint: disable=arguments-differ
    async def async_send(self):
        """Send the ON command async."""
        return await super().async_send()

    @status_handler
    def handle_response(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Handle the ON response direct ACK."""
        cmd2 = kwargs.get('cmd2')
        if cmd2 is not None:
            self._call_subscribers(status=cmd2)
