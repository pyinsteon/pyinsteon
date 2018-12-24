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
        self._messageType = None
        self._extended = None
        self._hopsLeft = None
        self._hopsMax = None

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
        if hasattr(other, 'messageType'):
            is_eq = self._messageType == other.messageType
            is_eq = is_eq and self._extended == other.extended
            return is_eq
        return False

    def __ne__(self, other):
        """Test for not equals."""
        if hasattr(other, 'messageType'):
            return not self.__eq__(other)
        return True

    def matches_pattern(self, other):
        """Test if current message match a patterns or template."""
        if hasattr(other, 'messageType'):
            messageTypeIsEqual = False
            if self.messageType is None or other.messageType is None:
                messageTypeIsEqual = True
            else:
                messageTypeIsEqual = (self.messageType == other.messageType)
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
    def isBroadcast(self):
        """Test if the message is a broadcast message type."""
        return (self._messageType & MESSAGE_TYPE_BROADCAST_MESSAGE ==
                MESSAGE_TYPE_BROADCAST_MESSAGE)

    @property
    def isDirect(self):
        """Test if the message is a direct message type."""
        direct = (self._messageType == 0x00)
        if self.isDirectACK or self.isDirectNAK:
            direct = True
        return direct

    @property
    def isDirectACK(self):
        """Test if the message is a direct ACK message type."""
        return self._messageType == MESSAGE_TYPE_DIRECT_MESSAGE_ACK

    @property
    def isDirectNAK(self):
        """Test if the message is a direct NAK message type."""
        return self._messageType == MESSAGE_TYPE_DIRECT_MESSAGE_NAK

    @property
    def isAllLinkBroadcast(self):
        """Test if the message is an ALl-Link broadcast message type."""
        return self._messageType == MESSAGE_TYPE_ALL_LINK_BROADCAST

    @property
    def isAllLinkCleanup(self):
        """Test if the message is a All-Link cleanup message type."""
        return self._messageType == MESSAGE_TYPE_ALL_LINK_CLEANUP

    @property
    def isAllLinkCleanupACK(self):
        """Test if the message is a All-LInk cleanup ACK message type."""
        return self._messageType == MESSAGE_TYPE_ALL_LINK_CLEANUP_ACK

    @property
    def isAllLinkCleanupNAK(self):
        """Test if the message is a All-Link cleanup NAK message type."""
        return self._messageType == MESSAGE_TYPE_ALL_LINK_CLEANUP_NAK

    @property
    def isExtended(self):
        """Test if the message is an extended message type."""
        return self._extended == 1

    @property
    def hopsLeft(self):
        """Return the number of hops left in message the trasport."""
        return self._hopsLeft

    @property
    def hopsMax(self):
        """Return the maximum number of hops allowed for this message."""
        return self._hopsMax

    @hopsMax.setter
    def hopsMax(self, val):
        """Set the maximum number of hops allowed for this message."""
        self._hopsMax = val

    @property
    def messageType(self):
        """Return the message type."""
        return self._messageType

    @messageType.setter
    def messageType(self, val):
        """Set the message type."""
        if val in range(0, 8):
            self._messageType = val
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
        if isinstance(message_type, MessageType):
            type_bits =  message_type.value
        elif message_type in range(0, 8):
            type_bits = message_type
        else:
            raise ValueError("message_type is not in range 0 - 7")

        ext_bit = 1 if bool(extended) else 0
        hops_left_bits = min(3, max(0, hops_left))
        max_hops_bits = min(3, max(0, max_hops))

        flags = ((type_bits << 5) +
                 (ext_bit << 4) + 
                 (hops_left << 2) +
                 max_hops_bits)

        return MessageFlags(flags)

    @classmethod
    def template(cls, messageType=None, extended=None,
                 hopsleft=None, hopsmax=None):
        """Create message flags template.

        messageType: integter 0 to 7 or None:
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
        if messageType is None:
            flags._messageType = None
        elif messageType < 8:
            flags._messageType = messageType
        else:
            flags._messageType = messageType >> 5
        if extended is None:
            flags._extended = None
        elif extended in [0, 1, True, False]:
            if extended:
                flags._extended = 1
            else:
                flags._extended = 0
        else:
            flags._extended = extended >> 4
        flags._hopsLeft = hopsleft
        flags._hopsMax = hopsmax
        return flags

    @property
    def bytes(self):
        """Return a byte representation of the message flags."""
        flagByte = 0x00
        messageType = 0
        if self._messageType is not None:
            messageType = self._messageType << 5
        extendedBit = 0 if self._extended is None else self._extended << 4
        hopsMax = 0 if self._hopsMax is None else self._hopsMax
        hopsLeft = 0 if self._hopsLeft is None else (self._hopsLeft << 2)
        flagByte = flagByte | messageType | extendedBit | hopsLeft | hopsMax
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
            self._messageType = (flagByte[0] & 0xe0) >> 5
            self._extended = (flagByte[0] & _EXTENDED_MESSAGE) >> 4
            self._hopsLeft = (flagByte[0] & 0x0c) >> 2
            self._hopsMax = flagByte[0] & 0x03
        else:
            self._messageType = None
            self._extended = None
            self._hopsLeft = None
            self._hopsMax = None
