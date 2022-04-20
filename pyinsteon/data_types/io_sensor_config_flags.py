"""I/O Sensor port configutation flags."""
from ..utils import bit_is_set, set_bit


class IOPortConfigFlags:
    """I/O Sensor port configuration flags."""

    def __init__(
        self,
        analog_input_mode: int = 0x00,
        send_on_sensor_alarm: bool = False,
        send_on_input_port_change: bool = False,
        enable_1_wire_port: bool = False,
        enable_all_link_aliasing: bool = False,
        send_on_outut_port_change: bool = False,
        enable_output_timers: bool = False,
    ):
        """Init the IOPortConfigFlags class."""
        # Analog Input Mode:
        #   0x00 Analog Input not used
        #   0x01 Analog Input used, convert upon command
        #   0x10 Analog Input used, convert at fixed interval
        #   0x11 Unused
        self._analog_input_mode = analog_input_mode
        self._send_on_sensor_alarm = send_on_sensor_alarm
        self._send_on_input_port_change = send_on_input_port_change
        self._enable_1_wire_port = enable_1_wire_port
        self._enable_all_link_aliasing = enable_all_link_aliasing
        self._send_on_output_port_change = send_on_outut_port_change
        self._enable_output_timers = enable_output_timers

    def __bytes__(self):
        """Return the byte representation of the flags."""
        return bytes(bytearray([int(self)]))

    def __int__(self):
        """Return the integer representation of the flags."""
        flags = self._analog_input_mode
        flags = set_bit(flags, 2, self._send_on_sensor_alarm)
        flags = set_bit(flags, 3, self._send_on_input_port_change)
        flags = set_bit(flags, 4, self._enable_1_wire_port)
        flags = set_bit(flags, 5, self._enable_all_link_aliasing)
        flags = set_bit(flags, 6, self._send_on_output_port_change)
        flags = set_bit(flags, 7, self._enable_output_timers)
        return flags

    @property
    def analog_input_mode(self):
        """Return the analog_input_mode flag."""
        return self._analog_input_mode

    @property
    def send_on_sensor_alarm(self):
        """Return the send_on_sensor_alarm flag."""
        return self._send_on_sensor_alarm

    @property
    def send_on_input_port_change(self):
        """Return the send_on_input_port_change flag."""
        return self._send_on_input_port_change

    @property
    def enable_1_wire_port(self):
        """Return the enable_1_wire_port flag."""
        return self._enable_1_wire_port

    @property
    def enable_all_link_aliasing(self):
        """Return the enable_all_link_aliasing flag."""
        return self._enable_all_link_aliasing

    @property
    def send_on_output_port_change(self):
        """Return the send_on_output_port_change flag."""
        return self._send_on_output_port_change

    @property
    def enable_output_timers(self):
        """Return the enable_output_timers flag."""
        return self._enable_output_timers

    @classmethod
    def create_from_byte(cls, value):
        """Create a IOPortConfigFlags from a byte value."""
        analog_input_mode = value & 0x03
        send_on_sensor_alarm = bit_is_set(value, 2)
        send_on_input_port_change = bit_is_set(value, 2)
        enable_1_wire_port = bit_is_set(value, 2)
        enable_all_link_aliasing = bit_is_set(value, 2)
        send_on_outut_port_change = bit_is_set(value, 2)
        enable_output_timers = bit_is_set(value, 2)
        return cls(
            analog_input_mode,
            send_on_sensor_alarm,
            send_on_input_port_change,
            enable_1_wire_port,
            enable_all_link_aliasing,
            send_on_outut_port_change,
            enable_output_timers,
        )
