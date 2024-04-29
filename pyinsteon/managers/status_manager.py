"""Manage status requests.

Status requests should not run more often than necessary due to the nature of linking the status message response to the original request.
If status messages overlap, the response can be very difficult to associate to the original request. This is especially important for
devices that have multiple status messages.

Logic:
first call always happens when requested
second call happens
    if
        No other call is in progress then run
    else
        if
            Another call is in queue then cancel
        else
            Wait until the first call is done then run

"""

from asyncio import Lock
from logging import DEBUG, getLogger
from typing import Callable, Dict, Union

from ..address import Address
from ..constants import ResponseStatus
from ..handlers.to_device.status_request import StatusRequestCommand
from ..utils import multiple_status

_LOGGER = getLogger(__name__)
_LOGGER.setLevel(DEBUG)


class StatusManager:
    """Status manager."""

    def __init__(self, address: Address):
        """Init the StatusManager class."""
        self._address = Address(address)
        self._status_cmds: Dict[int, StatusRequestCommand] = {}
        self._callbacks: Dict[int, Callable] = {}
        self._call_waiting: bool = False
        self._run_lock = Lock()

    def add_status_type(self, status_type: int, callback_function: Callable):
        """Add a status request type."""
        self.remove_status_type(status_type=status_type)

        status_cmd = StatusRequestCommand(self._address, status_type)
        status_cmd.subscribe(callback_function)
        self._status_cmds[status_type] = status_cmd
        self._callbacks[status_type] = callback_function

    def remove_status_type(self, status_type: int):
        """Remove a status request type and unsubscribe to command responses."""
        status_cmd: StatusRequestCommand = self._status_cmds.get(status_type)
        if status_cmd:
            status_cmd.unsubscribe(self._callbacks[status_type])
            self._callbacks.pop(status_type)
            self._status_cmds.pop(status_type)

    async def async_status(
        self, status_type: Union[int, None] = None
    ) -> ResponseStatus:
        """Send the status request."""
        if self._call_waiting:
            # No need for this call because an existing call is already scheduled
            _LOGGER.debug("No need to run this status request.")
            return ResponseStatus.SUCCESS

        if self._run_lock.locked():
            # This is the second call and needs to wait for the first call to finish
            # Make sure any subsequent calls know there is already a call waiting
            _LOGGER.debug(
                "This status request is waiting for the prior request to finish."
            )
            self._call_waiting = True

        results = []
        if status_type is not None and status_type not in self._status_cmds:
            status_type = None
        status_types = (
            [status_type] if status_type is not None else self._status_cmds.keys()
        )
        async with self._run_lock:
            for curr_status_type in status_types:
                result = await self._async_status(self._status_cmds[curr_status_type])
                results.append(result)
            self._call_waiting = False

        return multiple_status(*results)

    async def _async_status(self, status_cmd: Callable) -> ResponseStatus:
        """Execute the status command."""
        retries = 2
        result = ResponseStatus.UNSENT
        while retries and result not in [
            ResponseStatus.SUCCESS,
            ResponseStatus.DIRECT_NAK_ALDB,
        ]:
            result = await status_cmd.async_send()
            retries -= 1
        return result
