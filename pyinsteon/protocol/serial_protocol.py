"""Serial protocol to perform async I/O with the Powerline Modem (PLM)."""

import asyncio
import logging
from enum import Enum

from pubsub.core.topicobj import Topic
from serial_asyncio import create_serial_connection

from .. import pub


#pylint: disable=unused-import
from .command_to_msg import (assign_to_all_link_group,
                             assign_to_companion_group, brighten_one_step,
                             delete_from_all_link_group,
                             device_text_string_request, dim_one_step,
                             door_move_close_door, door_move_lower_door,
                             door_move_open_door, door_move_raise_door,
                             door_move_single_door_close,
                             door_move_single_door_open, door_move_stop_door,
                             door_status_report_close_door,
                             door_status_report_open_door,
                             door_status_report_raise_door,
                             door_status_report_single_door_close,
                             door_status_report_single_door_open,
                             door_status_report_stop_door,
                             door_status_reportlower_door, enter_linking_mode,
                             enter_unlinking_mode, extended_get_set,
                             extended_read_write_aldb,
                             extended_trigger_all_link, fx_username,
                             get_insteon_engine_version, get_operating_flags,
                             id_request, instant_change, io_alarm_data_request,
                             io_alarm_data_response, io_get_sensor_alarm_delta,
                             io_get_sensor_value, io_module_diagnostics_off,
                             io_module_diagnostics_on,
                             io_module_disable_status_change_message,
                             io_module_enable_status_change_message,
                             io_module_load_eeprom_from_ram,
                             io_module_load_initialization_values,
                             io_module_load_ram_from_eeprom,
                             io_module_read_analog_always,
                             io_module_read_analog_once, io_module_sensor_off,
                             io_module_sensor_on, io_module_status_request,
                             io_output_off, io_output_on,
                             io_read_configuration_port, io_read_input_port,
                             io_set_sensor_1_nominal_value,
                             io_set_sensor_nominal_value,
                             io_write_configuration_port, io_write_output_port,
                             off, off_at_ramp_rate, off_fast, on,
                             on_at_ramp_rate, on_fast, peek_one_byte,
                             peek_one_byte_internal, ping, poke_one_byte,
                             poke_one_byte_internal, pool_device_off,
                             pool_device_on, pool_get_ambient_temperature,
                             pool_get_ph, pool_get_pool_mode,
                             pool_get_water_temperature,
                             pool_load_eeprom_from_ram,
                             pool_load_initialization_values,
                             pool_set_device_hysteresis,
                             pool_set_device_temperature,
                             pool_temperature_down, pool_temperature_up,
                             product_data_request, set_address_msb,
                             set_all_link, set_all_link_command_alias,
                             set_device_text_string, set_operating_flags,
                             set_sprinkler_program, set_status,
                             sprinkler_broadcast_off, sprinkler_broadcast_on,
                             sprinkler_diagnostics_off,
                             sprinkler_diagnostics_on,
                             sprinkler_disable_pump_on_v8,
                             sprinkler_enable_pump_on_v8,
                             sprinkler_get_program_request,
                             sprinkler_get_program_response,
                             sprinkler_get_valve_status,
                             sprinkler_inhibit_command_acceptance,
                             sprinkler_load_eeprom_from_ram,
                             sprinkler_load_initialization_values,
                             sprinkler_load_ram_from_eeprom,
                             sprinkler_program_off, sprinkler_program_on,
                             sprinkler_resume_command_acceptance,
                             sprinkler_sensor_off, sprinkler_sensor_on,
                             sprinkler_skip_back, sprinkler_skip_forward,
                             sprinkler_valve_off, sprinkler_valve_on,
                             status_request, status_request_alternate_1,
                             status_request_alternate_2,
                             status_request_alternate_3,
                             thermostat_disable_status_change_message,
                             thermostat_enable_status_change_message,
                             thermostat_get_ambient_temperature,
                             thermostat_get_equipment_state,
                             thermostat_get_fan_on_speed, thermostat_get_mode,
                             thermostat_get_temperature_units,
                             thermostat_get_zone_information,
                             thermostat_load_eeprom_from_ram,
                             thermostat_load_initialization_values,
                             thermostat_off_all, thermostat_off_fan,
                             thermostat_on_auto, thermostat_on_cool,
                             thermostat_on_fan, thermostat_on_heat,
                             thermostat_program_auto, thermostat_program_cool,
                             thermostat_program_heat, thermostat_set_celsius,
                             thermostat_set_cool_setpoint,
                             thermostat_set_equipment_state,
                             thermostat_set_fahrenheit,
                             thermostat_set_fan_on_speed_high,
                             thermostat_set_fan_on_speed_low,
                             thermostat_set_fan_on_speed_medium,
                             thermostat_set_heat_setpoint,
                             thermostat_set_zone_cool_setpoint,
                             thermostat_set_zone_heat_setpoint,
                             thermostat_temperature_down,
                             thermostat_temperature_up,
                             thermostat_zone_temperature_down,
                             thermostat_zone_temperature_up,
                             window_covering_close, window_covering_open,
                             window_covering_position, window_covering_program,
                             window_covering_stop)
from .messages.inbound import create
from .messages.outbound import (cancel_all_linking,
                                get_all_link_record_for_sender,
                                get_first_all_link_record,
                                get_im_configuration, get_im_info,
                                get_next_all_link_record, led_off, led_on,
                                manage_all_link_record, reset_im, rf_sleep,
                                send_all_link_command, send_extended,
                                send_standard, set_ack_message_byte,
                                set_ack_message_two_bytes, set_host_dev_cat,
                                set_im_configuration, set_nak_message_byte,
                                start_all_linking, x10_send)
from .msg_to_topic import convert_to_topic


_LOGGER = logging.getLogger(__name__)
WRITE_WAIT = 1.5  # Time to wait between writes to transport


async def connect(device, loop=None, baudrate=19200, **kwargs):
    """Connect to the serial port.

    Parameters:

    port – Device name.

    baudrate (int) – Baud rate such as 9600 or 115200 etc.

    bytesize – Number of data bits. Possible values: FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS

    parity – Enable parity checking. Possible values: PARITY_NONE, PARITY_EVEN, PARITY_ODD
    PARITY_MARK, PARITY_SPACE

    stopbits – Number of stop bits. Possible values: STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE,
    STOPBITS_TWO

    timeout (float) – Set a read timeout value.

    xonxoff (bool) – Enable software flow control.

    rtscts (bool) – Enable hardware (RTS/CTS) flow control.

    dsrdtr (bool) – Enable hardware (DSR/DTR) flow control.

    write_timeout (float) – Set a write timeout value.

    inter_byte_timeout (float) – Inter-character timeout, None to disable (default).
    """
    loop = loop if loop else asyncio.get_event_loop()
    transport, protocol = await create_serial_connection(loop, SerialProtocol,
                                                         device,
                                                         baudrate=baudrate,
                                                         **kwargs)
    return transport, protocol


def _strip_topic(topic: Topic):
    """Return the root topic."""


class TransportStatus(Enum):
    """Status of the transport."""

    CLOSED = 0
    LOST = 1
    PAUSED = 2
    OPEN = 3


class SerialProtocol(asyncio.Protocol):
    """Serial protocol to perform async I/O with the PLM."""

    def __init__(self, *args, **kwargs):
        """Init the SerialProtocol class."""
        super().__init__(*args, **kwargs)
        self._transport = None
        self._status = TransportStatus.CLOSED
        self._message_queue = asyncio.PriorityQueue()
        self._buffer = bytearray()
        self._writer_task = None

    @property
    def connected(self) -> bool:
        """Return true if the transport is connected."""
        return self._status in [TransportStatus.OPEN, TransportStatus.PAUSED]

    def connection_made(self, transport):
        self._transport = transport
        self._start_writer()
        self._subscribe()
        self._status = TransportStatus.OPEN
        pub.sendMessage('connection.made')

    def data_received(self, data):
        """Receive data from the serial transport."""
        self._buffer.extend(data)
        _LOGGER.debug('CURR BUFF: %s', self._buffer.hex())
        while True:
            last_buffer = self._buffer
            _LOGGER.debug('BUFFER IN: %s', self._buffer.hex())
            msg, self._buffer = create(self._buffer)
            _LOGGER.debug('BUFFER OUT: %s', self._buffer.hex())
            if msg:
                try:
                    (topic, kwargs) = convert_to_topic(msg)
                    if self._is_nak(msg) and not self._has_listeners(topic):
                        self._resend(msg)
                    else:
                        pub.sendMessage(topic, **kwargs)
                except ValueError:
                    # No topic was found for this message
                    _LOGGER.warning('No topic found for message %r', msg)
            if last_buffer == self._buffer or not self._buffer:
                _LOGGER.debug('BREAKING: %s', self._buffer.hex())
                break

    def connection_lost(self, exc):
        """Notify listeners that the serial connection is lost."""
        self._writer_task.cancel()
        self._status = TransportStatus.CLOSED
        pub.sendMessage('connection.lost')

    def pause_writing(self):
        """Pause writing to the transport."""
        self._writer_task.cancel()
        self._status = TransportStatus.PAUSED
        pub.sendMessage('protocol.writing.pause')

    def resume_writing(self):
        """Resume writing to the transport."""
        self._start_writer()
        self._status = TransportStatus.OPEN
        pub.sendMessage('protocol.writing.resume')

    def close(self):
        """Close the serial transport."""
        self._unsubscribe()
        if self._transport:
            self._transport.close()
        self._writer_task.cancel()
        self._status = TransportStatus.CLOSED

    def _write(self, msg, priority=5):
        """Prepare data for writing to the transport.

        Data is actually writen by _write_message to ensure a pause beteen writes.
        This approach minimizes NAK messages. This also allows for some messages
        to be lower priority such as 'Load ALDB' versus higher priority such as
        'Set Light Level'.
        """
        send_msg = msg if isinstance(msg, bytes) else bytes(msg)
        self._message_queue.put_nowait((priority, send_msg))

    def _subscribe(self):
        """Subscribe to topics."""
        pub.subscribe(self._write, "send_message")

    def _resend(self, msg):
        """Resend after a NAK message.

        TODO: Avoid resending the same message 10 times.
        """
        self._write(bytes(msg)[:-1])

    def _is_nak(self, msg):
        """Test if a message is a NAK from the modem."""
        if hasattr(msg, 'ack') and msg.ack.value == 0x15:
            return True
        return False

    def _has_listeners(self, topic):
        """Test if a topic has listeners.

        Only used if the msg is a NAK. If no NAK specific listeners
        then resend the message. Otherwise it is assumed the NAK
        specific listner is resending if necessary.
        """
        topicManager = pub.getDefaultTopicMgr()
        pub_topic = topicManager.getTopic(name=topic, okIfNone=True)
        if pub_topic and pub_topic.getListeners():
            return True
        return False

    def _unsubscribe(self):
        """Unsubscribe to topics."""
        pub.unsubscribe(self._write, 'send_message')

    def _start_writer(self):
        """Start the message writer."""
        self._writer_task = asyncio.ensure_future(self._write_messages())

    async def _write_messages(self):
        """Write data to the transport."""
        while self._status == TransportStatus.OPEN:
            _, msg = await self._message_queue.get()
            self._transport.write(msg)
            await asyncio.sleep(WRITE_WAIT)
