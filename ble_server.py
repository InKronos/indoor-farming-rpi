import sys
import logging
import asyncio
import threading
import subprocess
from typing import Any, Union

from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name=__name__)

CREDENTIALS_FILE = "/tmp/wifi_credentials.txt"

def write_wifi_credentials(wifi_name: str, wifi_password: str):
    try:
        with open(CREDENTIALS_FILE, 'w') as file:
            file.write(f"{wifi_name}:{wifi_password}")
        logger.debug(f"Wrote Wi-Fi credentials to file: {wifi_name}:{wifi_password}")
    except Exception as e:
        logger.error(f"Failed to write Wi-Fi credentials: {e}")

# NOTE: Some systems require different synchronization methods.
trigger: Union[asyncio.Event, threading.Event]
if sys.platform in ["darwin", "win32"]:
    trigger = threading.Event()
else:
    trigger = asyncio.Event()


def is_connected_to_wifi() -> bool:
    try:
        result = subprocess.run(["iwgetid"], capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Failed to check Wi-Fi connection status: {e}")
        return False
    
def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    if is_connected_to_wifi():
        return b'\x01'
    else:
        logger.debug("Device is not connected to Wi-Fi")
        return b'\x00' 


def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
    logger.debug(f"Received write request with value: {value}")
    # Decode the incoming data
    data = value.decode('utf-8')
    # Split into Wi-Fi name and password
    wifi_name, wifi_password = data.split(':')
    logger.debug(f"Wi-Fi Name: {wifi_name}, Wi-Fi Password: {wifi_password}")

    # Write credentials to file
    write_wifi_credentials(wifi_name, wifi_password)
    characteristic.value = b"Written"
        
       



async def run(loop):
    trigger.clear()
    # Instantiate the server
    my_service_name = "BLE Farming Device"
    server = BlessServer(name=my_service_name, loop=loop)
    server.write_request_func = write_request
    server.read_request_func = read_request

    # Add Service
    my_service_uuid = "A07498CA-AD5B-474E-940D-16F1FBE7E8CD"
    await server.add_new_service(my_service_uuid)

    # Add the first Characteristic to the service
    my_char_uuid = "51FF12BB-3ED8-46E5-B4F9-D64E2FEC021B"
    char_flags = (
        GATTCharacteristicProperties.read
        | GATTCharacteristicProperties.write
        | GATTCharacteristicProperties.indicate
    )
    permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
    char = await server.add_new_characteristic(
        my_service_uuid, my_char_uuid, char_flags, None, permissions
    )
    

    logger.debug(f"Characteristic {my_char_uuid}: {server.get_characteristic(my_char_uuid)}")
    await server.start()
    logger.debug("Advertising")
    logger.info(f"Write '0xF' to the advertised characteristic: {my_char_uuid}")
    if trigger.__module__ == "threading":
        trigger.wait()
    else:
        await trigger.wait()

    await asyncio.sleep(2)
    logger.debug("Updating")
    server.get_characteristic(my_char_uuid)
    server.update_value(my_service_uuid, my_char_uuid)
    await asyncio.sleep(5)
    await server.stop()


loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))