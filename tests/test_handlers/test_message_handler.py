"""Example 1 for Chain Of Command."""
import asyncio
import unittest

from pyinsteon.handlers.state_manager import StateManager
from pyinsteon.handlers.message_manager import MessageManager
from pyinsteon.handlers.wait_for_message import WaitForMessage
from pyinsteon.handlers.send_message import SendMessage


class MockModem():
    """Mock modem class."""
    def send(self, msg):
        """Mock send message."""
        print('Sent message: ', msg)


class MockState():
    """Mock state class."""

    def __init__(self):
        """Init the MockState class."""
        self.value = "Unchanged"

    def set_value(self, val):
        """Change the state value."""
        print("Changing state value to ", val)
        self.value = val


class StateUpdater(StateManager):
    """Mock state update manager."""

    async def execute(self, **kwargs):
        """Print the message."""
        msg = kwargs.get('msg')
        print("Updating state from message: ", msg)
        self._state.set_value('Changed')
        await self._run_next(**kwargs)


def setup_custom_handler(manager, state, callback) -> MessageManager:
    """Setup a custom command handler to send a message and get response."""
    mgr = MessageManager(manager, callback)
    state_updater = StateUpdater(mgr, state, None)
    direct_ack = WaitForMessage(mgr, 'direct ack', state_updater)
    msg_ack = WaitForMessage(mgr, 'message ack', direct_ack, timeout=5)
    send_msg = SendMessage(mgr, "Send this message", msg_ack)
    mgr.add_handler(send_msg)
    return mgr


async def run_test():
    """Run example 1 test."""
    mock_state = MockState()
    mock_modem = MockModem()

    def mock_callback(**kwargs):
        """Print the value of the state."""
        print("Mock state: ", mock_state.value)


    # Setup the message handler from the end to the begining
    mgr = setup_custom_handler(mock_modem, mock_state, mock_callback)


    asyncio.ensure_future(mgr.execute())  # This should send the message
    await asyncio.sleep(1)  # Mock wait for message. To force timeout change to >5

    print("Receiving Message ACK")
    mgr.msg_queue.put_nowait('message ack')  # Set the timer to wait for a direct ack
    await asyncio.sleep(1)  # Mock wait for message. To force timeout change to >2

    print("Receiving Direct ACK")
    await mgr.msg_queue.put('direct ack')   # Kick off the StateManager and call mock_callback


class TestMessageHandler(unittest.TestCase):

    def test_message_handler(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(run_test())


if __name__ == "__main__":
    unittest.main()
