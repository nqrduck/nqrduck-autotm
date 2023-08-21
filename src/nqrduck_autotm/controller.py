import logging
import numpy as np
import json
from serial.tools.list_ports import comports
from PyQt6.QtTest import QTest
from PyQt6 import QtSerialPort
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt6.QtWidgets import QApplication
from nqrduck.module.module_controller import ModuleController
from .model import S11Data, LookupTable

logger = logging.getLogger(__name__)


class AutoTMController(ModuleController):
    BAUDRATE = 115200

    def find_devices(self) -> None:
        """Scan for available serial devices and add them to the model as available devices."""
        logger.debug("Scanning for available serial devices")
        ports = comports()
        self.module.model.available_devices = [port.device for port in ports]
        logger.debug("Found %s devices", len(self.module.model.available_devices))
        for device in self.module.model.available_devices:
            logger.debug("Found device: %s", device)

    def handle_connection(self, device: str) -> None:
        """Connect or disconnect to the specified device based on if there already is a connection.

        Args:
            device (str): The device port to connect to.

        @TODO: If the user actually want to connect to another device while already connected to one,
        this would have to be handled differently. But this doesn't really make sense in the current implementation.
        """
        logger.debug("Connecting to device %s", device)
        # If the user has already connected to a device, close the previous connection
        if self.module.model.serial is not None:
            if self.module.model.serial.isOpen():
                logger.debug("Closing previous connection")
                serial = self.module.model.serial
                serial.close()
                self.module.model.serial = serial
            else:
                self.open_connection(device)
        # This is just for the first time the user connects to the device
        else:
            self.open_connection(device)

    def open_connection(self, device: str) -> None:
        """Open a connection to the specified device.

        Args:
            device (str): The device port to connect to.
        """
        try:
            serial = QtSerialPort.QSerialPort(
                device, baudRate=self.BAUDRATE, readyRead=self.on_ready_read
            )
            serial.open(QtSerialPort.QSerialPort.OpenModeFlag.ReadWrite)
            self.module.model.serial = serial

            logger.debug("Connected to device %s", device)
        except Exception as e:
            logger.error("Could not connect to device %s: %s", device, e)

    def start_frequency_sweep(self, start_frequency: str, stop_frequency: str) -> None:
        """This starts a frequency sweep on the device in the specified range.
        The minimum start and stop frequency are specific to the AD4351 based frequency generator.

        Args:
            start_frequency (str): The start frequency in MHz.
            stop_frequency (str): The stop frequency in MHz.

        """
        N_POINTS = 400
        MIN_FREQUENCY = 35e6  # Hz
        MAX_FREQUENCY = 200e6  # Hz

        try:
            start_frequence = start_frequency.replace(",", ".")
            stop_frequency = stop_frequency.replace(",", ".")
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
            error = (
                "Could not start frequency sweep. Start and stop frequency must be between %s and %s MHz"
                % (
                    MIN_FREQUENCY / 1e6,
                    MAX_FREQUENCY / 1e6,
                )
            )
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        frequency_step = (stop_frequency - start_frequency) / N_POINTS
        logger.debug(
            "Starting frequency sweep from %s to %s with step size %s",
            start_frequency,
            stop_frequency,
            frequency_step,
        )
        # We create the frequency sweep spinner dialog
        self.module.model.clear_data_points()
        self.module.view.create_frequency_sweep_spinner_dialog()
        # Print the command 'f<start>f<stop>f<step>' to the serial connection
        command = "f%sf%sf%s" % (start_frequency, stop_frequency, frequency_step)
        self.send_command(command)

    def on_ready_read(self) -> None:
        """This method is called when data is received from the serial connection."""
        serial = self.module.model.serial
        while serial.canReadLine():
            text = serial.readLine().data().decode()
            text = text.rstrip("\r\n")
            # logger.debug("Received data: %s", text)
            # If the text starts with 'f' and the frequency sweep spinner is visible we know that the data is a data point
            # then we have the data for the return loss and the phase at a certain frequency
            if (
                text.startswith("f")
                and self.module.view.frequency_sweep_spinner.isVisible()
            ):
                text = text[1:].split("r")
                frequency = float(text[0])
                return_loss, phase = map(float, text[1].split("p"))
                self.module.model.add_data_point(frequency, return_loss, phase)
            # If the text starts with 'r' and no calibration is active we know that the data is a measurement
            elif text.startswith("r") and self.module.model.active_calibration == None:
                logger.debug("Measurement finished")
                self.module.model.measurement = S11Data(
                    self.module.model.data_points.copy()
                )
                self.module.view.frequency_sweep_spinner.hide()
            # If the text starts with 'r' and a short calibration is active we know that the data is a short calibration
            elif (
                text.startswith("r") and self.module.model.active_calibration == "short"
            ):
                logger.debug("Short calibration finished")
                self.module.model.short_calibration = S11Data(
                    self.module.model.data_points.copy()
                )
                self.module.model.active_calibration = None
                self.module.view.frequency_sweep_spinner.hide()
            # If the text starts with 'r' and an open calibration is active we know that the data is an open calibration
            elif (
                text.startswith("r") and self.module.model.active_calibration == "open"
            ):
                logger.debug("Open calibration finished")
                self.module.model.open_calibration = S11Data(
                    self.module.model.data_points.copy()
                )
                self.module.model.active_calibration = None
                self.module.view.frequency_sweep_spinner.hide()
            # If the text starts with 'r' and a load calibration is active we know that the data is a load calibration
            elif (
                text.startswith("r") and self.module.model.active_calibration == "load"
            ):
                logger.debug("Load calibration finished")
                self.module.model.load_calibration = S11Data(
                    self.module.model.data_points.copy()
                )
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
            # If the text starts with 'v' we know that the data is a voltage sweep result
            elif text.startswith("v"):
                text = text[1:]
                text = text.split("t")
                matching_voltage = float(text[0])
                tuning_voltage = float(text[1])
                # Now we add the datapoint to the current LUT
                LUT = self.module.model.LUT
                logger.debug(
                    "Received voltage sweep result: %s %s",
                    matching_voltage,
                    tuning_voltage,
                )
                LUT.add_voltages(matching_voltage, tuning_voltage)

                # Start the next voltage sweep if there are more voltages to sweep
                if LUT.is_incomplete():
                    next_frequency = LUT.get_next_frequency()
                    command = "s%s" % next_frequency
                    LUT.started_frequency = next_frequency
                    logger.debug("Starting next voltage sweep: %s", command)
                    self.send_command(command)

    def on_short_calibration(
        self, start_frequency: float, stop_frequency: float
    ) -> None:
        """This method is called when the short calibration button is pressed.
        It starts a frequency sweep in the specified range and then starts a short calibration.
        """
        logger.debug("Starting short calibration")
        self.module.model.init_short_calibration()
        self.start_frequency_sweep(start_frequency, stop_frequency)

    def on_open_calibration(
        self, start_frequency: float, stop_frequency: float
    ) -> None:
        """This method is called when the open calibration button is pressed.
        It starts a frequency sweep in the specified range and then starts an open calibration.
        """
        logger.debug("Starting open calibration")
        self.module.model.init_open_calibration()
        self.start_frequency_sweep(start_frequency, stop_frequency)

    def on_load_calibration(
        self, start_frequency: float, stop_frequency: float
    ) -> None:
        """This method is called when the load calibration button is pressed.
        It starts a frequency sweep in the specified range and then loads a calibration.
        """
        logger.debug("Starting load calibration")
        self.module.model.init_load_calibration()
        self.start_frequency_sweep(start_frequency, stop_frequency)

    def calculate_calibration(self) -> None:
        """This method is called when the calculate calibration button is pressed.
        It calculates the calibration from the short, open and calibration data points.

        @TODO: Improvements to the calibrations can be made the following ways:

        1. The ideal values for open, short and load  should be measured with a VNA and then be loaded for the calibration.
        The ideal values are probably not -1, 1 and 0 but will also show frequency dependent behaviour.
        2 The AD8302 chip only returns the absolute value of the phase. One would probably need to calculate the phase with various algorithms found in the literature.
        Though Im not sure if these proposed algorithms would work for the AD8302 chip.
        """
        logger.debug("Calculating calibration")
        # First we check if the short and open calibration data points are available
        if self.module.model.short_calibration == None:
            logger.error(
                "Could not calculate calibration. No short calibration data points available."
            )
            return
        if self.module.model.open_calibration == None:
            logger.error(
                "Could not calculate calibration. No open calibration data points available."
            )
            return
        if self.module.model.load_calibration == None:
            logger.error(
                "Could not calculate calibration. No load calibration data points available."
            )
            return

        # Then we calculate the calibration
        ideal_gamma_short = -1
        ideal_gamma_open = 1
        ideal_gamma_load = 0

        measured_gamma_short = self.module.model.short_calibration.gamma
        measured_gamma_open = self.module.model.open_calibration.gamma
        measured_gamma_load = self.module.model.load_calibration.gamma

        e_00s = []
        e_11s = []
        delta_es = []
        for gamma_s, gamma_o, gamma_l in zip(
            measured_gamma_short, measured_gamma_open, measured_gamma_load
        ):
            # This is the solution from
            A = np.array(
                [
                    [1, ideal_gamma_short * gamma_s, -ideal_gamma_short],
                    [1, ideal_gamma_open * gamma_o, -ideal_gamma_open],
                    [1, ideal_gamma_load * gamma_l, -ideal_gamma_load],
                ]
            )

            B = np.array([gamma_s, gamma_o, gamma_l])

            # Solve the system
            e_00, e11, delta_e = np.linalg.lstsq(A, B, rcond=None)[0]

            e_00s.append(e_00)
            e_11s.append(e11)
            delta_es.append(delta_e)

        self.module.model.calibration = (e_00s, e_11s, delta_es)

    def export_calibration(self, filename: str) -> None:
        """This method is called when the export calibration button is pressed.
        It exports the data of the short, open and load calibration to a file.

        Args:
            filename (str): The filename of the file to export to.
        """
        logger.debug("Exporting calibration")
        # First we check if the short and open calibration data points are available
        if self.module.model.short_calibration == None:
            logger.error(
                "Could not export calibration. No short calibration data points available."
            )
            return

        if self.module.model.open_calibration == None:
            logger.error(
                "Could not export calibration. No open calibration data points available."
            )
            return

        if self.module.model.load_calibration == None:
            logger.error(
                "Could not export calibration. No load calibration data points available."
            )
            return

        # Then we export the different calibrations as a json file
        data = {
            "short": self.module.model.short_calibration.to_json(),
            "open": self.module.model.open_calibration.to_json(),
            "load": self.module.model.load_calibration.to_json(),
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

    def set_voltages(self, tuning_voltage: str, matching_voltage: str) -> None:
        """This method is called when the set voltages button is pressed.
        It writes the specified tuning and matching voltage to the serial connection.

        Args:
            tuning_voltage (str): The tuning voltage in V.
            matching_voltage (str): The matching voltage in V.
        """
        logger.debug("Setting voltages")
        MAX_VOLTAGE = 5  # V
        try:
            tuning_voltage = tuning_voltage.replace(",", ".")
            matching_voltage = matching_voltage.replace(",", ".")
            tuning_voltage = float(tuning_voltage)
            matching_voltage = float(matching_voltage)
        except ValueError:
            error = "Could not set voltages. Tuning and matching voltage must be floats"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        if tuning_voltage < 0 or matching_voltage < 0:
            error = (
                "Could not set voltages. Tuning and matching voltage must be positive"
            )
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        if tuning_voltage > MAX_VOLTAGE or matching_voltage > MAX_VOLTAGE:
            error = "Could not set voltages. Tuning and matching voltage must be between 0 and 5 V"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        logger.debug(
            "Setting tuning voltage to %s V and matching voltage to %s V",
            tuning_voltage,
            matching_voltage,
        )

        command = "v%sv%s" % (matching_voltage, tuning_voltage)
        self.send_command(command)

    def generate_lut(
        self,
        start_frequency: str,
        stop_frequency: str,
        frequency_step: str,
        voltage_resolution: str,
    ) -> None:
        """This method is called when the generate LUT button is pressed.
        It generates a lookup table for the specified frequency range and voltage resolution.

        Args:
            start_frequency (str): The start frequency in Hz.
            stop_frequency (str): The stop frequency in Hz.
            frequency_step (str): The frequency step in Hz.
            voltage_resolution (str): The voltage resolution in V.
        """
        logger.debug("Generating LUT")
        try:
            start_frequency = start_frequency.replace(",", ".")
            stop_frequency = stop_frequency.replace(",", ".")
            frequency_step = frequency_step.replace(",", ".")
            voltage_resolution = voltage_resolution.replace(",", ".")
            start_frequency = float(start_frequency)
            stop_frequency = float(stop_frequency)
            frequency_step = float(frequency_step)
            voltage_resolution = float(voltage_resolution)
        except ValueError:
            error = "Could not generate LUT. Start frequency, stop frequency, frequency step and voltage resolution must be floats"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        if (
            start_frequency < 0
            or stop_frequency < 0
            or frequency_step < 0
            or voltage_resolution < 0
        ):
            error = "Could not generate LUT. Start frequency, stop frequency, frequency step and voltage resolution must be positive"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        if start_frequency > stop_frequency:
            error = "Could not generate LUT. Start frequency must be smaller than stop frequency"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        if frequency_step > (stop_frequency - start_frequency):
            error = "Could not generate LUT. Frequency step must be smaller than the frequency range"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        logger.debug(
            "Generating LUT from %s MHz to %s MHz with a frequency step of %s MHz and a voltage resolution of %s V",
            start_frequency,
            stop_frequency,
            frequency_step,
            voltage_resolution,
        )

        # We create the lookup table
        LUT = LookupTable(
            start_frequency, stop_frequency, frequency_step, voltage_resolution
        )

        LUT.started_frequency = start_frequency
        self.module.model.LUT = LUT

        # We write the first command to the serial connection
        command = "s%s" % (start_frequency)
        self.send_command(command)

    def switch_to_preamp(self) -> None:
        """This method is used to send the command 'cp' to the atm system. This switches the signal pathway of the atm system to 'RX' to 'Preamp'.
        This is the mode for either NQR or NMR measurements or if on wants to check the tuning of the probe coil on a network analyzer.
        """
        logger.debug("Switching to preamp")
        self.send_command("cp")

    def switch_to_atm(self) -> None:
        """This method is used to send the command 'ca' to the atm system. This switches the signal pathway of the atm system to 'RX' to 'ATM.
        In this state the atm system can be used to measure the reflection coefficient of the probecoils.
        """
        logger.debug("Switching to atm")
        self.send_command("ca")

    def send_command(self, command: str) -> None:
        """This method is used to send a command to the active serial connection.

        Args:
            command (str): The command that should be send to the atm system.
        """
        logger.debug("Sending command %s", command)
        try:
            self.module.model.serial.write(command.encode("utf-8"))
            # Wait for 0.5 seconds
            QTest.qWait(500)
            # Make sure that the command is being send
            QApplication.processEvents()
        except AttributeError:
            logger.error("Could not send command. No device connected.")
            self.module.view.add_error_text(
                "Could not send command. No device connected."
            )

    def homing(self) -> None:
        """This method is used to send the command 'h' to the atm system.
        This command is used to home the stepper motors of the atm system.
        """
        logger.debug("Homing")
        self.send_command("h")
