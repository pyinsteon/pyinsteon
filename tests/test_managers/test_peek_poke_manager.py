"""Test the peek poke manager."""
import asyncio
import random
import unittest

from pyinsteon.managers.peek_poke_manager import PeekPokeManager
from pyinsteon.topics import PEEK, POKE, SET_ADDRESS_MSB

from .. import set_log_levels
from ..utils import TopicItem, async_case, cmd_kwargs, random_address, send_topics


class TestPeekPokeManager(unittest.TestCase):
    """Test the PeekPokeManager class."""

    def setUp(self) -> None:
        """Set up the logging."""
        set_log_levels(logger_topics=True)

    @async_case
    async def test_peek(self):
        """Test the peek command."""
        orig_value = random.randint(0, 255)
        response_recieved = False

        def get_peek_value(mem_addr, value):
            nonlocal response_recieved
            assert value == orig_value
            response_recieved = True

        addr = random_address()
        mem_addr = 0x0FFF
        mgr = PeekPokeManager(addr)
        mgr.subscribe_peek(get_peek_value)

        set_msb_ack_topic = f"{addr.id}.ack.{SET_ADDRESS_MSB}.direct"
        set_msb_dir_ack_topic = f"{addr.id}.{SET_ADDRESS_MSB}.direct_ack"
        peek_ack_topic = f"{addr.id}.ack.{PEEK}.direct"
        peek_dir_ack_topic = f"{addr.id}.{PEEK}.direct_ack"

        set_msb_ack_item = TopicItem(
            set_msb_ack_topic,
            cmd_kwargs(0x28, mem_addr >> 8, None),
            0.1,
        )
        set_msb_dir_ack_item = TopicItem(
            set_msb_dir_ack_topic,
            cmd_kwargs(0x28, mem_addr >> 8, None, "00.00.00"),
            0.1,
        )
        peek_ack_item = TopicItem(
            peek_ack_topic, cmd_kwargs(0x2B, orig_value, None), 0.3
        )
        peek_dir_ack_item = TopicItem(
            peek_dir_ack_topic, cmd_kwargs(0x2B, orig_value, None, "00.00.00"), 0.1
        )
        send_topics(
            [set_msb_ack_item, set_msb_dir_ack_item, peek_ack_item, peek_dir_ack_item]
        )
        result = await mgr.async_peek(mem_addr=mem_addr)
        await asyncio.sleep(3)
        assert result == 0x01
        await asyncio.sleep(0.1)
        assert response_recieved

    @async_case
    async def test_poke(self):
        """Test the poke command."""
        orig_value = random.randint(0, 255)
        new_value = random.randint(0, 255)
        poke_response_recieved = False

        def get_poke_value(mem_addr, value):
            nonlocal poke_response_recieved
            assert value == new_value
            poke_response_recieved = True

        addr = random_address()
        mem_addr = 0x0FFF
        mgr = PeekPokeManager(addr)
        mgr.subscribe_poke(get_poke_value)

        set_msb_ack_topic = f"{addr.id}.ack.{SET_ADDRESS_MSB}.direct"
        set_msb_dir_ack_topic = f"{addr.id}.{SET_ADDRESS_MSB}.direct_ack"
        peek_ack_topic = f"{addr.id}.ack.{PEEK}.direct"
        peek_dir_ack_topic = f"{addr.id}.{PEEK}.direct_ack"
        poke_ack_topic = f"{addr.id}.ack.{POKE}.direct"
        poke_dir_ack_topic = f"{addr.id}.{POKE}.direct_ack"

        set_msb_ack_item = TopicItem(
            set_msb_ack_topic,
            cmd_kwargs(0x28, mem_addr >> 8, None),
            0.1,
        )
        set_msb_dir_ack_item = TopicItem(
            set_msb_dir_ack_topic,
            cmd_kwargs(0x28, mem_addr >> 8, None, "00.00.00"),
            0.1,
        )
        peek_ack_item = TopicItem(
            peek_ack_topic, cmd_kwargs(0x2B, orig_value, None), 0.3
        )
        peek_dir_ack_item = TopicItem(
            peek_dir_ack_topic, cmd_kwargs(0x2B, orig_value, None, "00.00.00"), 0.1
        )
        poke_ack_item = TopicItem(
            poke_ack_topic, cmd_kwargs(0x29, new_value, None), 0.6
        )
        poke_dir_ack_item = TopicItem(
            poke_dir_ack_topic, cmd_kwargs(0x29, new_value, None, "00.00.00"), 0.1
        )

        send_topics(
            [
                set_msb_ack_item,
                set_msb_dir_ack_item,
                peek_ack_item,
                peek_dir_ack_item,
                poke_ack_item,
                poke_dir_ack_item,
            ]
        )
        result = await mgr.async_poke(mem_addr=mem_addr, value=new_value)
        await asyncio.sleep(0.1)
        assert result == 0x01
        assert poke_response_recieved
