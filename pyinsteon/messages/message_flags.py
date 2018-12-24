"""Message Flags data type."""

import logging
import binascii
from ..constants import MessageFlagType

_LOGGER = logging.getLogger(__name__)
_EXTENDED_MESSAGE = 0x10

class MessageFlags():
    """Message Flags class use in Standard and Extended messages."""

    def __init__(self, flags=0x00):
        """Init the MessageFlags class."""
        self._message_type = None
        self._extended = None
        self._hops_left = None
        self._max_hops = None

        if flags is not None:
            self._set_properties(flags)

    def __repr__(self):
        """Representation of the message flags."""
        return self.hex

    def __str__(self):
        """Return a string representation of message flags."""
        return self.hex

    def __eq__(self, other):
        """Test for equality."""
        if hasattr(other, 'message_type'):
            is_eq = self._message_type == other.message_type
            is_eq = is_eq and self._extended == other.extended
            return is_eq
        return False

    def __ne__(self, other):
        """Test for not equals."""
        if hasattr(other, 'message_type'):
            return not self.__eq__(other)
        return True

    def matches_pattern(self, other):
        """Test if current message match a patterns or template."""
        if hasattr(other, 'message_type'):
            message_typeIsEqual = False
            if self.message_type is None or other.message_type is None:
                messageTypeIsEqual = True
            else:
                message_typeIsEqual = (self.message_type == other.message_type)
            extendedIsEqual = False
            if self.extended is None or other.extended is None:
                extendedIsEqual = True
            else:
                extendedIsEqual = (self.extended == other.extended)
            return messageTypeIsEqual and extendedIsEqual
        else:
            return False

    @classmethod
    def get_properties(cls):
        """Get all properties of the MessageFlags class."""
        property_names = [p for p in dir(cls)
                          if isinstance(getattr(cls, p), property)]
        return property_names

    @property
    def is_broadcast(self):
        """Test if the message is a broadcast message type."""
        return (self._message_type & MessageFlagType.BROADCAST_MESSAGE ==
                MessageFlagType.BROADCAST_MESSAGE)

    @property
    def is_direct(self):
        """Test if the message is a direct message type."""
        direct = (self._message_type == 0x00)
        if self.is_direct_ack or self.is_direct_nak:
            direct = True
        return direct

    @property
    def is_direct_ack(self):
        """Test if the message is a direct ACK message type."""
        return self._message_type == MessageFlagType.DIRECT_MESSAGE_ACK

    @property
    def is_direct_nak(self):
        """Test if the message is a direct NAK message type."""
        return self._message_type == MessageFlagType.DIRECT_MESSAGE_NAK

    @property
    def is_all_link_broadcast(self):
        """Test if the message is an ALl-Link broadcast message type."""
        return self._message_type == MessageFlagType.ALL_LINK_BROADCAST

    @property
    def is_all_link_cleanup(self):
        """Test if the message is a All-Link cleanup message type."""
        return self._message_type == MessageFlagType.ALL_LINK_CLEANUP

    @property
    def is_all_link_cleanup_ack(self):
        """Test if the message is a All-LInk cleanup ACK message type."""
        return self._message_type == MessageFlagType.ALL_LINK_CLEANUP_ACK

    @property
    def is_all_link_cleanup_nak(self):
        """Test if the message is a All-Link cleanup NAK message type."""
        return self._message_type == MessageFlagType.ALL_LINK_CLEANUP_NAK

    @property
    def is_extended(self):
        """Test if the message is an extended message type."""
        return self._extended == 1

    @property
    def hops_left(self):
        """Return the number of hops left in message the trasport."""
        return self._hops_left

    @property
    def max_hops(self):
        """Return the maximum number of hops allowed for this message."""
        return self._max_hops

    @max_hops.setter
    def max_hops(self, val):
        """Set the maximum number of hops allowed for this message."""
        self._max_hops = val

    @property
    def message_type(self):
        """Return the message type."""
        return self._message_type

    @message_type.setter
    def message_type(self, val):
        """Set the message type."""
        if val in range(0, 8):
            self._message_type = val
        else:
            raise ValueError

    @property
    def extended(self):
        """Return the extended flag."""
        return self._extended

    @extended.setter
    def extended(self, val):
        """Set the extended flag."""
        if val in [None, 0, 1]:
            self._extended = val
        else:
            raise ValueError

    @classmethod
    def create(cls, message_flag_type: MessageFlagType, extended:bool=False,
               hops_left:int=0, max_hops:int=0):
        """Create message flags.

        message_flag_type: MessageFlagType 0 to 7:
            DIRECT_MESSAGE = 0
            DIRECT_MESSAGE_ACK = 1
            ALL_LINK_CLEANUP = 2
            ALL_LINK_CLEANUP_ACK = 3
            BROADCAST_MESSAGE = 4
            DIRECT_MESSAGE_NAK = 5
            ALL_LINK_BROADCAST = 6
            ALL_LINK_CLEANUP_NAK = 7
        extended: 1 for extended, 0 for standard
        hops_left: int  0 - 3
        max_hops:  int  0 - 3
        """
        flags = 0
        type_bits = 0
        if isinstance(message_flag_type, MessageFlagType):
            type_bits =  message_flag_type.value
        elif message_flag_type in range(0, 8):
            type_bits = message_flag_type
        else:
            raise ValueError("message_flag_type is not in range 0 - 7")

        ext_bit = 1 if bool(extended) else 0
        hops_left_bits = min(3, max(0, hops_left))
        max_hops_bits = min(3, max(0, max_hops))

        flags = ((type_bits << 5) +
                 (ext_bit << 4) + 
                 (hops_left_bits << 2) +
                 max_hops_bits)

        return MessageFlags(flags)

    @classmethod
    def template(cls, message_type=None, extended=None,
                 hopsleft=None, hopsmax=None):
        """Create message flags template.

        message_type: integter 0 to 7 or None:
            MESSAGE_TYPE_DIRECT_MESSAGE = 0
            MESSAGE_TYPE_DIRECT_MESSAGE_ACK = 1
            MESSAGE_TYPE_ALL_LINK_CLEANUP = 2
            MESSAGE_TYPE_ALL_LINK_CLEANUP_ACK = 3
            MESSAGE_TYPE_BROADCAST_MESSAGE = 4
            MESSAGE_TYPE_DIRECT_MESSAGE_NAK = 5
            MESSAGE_TYPE_ALL_LINK_BROADCAST = 6
            MESSAGE_TYPE_ALL_LINK_CLEANUP_NAK = 7
        extended: 1 for extended, 0 for standard or None
        hopsleft: int  0 - 3
        hopsmax:  int  0 - 3
        """
        flags = MessageFlags(None)
        if message_type is None:
            flags._message_type = None
        elif message_type < 8:
            flags._message_type = message_type
        else:
            flags._message_type = message_type >> 5
        if extended is None:
            flags._extended = None
        elif extended in [0, 1, True, False]:
            if extended:
                flags._extended = 1
            else:
                flags._extended = 0
        else:
            flags._extended = extended >> 4
        flags._hops_left = hopsleft
        flags._max_hops = hopsmax
        return flags

    @property
    def bytes(self):
        """Return a byte representation of the message flags."""
        flagByte = 0x00
        message_type = 0
        if self._message_type is not None:
            message_type = self._message_type << 5
        extendedBit = 0 if self._extended is None else self._extended << 4
        hopsMax = 0 if self._max_hops is None else self._max_hops
        hopsLeft = 0 if self._hops_left is None else (self._hops_left << 2)
        flagByte = flagByte | message_type | extendedBit | hopsLeft | hopsMax
        return bytes([flagByte])

    @property
    def hex(self):
        """Return a hexadecimal representation of the message flags."""
        return binascii.hexlify(self.bytes).decode()

    # pylint: disable=no-self-use
    def _normalize(self, flags):
        """Take any format of flags and turn it into a hex string."""
        norm = None
        if isinstance(flags, MessageFlags):
            norm = flags.bytes
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
            _LOGGER.warning('MessageFlags with unknown type %s: %r',
                            type(flags), flags)
        return norm

    def _set_properties(self, flags):
        """Set the properties of the message flags based on a byte input."""
        flagByte = self._normalize(flags)

        if flagByte is not None:
            self._message_type = (flagByte[0] & 0xe0) >> 5
            self._extended = (flagByte[0] & _EXTENDED_MESSAGE) >> 4
            self._hops_left = (flagByte[0] & 0x0c) >> 2
            self._max_hops = flagByte[0] & 0x03
        else:
            self._message_type = None
            self._extended = None
            self._hops_left = None
            self._max_hops = None
