"""Extended Message User Data Type."""
import logging
import binascii

_LOGGER = logging.getLogger(__name__)


def create_empty(val=0x00):
    """Create an empty Userdata object.

    val: value to fill the empty user data fields with (default is 0x00)
    """
    userdata_dict = {}
    for i in range(1, 15):
        key = 'd{}'.format(i)
        userdata_dict.update({key: val})
    return userdata_dict


def _dict_to_dict(empty, userdata):
    if isinstance(userdata, dict):
        for key in userdata:
            if key in ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7',
                        'd8', 'd9', 'd10', 'd11', 'd12', 'd13', 'd14']:
                empty[key] = userdata[key]
    return empty


def _bytes_to_dict(empty, userdata):
    if len(userdata) == 14:
        for i in range(1, 15):
            key = 'd{}'.format(i)
            empty[key] = userdata[i - 1]
    else:
        raise ValueError
    return empty


def _normalize(empty, userdata):
    """Return normalized user data as a dictionary.

    empty: an empty dictionary
    userdata: data in the form of Userdata, dict or None
    """
    if isinstance(userdata, UserData):
        return userdata.to_dict()
    if isinstance(userdata, dict):
        return _dict_to_dict(empty, userdata)
    if isinstance(userdata, (bytes, bytearray)):
        return _bytes_to_dict(empty, userdata)
    if userdata is None:
        return empty
    raise ValueError


class UserData():
    """Extended Message User Data Type."""

    def __init__(self, userdata=bytearray(bytes(14))):
        """Init the Userdata Class."""
        self._userdata = _normalize(create_empty(0x00), userdata)

    def __len__(self):
        """Init Userdata Class."""
        return len(self._userdata)

    def __iter__(self):
        """Iterate through the user data bytes."""
        for itm in self._userdata:
            yield itm

    def __getitem__(self, key):
        """Return a single byte of the user data."""
        return self._userdata.get(key)

    def __setitem__(self, key, val):
        """Set a user data element."""
        self._userdata[key] = val

    def __eq__(self, other):
        """Test if the current user data equals another user data instance."""
        isequal = False
        if isinstance(other, UserData):
            for key in self._userdata:
                if self._userdata[key] == other[key]:
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
            if self._userdata[key] is not None:
                byteout.append(self._userdata[key])
            else:
                byteout.append(0x00)
        return bytes(byteout)

    def get(self, key):
        """Return a single byte of the user data."""
        return self._userdata.get(key)

    def to_dict(self):
        """Return userdata as a dict object."""
        return self._userdata
