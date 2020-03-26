"""Container for a default link record."""
from collections import namedtuple

DefaultLink = namedtuple(
    "DefaultLink",
    "is_controller group dev_data1 dev_data2 dev_data3 "
    "modem_data1 modem_data2 modem_data3",
)
