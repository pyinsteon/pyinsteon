"""Test creation of all devices."""
import unittest
import traceback

from pyinsteon.device_types.ipdb import IPDB
from tests.utils import random_address
from tests import _LOGGER


class TestCreateDevices(unittest.TestCase):
    """Test creation of all devices."""

    def test_create_devices(self):
        """Test device creation."""

        ipdb = IPDB()
        failed = False
        for prod in ipdb:
            addr = random_address()
            try:
                prod.deviceclass(
                    address=addr,
                    cat=prod.cat,
                    subcat=prod.subcat,
                    description=prod.description,
                    model=prod.model,
                )
            # pylint: disable=broad-except
            except Exception:
                _LOGGER.error("Failed with cat %02x subcat %02x", prod.cat, prod.subcat)
                _LOGGER.debug(traceback.format_exc())
                failed = True

        if failed:
            assert False
