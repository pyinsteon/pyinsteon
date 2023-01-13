"""Message Flags data type."""

import binascii
import logging

from ..constants import MessageFlagType
from ..utils import test_values_eq

_LOGGER = logging.getLogger(__name__)
_EXTENDED_MESSAGE = 0x10


class MessageFlags:
    """Message Flags class use in Standard and Extended messages."""

    def __init__(self, flags=0x00):
        """Init the MessageFlags class."""
        self._type = None
        self._extended = None
        self._hops_left = None
        self._max_hops = None

        if flags is not None:
            self._set_properties(flags)

    def __repr__(self):
        """Representation of the message flags."""
        int_self = int.from_bytes(bytes(self), byteorder="big")
        return f"0x{int_self:02x}"

    def __str__(self):
        """Return a hexadecimal representation of the message flags."""
        start = "{"
        end = "}"
        val = f"{start}'message_type': '{str(self._type)}', 'extended': {self._extended}, 'hops_left': {self._hops_left}, 'max_hops': {self._max_hops}{end}"
        return val

    def __bytes__(self):
        """Return a byte representation of the message flags."""
        message_type = (self._type.value << 5) if self._type else 0
        extended_bit = (1 << 4) if self._extended else 0
        hops_left = (self._hops_left << 2) if self._hops_left else 0
        hops_max = self._max_hops if self._max_hops else 0
        flag_byte = message_type | extended_bit | hops_left | hops_max
        return bytes([flag_byte])

    def __eq__(self, other):
        """Test for equality.

        Test only message type and extended bit. Ignore hops remaining and
        max hops.
        """
        if not isinstance(other, MessageFlags):
            return False

        match = True
        match = match & test_values_eq(self.message_type, other.message_type)
        match = match & test_values_eq(self.extended, other.extended)
        return match

    def __ne__(self, other):
        """Test for inequality.

        Test only message type and extended bit. Ignore hops remaining and
        max hops.
        """
        return not self.__eq__(other)

    def __hash__(self):
        """Represent the MessageFlags object as a hash."""
        return hash(bytes(self))

    @property
    def message_type(self) -> MessageFlagType:
        """Return the message type."""
        return self._type

    @message_type.setter
    def message_type(self, val: MessageFlagType):
        """Set the message type."""
        if isinstance(val, MessageFlagType) or val is None:
            self._type = val
        elif val in range(0, 8):
            self._type = MessageFlagType(val)
        else:
            raise ValueError("message_type property must be a MessageFlagType.")

    @property
    def hops_left(self) -> int:
        """Return the number of hops left in message the trasport."""
        return self._hops_left

    @hops_left.setter
    def hops_left(self, val: int):
        """Set the number of hops left for this message."""
        if isinstance(val, int):
            val_int = val
        elif isinstance(val, bytes):
            val_int = int.from_bytes(val, byteorder="big")
        elif val is None:
            self._hops_left = val
            return
        else:
            raise ValueError("hops_left property must be 0-3 or None")
        self._hops_left = min(3, max(val_int, 0))

    @property
    def max_hops(self) -> int:
        """Return the maximum number of hops allowed for this message."""
        return self._max_hops

    @max_hops.setter
    def max_hops(self, val: int):
        """Set the maximum number of hops allowed for this message."""
        if isinstance(val, int):
            val_int = val
        elif isinstance(val, bytes):
            val_int = int.from_bytes(val, byteorder="big")
        elif val is None:
            self._max_hops = val
            return
        else:
            raise ValueError("max_hops property must be 0-3 or None")
        self._max_hops = min(3, max(val_int, 0))

    @property
    def extended(self) -> MessageFlagType:
        """Return the extended flag."""
        return self._extended

    @extended.setter
    def extended(self, val: bool):
        """Set the extended flag."""
        if val in [None, True, False]:
            self._extended = val
        else:
            try:
                self._extended = bool(val)
            except TypeError as ex:
                raise ValueError(
                    "extended property must be True, False or None."
                ) from ex

    @property
    def is_broadcast(self) -> bool:
        """Test if the message is a broadcast message type."""
        return self._type == MessageFlagType.BROADCAST

    @property
    def is_direct(self) -> bool:
        """Test if the message is a direct message type."""
        direct = self._type == MessageFlagType.DIRECT
        if self.is_direct_ack or self.is_direct_nak:
            direct = True
        return direct

    @property
    def is_direct_ack(self) -> bool:
        """Test if the message is a direct ACK message type."""
        return self._type == MessageFlagType.DIRECT_ACK

    @property
    def is_direct_nak(self) -> bool:
        """Test if the message is a direct NAK message type."""
        return self._type == MessageFlagType.DIRECT_NAK

    @property
    def is_all_link_broadcast(self) -> bool:
        """Test if the message is an ALl-Link broadcast message type."""
        return self._type == MessageFlagType.ALL_LINK_BROADCAST

    @property
    def is_all_link_cleanup(self) -> bool:
        """Test if the message is a All-Link cleanup message type."""
        return self._type == MessageFlagType.ALL_LINK_CLEANUP

    @property
    def is_all_link_cleanup_ack(self) -> bool:
        """Test if the message is a All-LInk cleanup ACK message type."""
        return self._type == MessageFlagType.ALL_LINK_CLEANUP_ACK

    @property
    def is_all_link_cleanup_nak(self) -> bool:
        """Test if the message is a All-Link cleanup NAK message type."""
        return self._type == MessageFlagType.ALL_LINK_CLEANUP_NAK

    @property
    def is_extended(self) -> bool:
        """Test if the message is an extended message type."""
        return self._extended == 1

    # pylint: disable=no-self-use
    def _normalize(self, flags) -> bytes:
        """Take any format of flags and turn it into a hex string."""
        norm = None
        if isinstance(flags, MessageFlags):
            norm = bytes(flags)
        elif isinstance(flags, bytearray):
            norm = binascii.hexlify(flags)
        elif isinstance(flags, int):
            norm = bytes([flags])
        elif isinstance(flags, bytes):
            norm = binascii.hexlify(flags)
        elif isinstance(flags, str):
            flags = flags[0:2]
            norm = binascii.hexlify(binascii.unhexlify(flags.lower()))
        elif flags is None:
            norm = None
        else:
            _LOGGER.warning("MessageFlags with unknown type %s: %r", type(flags), flags)
        return norm

    def _set_properties(self, flags):
        """Set the properties of the message flags based on a byte input."""
        flag_byte = self._normalize(flags)

        if flag_byte is not None:
            self._type = MessageFlagType((flag_byte[0] & 0xE0) >> 5)
            self._extended = (flag_byte[0] & _EXTENDED_MESSAGE) >> 4
            self._hops_left = (flag_byte[0] & 0x0C) >> 2
            self._max_hops = flag_byte[0] & 0x03
        else:
            self._type = None
            self._extended = None
            self._hops_left = None
            self._max_hops = None

    @classmethod
    def create(
        cls,
        message_flag_type: MessageFlagType,
        extended: bool = False,
        hops_left: int = 0,
        max_hops: int = 0,
    ):
        """Create message flags.

        message_flag_type: MessageFlagType 0 to 7:
            DIRECT = 0
            DIRECT_ACK = 1
            ALL_LINK_CLEANUP = 2
            ALL_LINK_CLEANUP_ACK = 3
            BROADCAST = 4
            DIRECT_NAK = 5
            ALL_LINK_BROADCAST = 6
            ALL_LINK_CLEANUP_NAK = 7
        extended: True for extended, False for standard
        hops_left: int  0 - 3
        max_hops:  int  0 - 3
        """
        flags = cls(0x00)
        flags.message_type = message_flag_type
        flags.extended = extended
        flags.hops_left = hops_left
        flags.max_hops = max_hops
        return flags
