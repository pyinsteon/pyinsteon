"""Convert an Insteon Message to a URL for the Hub."""
from ..constants import AllLinkMode
from .messages.outbound import Outbound


def _to_url(host, port, cmd):
    """Convert a host, port and command to a url."""
    return f"http://{host}:{port}/{cmd}"


def convert_to_url(host, port, msg: Outbound) -> str:
    """Convert a message to a URL."""
    return _to_url(host, port, f"3?{bytes(msg).hex()}=I=3")


def start_all_link_url(host, port, msg: Outbound):
    """Convert a Start All-Linking message to URL."""
    if msg.link_mode == AllLinkMode.DELETE:
        return _to_url(host, port, f"3?{bytes(msg).hex()}=I=3")
    return _to_url(host, port, f"0?09{msg.group:d}=I=0")


def cancel_all_linking_url(host, port, msg: Outbound):
    """Convert a Cancel All-Linking message to URL."""
    return _to_url(host, port, "0?08=I=0")
