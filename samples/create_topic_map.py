"""Create a topic map."""
from random import randint

from pubsub import pub
from pubsub.utils.xmltopicdefnprovider import exportTopicTreeSpecXml

from pyinsteon.address import Address
from pyinsteon.device_types.ipdb import IPDB

devices = []


def random_address():
    """Generate a random address."""
    address = ""
    for _ in range(0, 3):
        rand_int = randint(1, 255)
        if address:
            address = f"{address}."
        address = f"{address}{rand_int:02x}"
    return Address(address)


ipdb = IPDB()
addr = random_address()
for prod in ipdb:
    try:
        device = prod.deviceclass(
            address=addr,
            cat=prod.cat,
            subcat=prod.subcat,
            description=prod.description,
            model=prod.model,
        )
        devices.append(device)

    except Exception:
        pass

exportTopicTreeSpecXml("pyinsteon", pub.topicTreeRoot)
# pub.exportTopicTreeSpec(moduleName="pyinsteon")
