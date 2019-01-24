"""Extended Message User Data Type."""
import logging
import binascii

_LOGGER = logging.getLogger(__name__)


def create_empty(val=0x00):
    """Create an empty Userdata object.

    val: value to fill the empty user data fields with (default is 0x00)
    """
    user_data_dict = {}
    for i in range(1, 15):
        key = 'd{}'.format(i)
        user_data_dict.update({key: val})
    return user_data_dict


def _dict_to_dict(empty, user_data):
    if isinstance(user_data, dict):
        for key in user_data:
            if key in ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7',
                       'd8', 'd9', 'd10', 'd11', 'd12', 'd13', 'd14']:
                empty[key] = user_data[key]
    return empty


def _bytes_to_dict(empty, user_data):
    if len(user_data) == 14:
        for i in range(1, 15):
            key = 'd{}'.format(i)
            empty[key] = user_data[i - 1]
    else:
        raise ValueError
    return empty


def _normalize(empty, user_data):
    """Return normalized user data as a dictionary.

    empty: an empty dictionary
    user_data: data in the form of Userdata, dict or None
    """
    if isinstance(user_data, UserData):
        return user_data.to_dict()
    if isinstance(user_data, dict):
        return _dict_to_dict(empty, user_data)
    if isinstance(user_data, (bytes, bytearray)):
        return _bytes_to_dict(empty, user_data)
    if user_data is None:
        return empty
    raise ValueError


class UserData():
    """Extended Message User Data Type."""

    def __init__(self, user_data=bytearray(bytes(14))):
        """Init the Userdata Class."""
        self._user_data = _normalize(create_empty(0x00), user_data)

    def __len__(self):
        """Init Userdata Class."""
        return len(self._user_data)

    def __iter__(self):
        """Iterate through the user data bytes."""
        for itm in self._user_data:
            yield itm

    def __getitem__(self, key):
        """Return a single byte of the user data."""
        return self._user_data.get(key)

    def __setitem__(self, key, val):
        """Set a user data element."""
        self._user_data[key] = val

    def __eq__(self, other):
        """Test if the current user data equals another user data instance."""
        isequal = False
        if isinstance(other, UserData):
            for key in self._user_data:
                if self._user_data[key] == other[key]:
                    isequal = True
                else:
                    isequal = False
                    break
        return isequal

    def __ne__(self, other):
        """Test if the current user data is not equal to another instance."""
        return bool(self != other)

    def __str__(self):
        """Emit the address in human-readible format (AA.BB.CC)."""
        hex_str = binascii.hexlify(bytes(self)).decode()
        strout = ''
        first = True
        for i in range(0, 28, 2):
            if first:
                first = False
            else:
                strout = strout + '.'
            strout = strout + hex_str[i:i + 2]
        return strout

    def __bytes__(self):
        """Emit the address in bytes format."""
        byteout = bytearray()
        for i in range(1, 15):
            key = 'd' + str(i)
            if self._user_data[key] is not None:
                byteout.append(self._user_data[key])
            else:
                byteout.append(0x00)
        return bytes(byteout)

    def get(self, key):
        """Return a single byte of the user data."""
        return self._user_data.get(key)

    def to_dict(self):
        """Return user_data as a dict object."""
        return self._user_data
