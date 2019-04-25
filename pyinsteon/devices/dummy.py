"""Dummy device used for testing."""

from . import Device


class DummyDevice(Device):
    """Dummy device for testing."""

    def _register_default_links(self):
        """Do nothing."""

    def _register_handlers(self):
        """Do nothing."""

    def _register_states(self):
        """Do nothing."""