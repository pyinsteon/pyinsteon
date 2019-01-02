"""Message Flags data type."""

import logging
import binascii
from ..constants import MessageFlagType
from ..utils import set_bit


_LOGGER = logging.getLogger(__name__)
_EXTENDED_MESSAGE = 0x10


def create(message_flag_type: MessageFlagType, extended:bool=False,
           hops_left:int=0, max_hops:int=0):
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



def create_template(message_type=None, extended=None,
                    hopsleft=None, hopsmax=None):
    """Create message flags template.

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
    flags = MessageFlags(None)
    if message_type is None:
        flags.message_type = None
    elif message_type < 8:
        flags.message_type = MessageFlagType(message_type)
    elif (message_type & 0xe0) in [0xe0, 0xc0, 0xa0, 0x80,
                                   0x60, 0x40, 0x20, 0x00]:
        flags.message_type = MessageFlagType(message_type >> 5)
    else:
        raise ValueError('message_type must be a MessageFlagType or in [1:7]')
    if extended is None:
        flags._extended = None
    elif bool(extended):
        flags.extended = 1
    else:
        flags.extended = 0
    flags.hops_left = hopsleft
    flags.max_hops = hopsmax
    return flags


class MessageFlags():
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
        val = {'message_type': self._type,
               'extended': str(self._extended),
               'hop_left': self._hops_left,
               'max_hops': self._max_hops}
        return str(val)

    def __str__(self):
        """Return a hexadecimal representation of the message flags."""
        return binascii.hexlify(bytes(self)).decode()

    def __bytes__(self):
        """Return a byte representation of the message flags."""
        message_type = (self._type.value << 5) if self._type else 0
        extendedBit = (1 << 4) if self._extended else 0
        hopsLeft = (self._hops_left << 2) if self._hops_left else 0
        hopsMax = self._max_hops if self._max_hops else 0
        flagByte = message_type | extendedBit | hopsLeft | hopsMax
        return bytes([flagByte])

    def __eq__(self, other):
        """Test for equality.
        
        Test only message type and extended bit. Ignore hops remaining and
        max hops.
        """
        if isinstance(other, MessageFlags):
            if (self.message_type is None or other.message_type is None or
                self.message_type == other.message_type):
                messageTypeIsEqual = True
            else:
                messageTypeIsEqual = False
            if (self.extended is None or other.extended is None or
                self.extended == other.extended):
                extendedIsEqual = True
            else:
                extendedIsEqual = False
            return messageTypeIsEqual and extendedIsEqual
        return False

    def __ne__(self, other):
        """Test for inequality.
        
        Test only message type and extended bit. Ignore hops remaining and
        max hops.
        """
        if hasattr(other, 'message_type'):
            return not self.__eq__(other)
        return True

    @property
    def message_type(self):
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
    def hops_left(self):
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
            raise ValueError('hops_left property must be 0-3 or None')
        self._hops_left = min(3, max(val_int, 0))

    @property
    def max_hops(self):
        """Return the maximum number of hops allowed for this message."""
        return self._max_hops

    @max_hops.setter
    def max_hops(self, val: int):
        """Set the maximum number of hops allowed for this message."""
        """Set the number of hops left for this message."""
        if isinstance(val, int):
            val_int = val
        elif isinstance(val, bytes):
            val_int = int.from_bytes(val, byteorder="big")
        elif val is None:
            self._max_hops = val
            return
        else:
            raise ValueError('max_hops property must be 0-3 or None')
        self._max_hops = min(3, max(val_int, 0))

    @property
    def extended(self):
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
            except TypeError:
                raise ValueError('extended property must be True, False or None.')

    @property
    def is_broadcast(self):
        """Test if the message is a broadcast message type."""
        return self._type == MessageFlagType.BROADCAST
    @property
    def is_direct(self):
        """Test if the message is a direct message type."""
        direct = (self._type == MessageFlagType.DIRECT)
        if self.is_direct_ack or self.is_direct_nak:
            direct = True
        return direct

    @property
    def is_direct_ack(self):
        """Test if the message is a direct ACK message type."""
        return self._type == MessageFlagType.DIRECT_ACK

    @property
    def is_direct_nak(self):
        """Test if the message is a direct NAK message type."""
        return self._type == MessageFlagType.DIRECT_NAK

    @property
    def is_all_link_broadcast(self):
        """Test if the message is an ALl-Link broadcast message type."""
        return self._type == MessageFlagType.ALL_LINK_BROADCAST

    @property
    def is_all_link_cleanup(self):
        """Test if the message is a All-Link cleanup message type."""
        return self._type == MessageFlagType.ALL_LINK_CLEANUP

    @property
    def is_all_link_cleanup_ack(self):
        """Test if the message is a All-LInk cleanup ACK message type."""
        return self._type == MessageFlagType.ALL_LINK_CLEANUP_ACK

    @property
    def is_all_link_cleanup_nak(self):
        """Test if the message is a All-Link cleanup NAK message type."""
        return self._type == MessageFlagType.ALL_LINK_CLEANUP_NAK

    @property
    def is_extended(self):
        """Test if the message is an extended message type."""
        return self._extended == 1

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
            self._type = MessageFlagType((flagByte[0] & 0xe0) >> 5)
            self._extended = (flagByte[0] & _EXTENDED_MESSAGE) >> 4
            self._hops_left = (flagByte[0] & 0x0c) >> 2
            self._max_hops = flagByte[0] & 0x03
        else:
            self._type = None
            self._extended = None
            self._hops_left = None
            self._max_hops = None
