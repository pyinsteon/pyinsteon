"""Extended Message User Data Type."""
import logging
import binascii

_LOGGER = logging.getLogger(__name__)


class UserData():
    """Extended Message User Data Type."""

    def __init__(self, userdata):
        """Init the Userdata Class."""
        self._userdata = self.normalize(self.create_empty(0x00), userdata)

    def __len__(self):
        """Init Userdata Class."""
        return len(self._userdata)

    def __str__(self):
        """Return string representation of user data."""
        return self.human

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

    @property
    def human(self):
        """Emit the address in human-readible format (AA.BB.CC)."""
        strout = ''
        first = True
        for i in range(0, 28, 2):
            if first:
                first = False
            else:
                strout = strout + '.'
            strout = strout + self.hex[i:i + 2]
        return strout

    @property
    def hex(self):
        """Emit the address in bare hex format."""
        return binascii.hexlify(self.bytes).decode()

    @property
    def bytes(self):
        """Emit the address in bytes format."""
        byteout = bytearray()
        for i in range(1, 15):
            key = 'd' + str(i)
            if self._userdata[key] is not None:
                byteout.append(self._userdata[key])
            else:
                byteout.append(0x00)
        return byteout

    @classmethod
    def from_raw_message(cls, rawmessage):
        """Create a user data instance from a raw byte stream."""
        empty = cls.create_empty(0x00)
        userdata_dict = cls.normalize(empty, rawmessage)
        return UserData(userdata_dict)

    @classmethod
    def create_pattern(cls, userdata):
        """Create a user data instance with all values the same."""
        empty = cls.create_empty(None)
        userdata_dict = cls.normalize(empty, userdata)
        return UserData(userdata_dict)

    @classmethod
    def create(cls):
        """Create an empty user data instance."""
        empty = cls.create_empty(0x00)
        return UserData(empty)

    @classmethod
    def template(cls, userdata):
        """Create a template instance used for message callbacks."""
        ud = UserData(cls.normalize(cls.create_empty(None), userdata))
        return ud

    def matches_pattern(self, other):
        """Test if the current instance matches a template instance."""
        ismatch = False
        if isinstance(other, UserData):
            for key in self._userdata:
                if self._userdata[key] is None or other[key] is None:
                    ismatch = True
                elif self._userdata[key] == other[key]:
                    ismatch = True
                else:
                    ismatch = False
                    break
        return ismatch

    def get(self, key):
        """Return a single byte of the user data."""
        return self[key]

    def to_dict(self):
        """Return userdata as a dict object."""
        return self._userdata

    @classmethod
    def _dict_to_dict(cls, empty, userdata):
        if isinstance(userdata, dict):
            for key in userdata:
                if key in ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7',
                           'd8', 'd9', 'd10', 'd11', 'd12', 'd13', 'd14']:
                    empty[key] = userdata[key]
        return empty

    @classmethod
    def _bytes_to_dict(cls, empty, userdata):
        if len(userdata) == 14:
            for i in range(1, 15):
                key = 'd{}'.format(i)
                empty[key] = userdata[i - 1]
        else:
            raise ValueError
        return empty

    @classmethod
    def create_empty(cls, val=0x00):
        """Create an empty Userdata object.

        val: value to fill the empty user data fields with (default is 0x00)
        """
        userdata_dict = {}
        for i in range(1, 15):
            key = 'd{}'.format(i)
            userdata_dict.update({key: val})
        return userdata_dict

    @classmethod
    def normalize(cls, empty, userdata):
        """Return normalized user data as a dictionary.

        empty: an empty dictionary
        userdata: data in the form of Userdata, dict or None
        """
        if isinstance(userdata, UserData):
            return userdata.to_dict()
        if isinstance(userdata, dict):
            return cls._dict_to_dict(empty, userdata)
        if isinstance(userdata, (bytes, bytearray)):
            return cls._bytes_to_dict(empty, userdata)
        if userdata is None:
            return empty
        raise ValueError
