"""All-Link Database for PLM based devices."""
from .modem_aldb import ModemALDB
from ..address import Address
from .aldb_record import ALDBRecord


MAX_RETRIES = 5

class PlmALDB(ModemALDB):
    """"All-Link database for PLM based devices."""
