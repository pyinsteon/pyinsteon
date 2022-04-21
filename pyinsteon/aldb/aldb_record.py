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
        if self._controller:
            link_mode = "C"
        else:
            link_mode = "R"
        rec = {
            "memory": f"0x{self._memory_location:04x}",
            "inuse": self._in_use,
            "link_mode": link_mode,
            "bit5": str(self._bit5),
            "bit4": str(self._bit4),
            "highwater": str(self._high_water_mark),
            "group": f"0x{int(self.group):02x}",
            "target": str(self.target),
            "data1": f"0x{int(self.data1):02x}",
            "data2": f"0x{int(self.data2):02x}",
            "data3": f"0x{int(self.data3):02x}",
        }
        return str(rec)

    def __repr__(self):
        """Return a representation of the record."""
        rec = {
            "memory": f"0x{self._memory_location:04x}",
            "control_flags": f"0x{int(self.control_flags):02x}",
            "group": f"0x{int(self.group):02x}",
            "target": str(self.target),
            "data1": f"0x{int(self.data1):02x}",
            "data2": f"0x{int(self.data2):02x}",
            "data3": f"0x{int(self.data3):02x}",
        }
        return str(rec)

    def __dict___(self):
        """Return a dictionary object of the ALDB Record."""

        return {
            "d1": 0x00,
            "d2": 0x00,
            "d3": self.memhi,
            "d4": self.memlo,
            "d5": 0x00,
            "d6": self.control_flags,
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

    @property
    def control_flags(self):
        """Return the control flag byte."""
        return (
            int(self._in_use) << 7
            | int(self._controller) << 6
            | int(self._bit5) << 5
            | int(self._bit4) << 4
            | int(not self._high_water_mark) << 1
        )

    def copy(self):
        """Create a new record as a copy of the current record."""
        return ALDBRecord(
            memory=self._memory_location,
            controller=self._controller,
            group=self._group,
            target=self._target,
            data1=self._data1,
            data2=self._data2,
            data3=self._data3,
            in_use=self._in_use,
            bit5=self._bit5,
            bit4=self._bit4,
        )


def new_aldb_record_from_existing(rec: ALDBRecord, **kwargs):
    """Create a new ALDB record from an existing record."""

    def get_element_or_default(key: str, default: any, **kwargs):
        """Return the value of the key or the default.

        Need to use this since the kwarg.get(key, default) can return
        `None` even if the default is not None if kwargs[key] is None.
        """
        value = kwargs.get(key)
        if value is not None:
            return value
        return default

    mem_addr = int(get_element_or_default("mem_addr", rec.mem_addr, **kwargs))
    in_use = bool(get_element_or_default("in_use", rec.is_in_use, **kwargs))
    controller = bool(get_element_or_default("controller", rec.is_controller, **kwargs))
    hwm = bool(
        get_element_or_default("high_water_mark", rec.is_high_water_mark, **kwargs)
    )
    target = Address(get_element_or_default("target", rec.target, **kwargs))
    group = int(get_element_or_default("group", rec.group, **kwargs))
    data1 = int(get_element_or_default("data1", rec.data1, **kwargs))
    data2 = int(get_element_or_default("data2", rec.data2, **kwargs))
    data3 = int(get_element_or_default("data3", rec.data3, **kwargs))
    bit5_set = bool(get_element_or_default("bit5", rec.is_bit5_set, **kwargs))
    bit4_set = bool(get_element_or_default("bit4", rec.is_bit4_set, **kwargs))

    return ALDBRecord(
        memory=mem_addr,
        controller=controller,
        group=group,
        target=target,
        high_water_mark=hwm,
        data1=data1,
        data2=data2,
        data3=data3,
        in_use=in_use,
        bit5=bit5_set,
        bit4=bit4_set,
    )
