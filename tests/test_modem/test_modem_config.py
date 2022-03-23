"""Test the modem configuration getting / setting."""
import asyncio
from random import randint
from unittest import TestCase

from pyinsteon.config import AUTO_LED, DEADMAN, DISABLE_AUTO_LINKING, MONITOR_MODE
from pyinsteon.device_types.modem_base import ModemBase
from pyinsteon.topics import GET_IM_CONFIGURATION, SET_IM_CONFIGURATION

from .. import set_log_levels
from ..utils import TopicItem, async_case, send_topics


def random_bool():
    """Generate a random boolean value."""
    return bool(randint(0, 1))


def reset_config(modem, disable_auto_linking, monitor_mode, auto_led, deadman):
    """Reset the modem config to values that are the inverse of the future new_value."""
    modem.configuration[DISABLE_AUTO_LINKING].load(not disable_auto_linking)
    modem.configuration[MONITOR_MODE].load(not monitor_mode)
    modem.configuration[AUTO_LED].load(not auto_led)
    modem.configuration[DEADMAN].load(not deadman)


def set_new_config(modem, disable_auto_linking, monitor_mode, auto_led, deadman):
    """Set the new value of the modem configuration flags."""
    modem.configuration[DISABLE_AUTO_LINKING].new_value = disable_auto_linking
    modem.configuration[MONITOR_MODE].new_value = monitor_mode
    modem.configuration[AUTO_LED].new_value = auto_led
    modem.configuration[DEADMAN].new_value = deadman


class TestModemConfig(TestCase):
    """Test the modem configuration getting / setting."""

    @async_case
    async def test_get_config(self):
        """Test getting the config from the modem."""
        disable_auto_linking = random_bool()
        monitor_mode = random_bool()
        auto_led = random_bool()
        deadman = random_bool()
        topic = f"ack.{GET_IM_CONFIGURATION}"

        topic_item = TopicItem(
            topic,
            {
                "disable_auto_linking": disable_auto_linking,
                "monitor_mode": monitor_mode,
                "auto_led": auto_led,
                "deadman": deadman,
            },
            0,
        )
        modem = ModemBase()
        send_topics([topic_item])
        await asyncio.sleep(0.1)

        assert modem.disable_auto_linking == disable_auto_linking
        assert modem.monitor_mode == monitor_mode
        assert modem.auto_led == auto_led
        assert modem.deadman == deadman

        assert modem.configuration[DISABLE_AUTO_LINKING].value == disable_auto_linking
        assert modem.configuration[MONITOR_MODE].value == monitor_mode
        assert modem.configuration[AUTO_LED].value == auto_led
        assert modem.configuration[DEADMAN].value == deadman

        assert modem.configuration[DISABLE_AUTO_LINKING].new_value is None
        assert modem.configuration[MONITOR_MODE].new_value is None
        assert modem.configuration[AUTO_LED].new_value is None
        assert modem.configuration[DEADMAN].new_value is None

    @async_case
    async def test_set_config(self):
        """Test setting the modem configuration."""
        set_log_levels(logger_topics=True)

        disable_auto_linking = random_bool()
        monitor_mode = random_bool()
        auto_led = random_bool()
        deadman = random_bool()
        topic = f"ack.{SET_IM_CONFIGURATION}"
        topic_item = TopicItem(
            topic,
            {
                "disable_auto_linking": disable_auto_linking,
                "monitor_mode": monitor_mode,
                "auto_led": auto_led,
                "deadman": deadman,
            },
            0.1,
        )

        modem = ModemBase()
        reset_config(modem, disable_auto_linking, monitor_mode, auto_led, deadman)

        send_topics([topic_item])
        await modem.async_set_configuration(
            disable_auto_linking, monitor_mode, auto_led, deadman
        )
        await asyncio.sleep(0.1)

        assert modem.configuration[DISABLE_AUTO_LINKING].value == disable_auto_linking
        assert modem.configuration[MONITOR_MODE].value == monitor_mode
        assert modem.configuration[AUTO_LED].value == auto_led
        assert modem.configuration[DEADMAN].value == deadman

        assert modem.configuration[DISABLE_AUTO_LINKING].new_value is None
        assert modem.configuration[MONITOR_MODE].new_value is None
        assert modem.configuration[AUTO_LED].new_value is None
        assert modem.configuration[DEADMAN].new_value is None

    @async_case
    async def test_set_config_with_std_device_methods(self):
        """Test setting the modem configuration."""
        set_log_levels(logger_topics=True)

        disable_auto_linking = random_bool()
        monitor_mode = random_bool()
        auto_led = random_bool()
        deadman = random_bool()
        topic = f"ack.{SET_IM_CONFIGURATION}"
        topic_item = TopicItem(
            topic,
            {
                "disable_auto_linking": disable_auto_linking,
                "monitor_mode": monitor_mode,
                "auto_led": auto_led,
                "deadman": deadman,
            },
            0.1,
        )

        modem = ModemBase()
        reset_config(modem, disable_auto_linking, monitor_mode, auto_led, deadman)
        set_new_config(modem, disable_auto_linking, monitor_mode, auto_led, deadman)

        send_topics([topic_item])
        await modem.async_write_config()
        await asyncio.sleep(0.1)

        assert modem.configuration[DISABLE_AUTO_LINKING].value == disable_auto_linking
        assert modem.configuration[MONITOR_MODE].value == monitor_mode
        assert modem.configuration[AUTO_LED].value == auto_led
        assert modem.configuration[DEADMAN].value == deadman

        assert modem.configuration[DISABLE_AUTO_LINKING].new_value is None
        assert modem.configuration[MONITOR_MODE].new_value is None
        assert modem.configuration[AUTO_LED].new_value is None
        assert modem.configuration[DEADMAN].new_value is None
