"""Test creation of all devices."""
import traceback
import unittest

from pyinsteon.device_types.ipdb import IPDB
from tests import _LOGGER
from tests.utils import random_address


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
            except Exception as e:
                cat = None if prod.cat is None else f"{int(prod.cat):02x}"
                subcat = None if prod.subcat is None else f"{int(prod.subcat):02x}"
                _LOGGER.error("Failed with cat %s subcat %s", cat, subcat)
                _LOGGER.error(e)
                _LOGGER.debug(traceback.format_exc())
                failed = True

        if failed:
            assert False
