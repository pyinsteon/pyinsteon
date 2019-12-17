"""ALDB Records."""

from ..address import Address


class ALDBRecord:
    """Represents an ALDB record."""

    def __init__(
        self,
        memory: int,
        controller: bool,
        group: int,
        target: Address,
        data1: int,
        data2: int,
        data3: int,
        in_use: bool = True,
        high_water_mark: bool = False,
        bit5: bool = False,
        bit4: bool = False,
    ):
        """Initialze the ALDBRecord class."""
        self._memory_location = memory
        self._target = Address(target)
        self._group = group
        self._data1 = data1
        self._data2 = data2
        self._data3 = data3
        self._controller = controller
        self._in_use = in_use
        self._high_water_mark = high_water_mark
        self._bit5 = bit5
        self._bit4 = bit4

    def __str__(self):
        """Return the string representation of an ALDB record."""
        props = self._record_properties()
        msgstr = "{"
        first = True
        for prop in props:
            if not first:
                msgstr = "{}, ".format(msgstr)
            for key, val in prop.items():
                if isinstance(val, Address):
                    msgstr = "{}'{}': {}".format(msgstr, key, val)
                elif key == "memory":
                    msgstr = "{}'{}': 0x{:04x}".format(msgstr, key, val)
                elif isinstance(val, int):
                    msgstr = "{}'{}': 0x{:02x}".format(msgstr, key, val)
                else:
                    msgstr = "{}'{}': {}".format(msgstr, key, val)
            first = False
        msgstr = "{}{}".format(msgstr, "}")
        return msgstr

    def __dict___(self):
        """Return a dictionary object of the ALDB Record."""
        control_flags = (
            int(self._in_use) << 7
            | int(self._controller) << 6
            | int(self._bit5) << 5
            | int(self._bit4) << 4
            | int(not self._high_water_mark) << 1
        )
        return {
            "d1": 0x00,
            "d2": 0x00,
            "d3": self.memhi,
            "d4": self.memlo,
            "d5": 0x00,
            "d6": control_flags,
            "d7": self.group,
            "d8": self.target.low,
            "d9": self.target.middle,
            "d10": self.target.high,
            "d11": self.data1,
            "d12": self.data2,
            "d13": self.data3,
            "d14": 0x00,
        }

    @property
    def mem_addr(self):
        """Return the memory address of the database record."""
        return self._memory_location

    @mem_addr.setter
    def mem_addr(self, value):
        """Set the memory address of the record."""
        try:
            mem = int(value)
        except ValueError:
            raise ValueError("Memory address must be an integer.")
        else:
            self._memory_location = mem

    @property
    def memhi(self):
        """Return the memory address MSB."""
        return self._memory_location >> 8

    @property
    def memlo(self):
        """Return the memory address LSB."""
        return self._memory_location & 0xFF

    @property
    def target(self):
        """Return the address of the device the record points to."""
        return self._target

    @property
    def group(self):
        """Return the group the record responds to."""
        return self._group

    @property
    def data1(self):
        """Return the data1 field of the ALDB record."""
        return self._data1

    @property
    def data2(self):
        """Return the data2 field of the ALDB record."""
        return self._data2

    @property
    def data3(self):
        """Return the data3 field of the ALDB record."""
        return self._data3

    @property
    def is_controller(self):
        """Return if the record is a controller record."""
        return self._controller

    @property
    def is_responder(self):
        """Return if the record is a responder."""
        return not self._controller

    @property
    def is_in_use(self):
        """Return if the record is in use."""
        return self._in_use

    @property
    def is_high_water_mark(self):
        """Return if this is the high water mark record."""
        return self._high_water_mark

    @property
    def is_bit5_set(self):
        """Return if control flag bit 5 is set."""
        return self._bit5

    @property
    def is_bit4_set(self):
        """Return if control flag bit 4 is set."""
        return self._bit4

    def _record_properties(self):
        if self._controller:
            mode = "C"
        else:
            mode = "R"
        rec = [
            {"memory": self._memory_location},
            {"inuse": self._in_use},
            {"mode": mode},
            {"bit5": self._bit5},
            {"bit4": self._bit4},
            {"highwater": self._high_water_mark},
            {"group": self.group},
            {"target": self.target},
            {"data1": self.data1},
            {"data2": self.data2},
            {"data3": self.data3},
        ]
        return rec
