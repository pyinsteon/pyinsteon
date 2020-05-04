"""Convert an Insteon Message to a URL for the Hub."""
from ..constants import AllLinkMode
from .messages.outbound import Outbound


def _to_url(host, port, cmd):
    """Convert a host, port and command to a url."""
    return "http://{:s}:{:d}/{:s}".format(host, port, cmd)


def convert_to_url(host, port, msg: Outbound) -> str:
    """Convert a message to a URL."""
    return _to_url(host, port, "3?{:s}=I=3".format(bytes(msg).hex()))


def start_all_link_url(host, port, msg: Outbound):
    """Convert a Start All-Linking message to URL."""
    if msg.mode == AllLinkMode.DELETE:
        return _to_url(host, port, "3?{:s}=I=3".format(bytes(msg).hex()))
    return _to_url(host, port, "0?09{:02d}".format(msg.group))


def cancel_all_linking_url(host, port, msg: Outbound):
    """Convert a Cancel All-Linking message to URL."""
    return _to_url(host, port, "0?0800")
