import logging
import serial
from serial.tools.list_ports import comports
from nqrduck.module.module_controller import ModuleController

logger = logging.getLogger(__name__)

class AutoTMController(ModuleController):
    BAUDRATE = 115200

    def find_devices(self) -> None:
        """Scan for available serial devices and add them to the model as available devices. """
        logger.debug("Scanning for available serial devices")
        ports = comports()
        self.module.model.available_devices = [port.device for port in ports]
        logger.debug("Found %s devices", len(self.module.model.available_devices))
        for device in self.module.model.available_devices:
            logger.debug("Found device: %s", device)

    def connect(self, device : str) -> None:
        """Connect to the specified device. """
        logger.debug("Connecting to device %s", device)
        try:
            self.module.model.serial = serial.Serial(device, self.BAUDRATE, timeout=0.1)
            logger.debug("Connected to device %s", device)
        except serial.SerialException as e:
            logger.error("Failed to connect to device %s", device)
            logger.error(e)

    def start_frequency_sweep(self, start_frequency : float, stop_frequency : float) -> None:
        """ This starts a frequency sweep on the device in the specified range."""
        pass