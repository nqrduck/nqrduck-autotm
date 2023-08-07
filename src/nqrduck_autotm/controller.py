import logging
from serial.tools.list_ports import comports
from PyQt6 import QtSerialPort
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
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
            self.module.model.serial = QtSerialPort.QSerialPort(device, baudRate=self.BAUDRATE, readyRead=self.on_ready_read)
            self.module.model.serial.open(QtSerialPort.QSerialPort.OpenModeFlag.ReadWrite)


            
            logger.debug("Connected to device %s", device)
        except Exception as e:
            logger.error("Could not connect to device %s: %s", device, e)

    def start_frequency_sweep(self, start_frequency : float, stop_frequency : float) -> None:
        """ This starts a frequency sweep on the device in the specified range."""
        logger.debug("Starting frequency sweep from %s to %s", start_frequency, stop_frequency)
        # Print the command 'f <start> <stop>' to the serial connection
        command = "f %s %s" % (start_frequency, stop_frequency)
        self.module.model.serial.write(command.encode('utf-8'))

    def on_ready_read(self) -> None:
        """This method is called when data is received from the serial connection. """
        serial = self.module.model.serial
        while serial.canReadLine():
            text = serial.readLine().data().decode()
            text = text.rstrip('\r\n')
            logger.debug("Received data: %s", text)
            if text.startswith("f"):
                text = text[1:].split("r")
                frequency = float(text[0])
                return_loss = float(text[1])
                self.module.model.add_data_point(frequency, return_loss)
            else:
                self.module.view.add_info_text(text)
