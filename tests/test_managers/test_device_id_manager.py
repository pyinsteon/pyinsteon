"""Test the device manager."""
import asyncio
import unittest

from pyinsteon.address import Address
from pyinsteon.managers.device_id_manager import DeviceIdManager
from pyinsteon.topics import ASSIGN_TO_ALL_LINK_GROUP, ID_REQUEST, OFF
from tests.utils import TopicItem, async_case, cmd_kwargs, send_topics


class TestDeviceIdManager(unittest.TestCase):
    """Test device ID manager."""

    def setUp(self):
        """Set up the test."""
        self._test_response = None
        self._modem_address = Address("4d5e6f")
        self._cat = 0x01
        self._subcat = 0x02
        self._firmware = 0x03
        self._target = Address(bytearray([self._cat, self._subcat, self._firmware]))

    def _set_topics(self, address):
        off = "{}.{}.broadcast".format(address.id, OFF)
        ack = "ack.{}.{}.direct".format(address.id, ID_REQUEST)
        dir_ack = "{}.{}.direct_ack".format(address.id, ID_REQUEST)
        response = "{}.{}.broadcast".format(address.id, ASSIGN_TO_ALL_LINK_GROUP)
        return (off, ack, dir_ack, response)

    def _callback(self, *args, **kwargs):
        self._test_response = True

    @async_case
    async def test_id_awake_device(self):
        """Test an awake device is recognized."""
        self._id_mgr = DeviceIdManager()
        address = Address("010101")
        off, ack, dir_ack, response = self._set_topics(address)
        topic_item_1 = TopicItem(
            off, cmd_kwargs(0x10, 0x00, None, Address("000001")), 1
        )
        topic_item_2 = TopicItem(ack, cmd_kwargs(0x10, 0x00, None, None), 0.5)
        topic_item_3 = TopicItem(
            dir_ack, cmd_kwargs(0x10, 0x00, None, self._modem_address, None, 3), 0.5
        )
        topic_item_4 = TopicItem(
            response, cmd_kwargs(0x10, 0x12, None, self._target, None, 3), 0.5
        )
        topic_data = [topic_item_1, topic_item_2, topic_item_3, topic_item_4]

        self._id_mgr.start()
        self._id_mgr.append(address)
        send_topics(topic_data)
        await asyncio.sleep(3.5)
        device_id = self._id_mgr[address]
        assert device_id.cat == self._cat
        self._id_mgr.close()
        await asyncio.sleep(0.1)

    @async_case
    async def test_append(self):
        """Test appending an address to the list of devices to ID."""
        self._id_mgr = DeviceIdManager()
        address = Address("020202")
        self._id_mgr.append(address)
        assert self._id_mgr[address] is not None
        assert self._id_mgr[address].cat is None

    @async_case
    async def test_set_device_id(self):
        """Test setting the device ID."""
        self._id_mgr = DeviceIdManager()
        address = Address("030303")
        self._id_mgr.set_device_id(address, self._cat, self._subcat, self._firmware)
        assert self._id_mgr[address].cat == self._cat
        assert self._id_mgr[address].subcat == self._subcat
        assert self._id_mgr[address].firmware == self._firmware

    @async_case
    async def test_id_device(self):
        """Test device identification."""
        self._id_mgr = DeviceIdManager()
        address = Address("040404")
        _, ack, dir_ack, response = self._set_topics(address)
        topic_item_1 = TopicItem(ack, cmd_kwargs(0x10, 0x00, None, None), 1)
        topic_item_2 = TopicItem(
            dir_ack, cmd_kwargs(0x10, 0x00, None, self._modem_address), 0.5
        )
        topic_item_3 = TopicItem(
            response, cmd_kwargs(0x10, 0x12, None, self._target), 0.5
        )
        topic_data = [topic_item_1, topic_item_2, topic_item_3]

        send_topics(topic_data)
        device_id = await self._id_mgr.async_id_device(address)
        assert device_id.cat == self._cat


if __name__ == "__main__":
    unittest.main()
