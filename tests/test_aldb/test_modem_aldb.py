"""Test the modem ALDB."""

from unittest import TestCase

from pyinsteon import pub
from pyinsteon.aldb.modem_aldb import ModemALDB
from pyinsteon.topics import ALL_LINK_RECORD_RESPONSE, MODEM

from ..utils import async_case, random_address


class TestModemALDB(TestCase):
    """Test the modem ALDB."""

    @async_case
    async def test_one_modem(self):
        """Test only one modem can receive records."""
        mgr = pub.getDefaultTopicMgr()
        topic = mgr.getTopic(f"{MODEM}.{ALL_LINK_RECORD_RESPONSE}", okIfNone=True)

        # Check if there is already one listner. If there is,
        # then we should still only have one at the end
        if topic:
            listeners = topic.getListeners()
            has_listeners = len(listeners) != 0
        else:
            has_listeners = False

        modem_aldb_1 = ModemALDB(random_address())
        modem_aldb_2 = ModemALDB(random_address())
        if has_listeners:
            assert modem_aldb_1._read_manager is None
        else:
            assert modem_aldb_1._read_manager is not None
        assert modem_aldb_2._read_manager is None

        topic = mgr.getTopic(f"{MODEM}.{ALL_LINK_RECORD_RESPONSE}")
        listeners = topic.getListeners()
        assert len(listeners) == 1
