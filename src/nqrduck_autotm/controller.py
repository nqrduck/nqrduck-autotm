import logging
import numpy as np
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
        # We create the frequency sweep spinner dialog
        self.module.model.clear_data_points()
        self.module.view.create_frequency_sweep_spinner_dialog()
        # Print the command 'f <start> <stop>' to the serial connection
        try:
            command = "f %s %s" % (start_frequency, stop_frequency)
            self.module.model.serial.write(command.encode('utf-8'))
        except AttributeError:
            logger.error("Could not start frequency sweep. No device connected.")


    def on_ready_read(self) -> None:
        """This method is called when data is received from the serial connection. """
        serial = self.module.model.serial
        while serial.canReadLine():
            text = serial.readLine().data().decode()
            text = text.rstrip('\r\n')
            # logger.debug("Received data: %s", text)
            # If the text starts with 'f' and the frequency sweep spinner is visible we know that the data is a data point
            # then we have the data for the return loss and the phase at a certain frequency
            if text.startswith("f") and self.module.view.frequency_sweep_spinner.isVisible():
                text = text[1:].split("r")
                frequency = float(text[0])
                return_loss, phase = map(float, text[1].split("p"))
                self.module.model.add_data_point(frequency, return_loss, phase)
            # If the text starts with 'r' and no calibration is active we know that the data is a measurement
            elif text.startswith("r") and self.module.model.active_calibration == None:
                logger.debug("Measurement finished")
                self.module.model.measurement = self.module.model.data_points.copy()
                self.module.view.frequency_sweep_spinner.hide()
            # If the text starts with 'r' and a short calibration is active we know that the data is a short calibration
            elif text.startswith("r") and self.module.model.active_calibration == "short":
                logger.debug("Short calibration finished")
                self.module.model.short_calibration = self.module.model.data_points.copy()
                self.module.model.active_calibration = None
                self.module.view.frequency_sweep_spinner.hide()
            # If the text starts with 'r' and an open calibration is active we know that the data is an open calibration
            elif text.startswith("r") and self.module.model.active_calibration == "open":
                logger.debug("Open calibration finished")
                self.module.model.open_calibration = self.module.model.data_points.copy()
                self.module.model.active_calibration = None
                self.module.view.frequency_sweep_spinner.hide()
            # If the text starts with 'r' and a load calibration is active we know that the data is a load calibration
            elif text.startswith("r") and self.module.model.active_calibration == "load":
                logger.debug("Load calibration finished")
                self.module.model.load_calibration = self.module.model.data_points.copy()
                self.module.model.active_calibration = None
                self.module.view.frequency_sweep_spinner.hide()
            # If the text starts with 'i' we know that the data is an info message
            elif text.startswith("i"):
                text = "ATM Info: " + text[1:]
                self.module.view.add_info_text(text)
            # If the text starts with 'e' we know that the data is an error message
            elif text.startswith("e"):
                text = "ATM Error: " + text[1:]
                self.module.view.add_info_text(text)

    def on_short_calibration(self, start_frequency : float, stop_frequency : float) -> None:
        """This method is called when the short calibration button is pressed.
        It starts a frequency sweep in the specified range and then starts a short calibration.
        """
        logger.debug("Starting short calibration")
        self.module.model.init_short_calibration()
        self.start_frequency_sweep(start_frequency, stop_frequency)

    def on_open_calibration(self, start_frequency : float, stop_frequency : float) -> None:
        """This method is called when the open calibration button is pressed.
        It starts a frequency sweep in the specified range and then starts an open calibration.
        """
        logger.debug("Starting open calibration")
        self.module.model.init_open_calibration()
        self.start_frequency_sweep(start_frequency, stop_frequency)

    def on_load_calibration(self, start_frequency : float, stop_frequency : float) -> None:
        """This method is called when the load calibration button is pressed.
        It starts a frequency sweep in the specified range and then loads a calibration.
        """
        logger.debug("Starting load calibration")
        self.module.model.init_load_calibration()
        self.start_frequency_sweep(start_frequency, stop_frequency)

    def calculate_calibration(self) -> None:
        """This method is called when the calculate calibration button is pressed.
        It calculates the calibration from the short, open and calibration data points.
        """
        logger.debug("Calculating calibration")
        # First we check if the short and open calibration data points are available
        if self.module.model.short_calibration == None:
            logger.error("No short calibration data points available")
            return
        
        if self.module.model.open_calibration == None:
            logger.error("No open calibration data points available")
            return
        
        if self.module.model.load_calibration == None:
            logger.error("No load calibration data points available")
            return
        
        # Then we check if the short, open and load calibration data points have the same length
        if len(self.module.model.short_calibration) != len(self.module.model.open_calibration) or len(self.module.model.short_calibration) != len(self.module.model.load_calibration):
            logger.error("The short, open and load calibration data points do not have the same length")
            return
        
        # Then we calculate the calibration
        ideal_gamma_short = -1
        ideal_gamma_open = 1
        ideal_gamma_load = 0

        short_calibration = [10 **(-returnloss_s[1]) for returnloss_s in self.module.model.short_calibration]
        open_calibration = [10 **(-returnloss_o[1]) for returnloss_o in self.module.model.open_calibration]
        load_calibration = [10 **(-returnloss_l[1]) for returnloss_l in self.module.model.load_calibration]

        e_00s = []
        e11s = []
        delta_es = []
        for gamma_s, gamma_o, gamma_l in zip(short_calibration, open_calibration, load_calibration):
            A = np.array([
                [1, ideal_gamma_short * gamma_s, -ideal_gamma_short],
                [1, ideal_gamma_open * gamma_o, -ideal_gamma_open],
                [1, ideal_gamma_load * gamma_l, -ideal_gamma_load]
            ])

            B = np.array([gamma_s, gamma_o, gamma_l])

            # Solve the system
            e_00, e11, delta_e = np.linalg.lstsq(A, B, rcond=None)[0]

            e_00s.append(e_00)
            e11s.append(e11)
            delta_es.append(delta_e)

        self.module.model.calibration = (e_00s, e11s, delta_es)