import logging
from serial.tools.list_ports import comports
from nqrduck.module.module_controller import ModuleController

logger = logging.getLogger(__name__)

class AutoTMController(ModuleController):
    

    def find_devices(self):
        """Scan for available serial devices and add them to the model as available devices. """
        logger.debug("Scanning for available serial devices")
        ports = comports()
        self.module.model.available_devices = [port.device for port in ports]
        logger.debug("Found %s devices", len(self.module.model.available_devices))
        for device in self.module.model.available_devices:
            logger.debug("Found device: %s", device)
