import logging
import numpy as np
import json
from serial.tools.list_ports import comports
from PyQt6 import QtSerialPort
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from nqrduck.module.module_controller import ModuleController
from .model import S11Data

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
        """Connect to the specified device. 
        
        Args:
            device (str): The device port to connect to."""
        logger.debug("Connecting to device %s", device)
        try:
            self.module.model.serial = QtSerialPort.QSerialPort(device, baudRate=self.BAUDRATE, readyRead=self.on_ready_read)
            self.module.model.serial.open(QtSerialPort.QSerialPort.OpenModeFlag.ReadWrite)


            
            logger.debug("Connected to device %s", device)
        except Exception as e:
            logger.error("Could not connect to device %s: %s", device, e)

    def start_frequency_sweep(self, start_frequency : str, stop_frequency : str) -> None:
        """ This starts a frequency sweep on the device in the specified range.
        The minimum start and stop frequency are specific to the AD4351 based frequency generator.
        
        Args:
            start_frequency (str): The start frequency in MHz.
            stop_frequency (str): The stop frequency in MHz.

        """
        FREQUENCY_STEP = 50000 # Hz
        MIN_FREQUENCY = 35e6 # Hz
        MAX_FREQUENCY = 300e6 # Hz

        try:
            start_frequency = float(start_frequency) * 1e6
            stop_frequency = float(stop_frequency) * 1e6
        except ValueError:
            error = "Could not start frequency sweep. Start and stop frequency must be floats"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        if start_frequency > stop_frequency:
            error = "Could not start frequency sweep. Start frequency must be smaller than stop frequency"
            logger.error(error)
            self.module.view.add_info_text(error)
            return
        
        if start_frequency < 0 or stop_frequency < 0:
            error = "Could not start frequency sweep. Start and stop frequency must be positive"
            logger.error(error)
            self.module.view.add_info_text(error)
            return
        
        if start_frequency < MIN_FREQUENCY or stop_frequency > MAX_FREQUENCY:
            error = "Could not start frequency sweep. Start and stop frequency must be between %s and %s MHz" % (MIN_FREQUENCY / 1e6, MAX_FREQUENCY / 1e6)
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        logger.debug("Starting frequency sweep from %s to %s with step size %s", start_frequency, stop_frequency, FREQUENCY_STEP)
        # We create the frequency sweep spinner dialog
        self.module.model.clear_data_points()
        self.module.view.create_frequency_sweep_spinner_dialog()
        # Print the command 'f<start>f<stop>' to the serial connection
        try:
            command = "f%sf%sf%s" % (start_frequency, stop_frequency, FREQUENCY_STEP)
            self.module.model.serial.write(command.encode('utf-8'))
        except AttributeError:
            logger.error("Could not start frequency sweep. No device connected.")
            self.module.view.frequency_sweep_spinner.hide()


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
                self.module.model.measurement = S11Data(self.module.model.data_points.copy())
                self.module.view.frequency_sweep_spinner.hide()
            # If the text starts with 'r' and a short calibration is active we know that the data is a short calibration
            elif text.startswith("r") and self.module.model.active_calibration == "short":
                logger.debug("Short calibration finished")
                self.module.model.short_calibration = S11Data(self.module.model.data_points.copy())
                self.module.model.active_calibration = None
                self.module.view.frequency_sweep_spinner.hide()
            # If the text starts with 'r' and an open calibration is active we know that the data is an open calibration
            elif text.startswith("r") and self.module.model.active_calibration == "open":
                logger.debug("Open calibration finished")
                self.module.model.open_calibration = S11Data(self.module.model.data_points.copy())
                self.module.model.active_calibration = None
                self.module.view.frequency_sweep_spinner.hide()
            # If the text starts with 'r' and a load calibration is active we know that the data is a load calibration
            elif text.startswith("r") and self.module.model.active_calibration == "load":
                logger.debug("Load calibration finished")
                self.module.model.load_calibration = S11Data(self.module.model.data_points.copy())
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

        @TODO: Make calibration useful. Right now the calibration does not work for the probe coils. It completly messes up the S11 data.
        For 50 Ohm reference loads the calibration makes the S11 data usable - one then gets a flat line at -50 dB.
        The problem is probably two things:
        1. The ideal values for open, short and load  should be measured with a VNA and then be loaded for the calibration. 
        The ideal values are probably not -1, 1 and 0 but will also show frequency dependent behaviour.
        2 The AD8302 chip only returns the absolute value of the phase. One would probably need to calculate the phase with various algorithms found in the literature.
        Though Im not sure if these proposed algorithms would work for the AD8302 chip.
        """
        logger.debug("Calculating calibration")
        # First we check if the short and open calibration data points are available
        if self.module.model.short_calibration == None:
            logger.error("Could not calculate calibration. No short calibration data points available.")
            return
        if self.module.model.open_calibration == None:
            logger.error("Could not calculate calibration. No open calibration data points available.")
            return
        if self.module.model.load_calibration == None:
            logger.error("Could not calculate calibration. No load calibration data points available.")
            return
        
        # Then we calculate the calibration
        ideal_gamma_short = -1
        ideal_gamma_open = 1
        ideal_gamma_load = 0

        measured_gamma_short = self.module.model.short_calibration.gamma
        measured_gamma_open = self.module.model.open_calibration.gamma
        measured_gamma_load = self.module.model.load_calibration.gamma

        E_Ds = []
        E_Ss = []
        E_ts = []
        for gamma_s, gamma_o, gamma_l in zip(measured_gamma_short, measured_gamma_open, measured_gamma_load):
            # This is the solution from 
            # A = np.array([
            #      [1, ideal_gamma_short * gamma_s, -ideal_gamma_short],
            #      [1, ideal_gamma_open * gamma_o, -ideal_gamma_open],
            #      [1, ideal_gamma_load * gamma_l, -ideal_gamma_load]
            #  ])

            # B = np.array([gamma_s, gamma_o, gamma_l])

            # Solve the system
            # e_00, e11, delta_e = np.linalg.lstsq(A, B, rcond=None)[0]

            E_D = gamma_l
            E_ = (2 * gamma_l - (gamma_s  + gamma_o)) / (gamma_s - gamma_o)
            E_S = (2 * (gamma_o + gamma_l) * (gamma_s + gamma_l)) / (gamma_s - gamma_o)

            E_Ds.append(E_D)
            E_Ss.append(E_S)
            E_ts.append(E_)
            # e_00 = gamma_l # Because here the reflection coefficient should be 0

            # e11 = (gamma_o + gamma_o - 2 * e_00) / (gamma_o - gamma_s)

            # delta_e = -gamma_o + gamma_o* e11 + e_00

            # e_00s.append(e_00)
            # e11s.append(e11)
            # delta_es.append(delta_e)

        self.module.model.calibration = (E_Ds, E_Ss, E_ts)

    def export_calibration(self, filename: str) -> None:
        """This method is called when the export calibration button is pressed.
        It exports the data of the short, open and load calibration to a file.

        Args:
            filename (str): The filename of the file to export to.
        """
        logger.debug("Exporting calibration")
        # First we check if the short and open calibration data points are available
        if self.module.model.short_calibration == None:
            logger.error("Could not export calibration. No short calibration data points available.")
            return
        
        if self.module.model.open_calibration == None:
            logger.error("Could not export calibration. No open calibration data points available.")
            return
        
        if self.module.model.load_calibration == None:
            logger.error("Could not export calibration. No load calibration data points available.")
            return

        # Then we export the different calibrations as a json file
        data = {
            "short": self.module.model.short_calibration.to_json(),
            "open": self.module.model.open_calibration.to_json(),
            "load": self.module.model.load_calibration.to_json()
        }

        with open(filename, "w") as f:
            json.dump(data, f)

    def import_calibration(self, filename: str) -> None:
        """This method is called when the import calibration button is pressed.
        It imports the data of the short, open and load calibration from a file.

        Args:
            filename (str): The filename of the file to import from.
        """
        logger.debug("Importing calibration")

        # We import the different calibrations from a json file
        with open(filename, "r") as f:
            data = json.load(f)
            self.module.model.short_calibration = S11Data.from_json(data["short"])
            self.module.model.open_calibration = S11Data.from_json(data["open"])
            self.module.model.load_calibration = S11Data.from_json(data["load"])

    def set_voltages(self, tuning_voltage : str, matching_voltage : str) -> None:
        """This method is called when the set voltages button is pressed.
        It writes the specified tuning and matching voltage to the serial connection.
        
        Args:
            tuning_voltage (str): The tuning voltage in V.
            matching_voltage (str): The matching voltage in V.
        """
        logger.debug("Setting voltages")
        MAX_VOLTAGE = 5 # V
        try:
            tuning_voltage = float(tuning_voltage)
            matching_voltage = float(matching_voltage)
        except ValueError:
            error = "Could not set voltages. Tuning and matching voltage must be floats"
            logger.error(error)
            self.module.view.add_info_text(error)
            return
        
        if tuning_voltage < 0 or matching_voltage < 0:
            error = "Could not set voltages. Tuning and matching voltage must be positive"
            logger.error(error)
            self.module.view.add_info_text(error)
            return
        
        if tuning_voltage > MAX_VOLTAGE or matching_voltage > MAX_VOLTAGE:
            error = "Could not set voltages. Tuning and matching voltage must be between 0 and 5 V"
            logger.error(error)
            self.module.view.add_info_text(error)
            return
        
        logger.debug("Setting tuning voltage to %s V and matching voltage to %s V", tuning_voltage, matching_voltage)
        try:
            command = "v%sv%s" % (matching_voltage, tuning_voltage)
            self.module.model.serial.write(command.encode('utf-8'))
        except AttributeError:
            logger.error("Could not set voltages. No device connected.")
