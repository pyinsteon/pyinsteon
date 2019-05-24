"""Security, Heath and Safety device types."""
from . import Device, BatteryDeviceBase
from .on_off_controller_base import OnOffControllerBase

class SecurityHealthSafety(Device):
    """Security, Health and Safety base device."""

class SecurityHealthSafety_2845_222(BatteryDeviceBase, OnOffControllerBase):
    """Door sensor model 2845-222 or similary."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model=''):
        """Init the DevSecurityHealthSafety_2845_222 class."""
        super(SecurityHealthSafety_2845_222, self).__init__(
            address=address, cat=cat, subcat=subcat, firmware=firmware,
            description=description, model=model)
