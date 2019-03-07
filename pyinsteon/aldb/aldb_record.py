"""ALDB Records."""

from ..address import Address
from .control_flags import ControlFlags, create_from_byte
from ..messages.all_link_record_flags import AllLinkRecordFlags
from ..messages.user_data import UserData


def create_from_userdata(userdata: UserData):
    """Create ALDB Record from the userdata dictionary."""
    memhi = userdata.get('d3')
    memlo = userdata.get('d4')
    memory = memhi << 8 | memlo
    control_flags = userdata.get('d6')
    group = userdata.get('d7')
    addrhi = userdata.get('d8')
    addrmed = userdata.get('d9')
    addrlo = userdata.get('d10')
    addr = Address(bytearray([addrhi, addrmed, addrlo]))
    data1 = userdata.get('d11')
    data2 = userdata.get('d12')
    data3 = userdata.get('d13')
    return ALDBRecord(memory, control_flags, group, addr,
                      data1, data2, data3)

class ALDBRecord():
    """Represents an ALDB record."""

    def __init__(self, memory: int, control_flags: ControlFlags, group: int,
                 address: Address, data1: int, data2: int, data3: int):
        """Initialze the ALDBRecord class."""
        self._memoryLocation = memory
        self._address = Address(address)
        self._group = group
        self._data1 = data1
        self._data2 = data2
        self._data3 = data3
        if isinstance(control_flags, ControlFlags):
            self._control_flags = control_flags
        elif isinstance(control_flags, AllLinkRecordFlags):
            from ..constants import AllLinkMode
            is_controller = control_flags.mode == AllLinkMode.CONTROLLER
            self._control_flags = ControlFlags(control_flags.is_in_use,
                                               is_controller,
                                               control_flags.is_hwm,
                                               control_flags.is_bit_5_set,
                                               control_flags.is_bit_4_set)
        else:
            self._control_flags = create_from_byte(control_flags)

    def __str__(self):
        """Return the string representation of an ALDB record."""
        props = self._record_properties()
        msgstr = "{"
        first = True
        for prop in props:
            if not first:
                msgstr = '{}, '.format(msgstr)
            for key, val in prop.items():
                if isinstance(val, Address):
                    msgstr = "{}'{}': {}".format(msgstr, key, val)
                elif key == 'memory':
                    msgstr = "{}'{}': 0x{:04x}".format(msgstr, key, val)
                elif isinstance(val, int):
                    msgstr = "{}'{}': 0x{:02x}".format(msgstr, key, val)
                else:
                    msgstr = "{}'{}': {}".format(msgstr, key, val)
            first = False
        msgstr = "{}{}".format(msgstr, '}')
        return msgstr

    def __dict___(self):
        """Return a dictionary object of the ALDB Record."""
        return {'d1': 0x00,
                'd2': 0x00,
                'd3': self.memhi,
                'd4': self.memlo,
                'd5': 0x00,
                'd6': self.control_flags,
                'd7': self.group,
                'd8': bytes(self.address)[2],
                'd9': bytes(self.address)[1],
                'd10': bytes(self.address)[0],
                'd11': self.data1,
                'd12': self.data2,
                'd13': self.data3,
                'd14': 0x00}

    @property
    def mem_addr(self):
        """Return the memory address of the database record."""
        return self._memoryLocation

    @property
    def memhi(self):
        """Return the memory address MSB."""
        return self._memoryLocation >> 8

    @property
    def memlo(self):
        """Return the memory address LSB."""
        return self._memoryLocation & 0xff

    @property
    def address(self):
        """Return the address of the device the record points to."""
        return self._address

    @property
    def group(self):
        """Return the group the record responds to."""
        return self._group

    @property
    def control_flags(self):
        """Return the record control flags."""
        return self._control_flags

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

    def _record_properties(self):
        if self._control_flags.is_controller:
            mode = 'C'
        else:
            mode = 'R'
        rec = [{'memory': self._memoryLocation},
               {'inuse': self._control_flags.is_in_use},
               {'mode': mode},
               {'highwater': self._control_flags.is_high_water_mark},
               {'group': self.group},
               {'address': self.address},
               {'data1': self.data1},
               {'data2': self.data2},
               {'data3': self.data3}]
        return rec
