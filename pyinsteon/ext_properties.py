"""Extended Properties."""
RAMP_RATE = 'ramp_rate'
X10_HOUSE = 'x10_house'
X10_UNIT = 'x10_unit'
LED_DIMMING = 'led_dimming'
ON_LEVEL = 'on_level'

class ExtendedProperties():
    """Device extended properties."""

    def __init__(self, data3='data3', data4='data4', data5='data5', data6='data6',
                 data7='data7', data8='data8', data9='data9', data10='data10',
                 data11='data11', data12='data12', data13='data13', data14='data14'):
        """Init the OperatingFlagByte class."""
        self._flags = {}
        self._names = {}
        args = locals()
        for flag in range(3, 15):
            param = 'data{}'.format(flag)
            self._flags[flag] = 0x00
            self._names[flag] = args.get(param)

        self._is_dirty = False

    def __getitem__(self, key):
        """Return the value of the flag."""
        flag = self._get_flag_from_key(key)
        return self._flags.get(flag)

    def __setitem__(self, key, value):
        """Set the value of the flag."""
        self._set_value(key, value)
        self._is_dirty = True

    def __iter__(self):
        """Return the flag keys."""
        for flag in self._names:
            yield self._names[flag]

    def add_handler(self, handler):
        """Subscribe to a handler to set the value of the state."""
        handler.subscribe(self._set_values)

    def _set_value(self, key, value):
        """Set the value of the flag without marking as dirty."""
        try:
            if int(value) < 0 or int(value) > 0xff:
                raise ValueError('Operating flag must be a single byte integer')
        except ValueError:
            raise ValueError('Operating flag must be a single byte integer')
        flag = self._get_flag_from_key(key)
        self._flags[flag] = int(value)

    def _set_values(self, data):
        """Set the value of the flags."""
        flag = range(3, 15).__iter__()
        for value in data:
            self[next(flag)] = value

    def _get_flag_from_key(self, key):
        """Return the bit number from the operating flag name."""
        if not isinstance(key, str) and not isinstance(key, int):
            raise KeyError
        if isinstance(key, str):
            for bit in self._names:
                if self._names[bit] == key:
                    return bit
            raise KeyError('Extended property {} not found'.format(key))
        if not key in range(3, 15):
            raise KeyError('Extended property must be in user data bytes 3 through 14')
        return key
