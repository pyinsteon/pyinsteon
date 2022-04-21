"""Test the on_level command handler."""
import asyncio
import unittest

from pyinsteon.handlers.to_device.status_request import StatusRequestCommand
from tests import set_log_levels
from tests.utils import TopicItem, async_case, random_address, send_topics


class TestStatusRequest(unittest.TestCase):
    """Test the id_request command handler."""

    def setUp(self):
        """Set up the test."""
        self._address = random_address()
        self._db_version = None
        self._status = None
        self._db_version_1 = None
        self._status_1 = None
        self.ack_topic = f"ack.{self._address.id}.status_request.direct"
        self.direct_ack_topic = f"{self._address.id}.any_topic.direct_ack"
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    def set_status(self, db_version, status):
        """Handle callback to on_level direct_ack."""
        self._db_version = db_version
        self._status = status

    def set_status_1(self, db_version, status):
        """Handle callback to on_level direct_ack."""
        self._db_version_1 = db_version
        self._status_1 = status

    @async_case
    async def test_status_command(self):
        """Test Status Request command."""
        self.status_command = StatusRequestCommand(self._address, status_type=0)
        self.status_command.subscribe(self.set_status)
        cmd1 = 0x19
        cmd2 = 0x00
        db_version = 0x22
        status = 0x33
        topics = [
            TopicItem(
                self.ack_topic,
                {"cmd1": cmd1, "cmd2": cmd2, "user_data": None},
                0.5,
            ),
            TopicItem(
                self.direct_ack_topic,
                {
                    "cmd1": db_version,
                    "cmd2": status,
                    "target": "112233",
                    "user_data": None,
                    "hops_left": 3,
                },
                0.5,
            ),
        ]
        send_topics(topics)
        assert await self.status_command.async_send()
        await asyncio.sleep(1)
        assert self._db_version == db_version
        assert self._status == status

    @async_case
    async def test_status_request_hub(self):
        """Test a status request coming from the Hub.

        This starts with an ACK message rather than a send() command.
        """
        self.status_command = StatusRequestCommand(self._address, status_type=0)
        self.status_command.subscribe(self.set_status)
        cmd1 = 0x19
        cmd2 = 0x00
        db_version = 0x44
        status = 0x55
        topics = [
            TopicItem(
                self.ack_topic,
                {"cmd1": cmd1, "cmd2": cmd2, "user_data": None},
                0.1,
            ),
            TopicItem(
                self.direct_ack_topic,
                {
                    "cmd1": db_version,
                    "cmd2": status,
                    "target": "aabbcc",
                    "user_data": None,
                    "hops_left": 3,
                },
                0.2,
            ),
        ]
        send_topics(topics)
        await asyncio.sleep(0.5)
        assert self._db_version == db_version
        assert self._status == status

    @async_case
    async def test_other_status(self):
        """Test other status command and confirm first handler does not handle."""
        self.status_command = StatusRequestCommand(self._address, status_type=0)
        self.status_command.subscribe(self.set_status)
        status_type = 1
        status_1_command = StatusRequestCommand(self._address, status_type=status_type)
        status_1_command.subscribe(self.set_status_1)
        cmd1 = 0x19
        cmd2 = 0x01
        db_version = 0x66
        status = 0x77
        topics = [
            TopicItem(
                self.ack_topic,
                {"cmd1": cmd1, "cmd2": cmd2, "user_data": None},
                0.1,
            ),
            TopicItem(
                self.direct_ack_topic,
                {
                    "cmd1": db_version,
                    "cmd2": status,
                    "target": "112233",
                    "user_data": None,
                    "hops_left": 3,
                },
                0.1,
            ),
        ]
        self.set_status(-1, -1)
        self.set_status_1(-2, -2)
        send_topics(topics)
        assert await status_1_command.async_send()

        assert self._db_version_1 == db_version
        assert self._status_1 == status

        # Confirm status 1 did not respond.
        assert self._status == -1
        assert self._db_version == -1


if __name__ == "__main__":
    unittest.main()
