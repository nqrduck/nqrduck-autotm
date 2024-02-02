import logging
import time
import numpy as np
import json
import time
from serial.tools.list_ports import comports
from PyQt6.QtTest import QTest
from PyQt6 import QtSerialPort
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from nqrduck.module.module_controller import ModuleController
from .model import S11Data, ElectricalLookupTable, MechanicalLookupTable, SavedPosition, Stepper

logger = logging.getLogger(__name__)


class AutoTMController(ModuleController):
    BAUDRATE = 115200

    def on_loading(self):
        """This method is called when the module is loaded.
        It sets up the serial connection and connects the signals and slots.
        """
        logger.debug("Setting up serial connection")
        self.find_devices()

        # Connect signals
        self.module.model.serial_data_received.connect(self.process_frequency_sweep_data)
        self.module.model.serial_data_received.connect(self.process_measurement_data)
        self.module.model.serial_data_received.connect(self.process_calibration_data)
        self.module.model.serial_data_received.connect(self.process_voltage_sweep_result)
        self.module.model.serial_data_received.connect(self.print_info)
        self.module.model.serial_data_received.connect(self.read_position_data)
        self.module.model.serial_data_received.connect(self.process_reflection_data)
        self.module.model.serial_data_received.connect(self.process_position_sweep_result)
        self.module.model.serial_data_received.connect(self.process_signalpath_data)

    @pyqtSlot(str, object)
    def process_signals(self, key: str, value: object) -> None:
        logger.debug("Received signal: %s", key)
        if key == "set_tune_and_match":
            self.tune_and_match(value)

    def tune_and_match(self, frequency: float) -> None:
        """ This method is called when this module already has a LUT table. It should then tune and match the probe coil to the specified frequency.
        """
        if self.module.model.LUT is None:
            logger.error("Could not tune and match. No LUT available.")
            return
        elif self.module.model.LUT.TYPE == "Electrical":
            tuning_voltage, matching_voltage = self.module.model.LUT.get_voltages(frequency)
            confirmation = self.set_voltages(str(tuning_voltage), str(matching_voltage))
            # We need to change the signal pathway to preamp to measure the reflection
            self.switch_to_atm()
            reflection = self.read_reflection(frequency)
            # We need to change the signal pathway back to atm to perform a measurement
            self.switch_to_preamp()
            self.module.nqrduck_signal.emit("confirm_tune_and_match", reflection)

        elif self.module.model.LUT.TYPE == "Mechanical":
            tuning_position, matching_position = self.module.model.LUT.get_positions(frequency)
            self.go_to_position(tuning_position, matching_position)
            self.switch_to_atm()
            # Switch to atm to measure the reflection
            reflection = self.read_reflection(frequency)
            # Switch back to preamp to perform a measurement
            self.switch_to_preamp()

            # The Lime doesn"t like it if we send the command to switch to atm and then immediately send the command to measure the reflection.
            # So we wait a bit before starting the measurement

            QTimer.singleShot(100, lambda: self.module.nqrduck_signal.emit("confirm_tune_and_match", reflection))

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

            # On opening of the command we set the switch position to atm
            self.switch_to_atm()

            self.set_voltages("0", "0")

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
            start_frequency = start_frequency.replace(",", ".")
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

        # Print the command 'f<start>f<stop>f<step>' to the serial connection
        command = "f%sf%sf%s" % (start_frequency, stop_frequency, frequency_step)
        self.module.model.frequency_sweep_start = time.time()
        confirmation = self.send_command(command)
        if confirmation:
            # We create the frequency sweep spinner dialog
            self.module.model.clear_data_points()
            self.module.view.create_frequency_sweep_spinner_dialog()

    @pyqtSlot(str)
    def process_frequency_sweep_data(self, text : str) -> None:
        """This method is called when data is received from the serial connection during a frequency sweep.
        It processes the data and adds it to the model.
        """
        if text.startswith("f") and self.module.view.frequency_sweep_spinner.isVisible():
            text = text[1:].split("r")
            frequency = float(text[0])
            return_loss, phase = map(float, text[1].split("p"))
            self.module.model.add_data_point(frequency, return_loss, phase)

    @pyqtSlot(str)
    def process_measurement_data(self, text : str) -> None:
        """This method is called when data is received from the serial connection during a measurement.
        It processes the data and adds it to the model.
        """
        if self.module.model.active_calibration is None and text.startswith("r"):
            logger.debug("Measurement finished")
            self.module.model.measurement = S11Data(
                self.module.model.data_points.copy()
            )
            self.finish_frequency_sweep()

    @pyqtSlot(str)
    def process_calibration_data(self, text : str) -> None:
        """This method is called when data is received from the serial connection during a calibration.
        It processes the data and adds it to the model.
        
        Args:
            calibration_type (str): The type of calibration that is being performed.
        """
        if text.startswith("r") and self.module.model.active_calibration in ["short", "open", "load"]:
            calibration_type  = self.module.model.active_calibration
            logger.debug(f"{calibration_type.capitalize()} calibration finished")
            setattr(self.module.model, f"{calibration_type}_calibration",
                    S11Data(self.module.model.data_points.copy()))
            self.module.model.active_calibration = None
            self.module.view.frequency_sweep_spinner.hide()

    @pyqtSlot(str)
    def process_voltage_sweep_result(self, text : str) -> None:
        """This method is called when data is received from the serial connection during a voltage sweep.
        It processes the data and adds it to the model.
        
        Args:
            text (str): The data received from the serial connection.
        """
        if text.startswith("v"):
            text = text[1:].split("t")
            tuning_voltage, matching_voltage = map(float, text)
            LUT = self.module.model.el_lut
            if LUT is not None:
                if LUT.is_incomplete():
                        logger.debug("Received voltage sweep result: Tuning %s Matching %s", tuning_voltage, matching_voltage)
                        LUT.add_voltages(tuning_voltage, matching_voltage)
                        self.continue_or_finish_voltage_sweep(LUT)

            self.module.model.tuning_voltage = tuning_voltage
            self.module.model.matching_voltage = matching_voltage
            logger.debug("Updated voltages: Tuning %s Matching %s", self.module.model.tuning_voltage, self.module.model.matching_voltage)

    def finish_frequency_sweep(self):
        """This method is called when a frequency sweep is finished.
        It hides the frequency sweep spinner dialog and adds the data to the model.
        """
        self.module.view.frequency_sweep_spinner.hide()
        self.module.model.frequency_sweep_stop = time.time()
        duration = self.module.model.frequency_sweep_stop - self.module.model.frequency_sweep_start
        self.module.view.add_info_text(f"Frequency sweep finished in {duration:.2f} seconds")

    def continue_or_finish_voltage_sweep(self, LUT):
        """This method is called when a voltage sweep is finished.
        It checks if the voltage sweep is finished or if the next voltage sweep should be started.
        
        Args:
            LUT (LookupTable): The lookup table that is being generated.
        """
        if LUT.is_incomplete():
            # Start the next voltage sweep
            self.start_next_voltage_sweep(LUT)
        else:
            # Finish voltage sweep
            self.finish_voltage_sweep(LUT)

    def start_next_voltage_sweep(self, LUT):
        """This method is called when a voltage sweep is finished.
        It starts the next voltage sweep.
        
        Args:
            LUT (LookupTable): The lookup table that is being generated.
        """
        next_frequency = LUT.get_next_frequency()
        # We write the first command to the serial connection
        if self.module.view._ui_form.prevVoltagecheckBox.isChecked():
            # Command format is s<frequency in MHz>o<optional tuning voltage>o<optional matching voltage>
            # We use the currently set voltages
            command = "s%so%so%s" % (next_frequency, self.module.model.tuning_voltage, self.module.model.matching_voltage)
        else:
            command = "s%s" % (next_frequency)
            
        LUT.started_frequency = next_frequency
        logger.debug("Starting next voltage sweep: %s", command)
        self.send_command(command)

    def finish_voltage_sweep(self, LUT):
        """This method is called when a voltage sweep is finished.
        It hides the voltage sweep spinner dialog and adds the data to the model.
        
        Args:
            LUT (LookupTable): The lookup table that is being generated."""
        logger.debug("Voltage sweep finished")
        self.module.view.el_LUT_spinner.hide()
        self.module.model.LUT = LUT
        self.module.model.voltage_sweep_stop = time.time()
        duration = self.module.model.voltage_sweep_stop - self.module.model.voltage_sweep_start
        self.module.view.add_info_text(f"Voltage sweep finished in {duration:.2f} seconds")
        self.module.nqrduck_signal.emit("LUT_finished", LUT)

    @pyqtSlot(str)
    def print_info(self, text : str) -> None:
        """This method is called when data is received from the serial connection.
        It prints the data to the info text box.

        Args:
            text (str): The data received from the serial connection.
        """
        if text.startswith("i"):
            text = text[1:]
            self.module.view.add_info_text(text)
        elif text.startswith("e"):
            text = text[1:]
            self.module.view.add_error_text(text)
    
    @pyqtSlot(str)
    def read_position_data(self, text : str) -> None:
        """This method is called when data is received from the serial connection."""
        if text.startswith("p"):
            # Format is p<tuning_position>m<matching_position>
            text = text[1:].split("m")
            tuning_position, matching_position = map(int, text)
            self.module.model.tuning_stepper.position = tuning_position
            self.module.model.matching_stepper.position = matching_position
            self.module.model.tuning_stepper.homed = True
            self.module.model.matching_stepper.homed = True
            logger.debug("Tuning position: %s, Matching position: %s", tuning_position, matching_position)
            self.module.view.on_active_stepper_changed()

    def on_ready_read(self) -> None:
        """This method is called when data is received from the serial connection."""
        serial = self.module.model.serial
        
        while serial.canReadLine():
            text = serial.readLine().data().decode().rstrip("\r\n")
            logger.debug("Received data: %s", text)

            self.module.model.serial_data_received.emit(text)

    @pyqtSlot(str)
    def process_reflection_data(self, text):
        """This method is called when data is received from the serial connection.
        It processes the data and adds it to the model.
        
        Args:
            text (str): The data received from the serial connection.
        """
        if text.startswith("m"):
            text = text[1:]
            return_loss, phase = map(float, text.split("p"))
            self.module.model.last_reflection = (return_loss, phase)

    ### Calibration Stuff ###

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

    def save_measurement(self, filename: str) -> None:
        """Save measurement to file.

        Args:
            filename (str): Path to file.
        """
        logger.debug("Saving measurement.")
        if not self.module.model.measurement:
            logger.debug("No measurement to save.")
            return

        measurement = self.module.model.measurement.to_json()

        with open(filename, "w") as f:
            json.dump(measurement, f)

    def load_measurement(self, filename: str) -> None:
        """Load measurement from file.
        
        Args:
            filename (str): Path to file.
        """

        logger.debug("Loading measurement.")

        with open(filename, "r") as f:
            measurement = json.load(f)
            self.module.model.measurement = S11Data.from_json(measurement)

    ### Voltage Control ###

    def set_voltages(self, tuning_voltage: str, matching_voltage: str) -> None:
        """This method is called when the set voltages button is pressed.
        It writes the specified tuning and matching voltage to the serial connection.

        Args:
            tuning_voltage (str): The tuning voltage in V.
            matching_voltage (str): The matching voltage in V.
        """
        logger.debug("Setting voltages")
        MAX_VOLTAGE = 5  # V
        timeout_duration = 15  # timeout in seconds

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

        if tuning_voltage == self.module.model.tuning_voltage and matching_voltage == self.module.model.matching_voltage:
            logger.debug("Voltages already set")
            return
        
        command = "v%sv%s" % (tuning_voltage, matching_voltage)
        
        start_time = time.time()

        confirmation = self.send_command(command)
        while matching_voltage != self.module.model.matching_voltage and tuning_voltage != self.module.model.tuning_voltage:
            QApplication.processEvents()
            # Check for timeout
            if time.time() - start_time > timeout_duration:
                logger.error("Voltage setting timed out")
                break

            logger.debug("Voltages set successfully")
            return confirmation
        else:
            logger.error("Could not set voltages")
            return confirmation
 
    ### Electrical Lookup Table ###

    def generate_electrical_lut(
        self,
        start_frequency: str,
        stop_frequency: str,
        frequency_step: str,
    ) -> None:
        """This method is called when the generate LUT button is pressed.
        It generates a lookup table for the specified frequency range and voltage resolution.

        Args:
            start_frequency (str): The start frequency in Hz.
            stop_frequency (str): The stop frequency in Hz.
            frequency_step (str): The frequency step in Hz.
        """
        logger.debug("Generating LUT")
        try:
            start_frequency = start_frequency.replace(",", ".")
            stop_frequency = stop_frequency.replace(",", ".")
            frequency_step = frequency_step.replace(",", ".")
            start_frequency = float(start_frequency)
            stop_frequency = float(stop_frequency)
            frequency_step = float(frequency_step)
        except ValueError:
            error = "Could not generate LUT. Start frequency, stop frequency, frequency step must be floats"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        if (
            start_frequency < 0
            or stop_frequency < 0
            or frequency_step < 0
        ):
            error = "Could not generate LUT. Start frequency, stop frequency, frequency step must be positive"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        if start_frequency > stop_frequency:
            error = "Could not generate LUT. Start frequency must be smaller than stop frequency"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        # - 0.1 is to prevent float errors
        if frequency_step - 0.1 > (stop_frequency - start_frequency):
            error = "Could not generate LUT. Frequency step must be smaller than the frequency range"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        logger.debug(
            "Generating LUT from %s MHz to %s MHz with a frequency step of %s MHz",
            start_frequency,
            stop_frequency,
            frequency_step,
        )

        self.switch_to_atm()
        # self.set_voltages("0", "0")

        # We create the lookup table
        LUT = ElectricalLookupTable(
            start_frequency, stop_frequency, frequency_step
        )

        LUT.started_frequency = start_frequency

        # We write the first command to the serial connection
        if self.module.view._ui_form.prevVoltagecheckBox.isChecked():
            # Command format is s<frequency in MHz>o<optional tuning voltage>o<optional matching voltage>
            # We use the currently set voltages
            logger.debug("Starting preset Voltage sweep with voltage Tuning: %s V and Matching: %s V", self.module.model.tuning_voltage, self.module.model.matching_voltage)
            command = "s%so%so%s" % (start_frequency, self.module.model.tuning_voltage, self.module.model.matching_voltage)
        else:
            command = "s%s" % (start_frequency)
        
        # For timing of the voltage sweep
        self.module.model.voltage_sweep_start = time.time()
        confirmation = self.send_command(command)
        # If the command was send successfully, we set the LUT 
        if confirmation:
            self.module.model.el_lut = LUT
            self.module.view.create_el_LUT_spinner_dialog()

    def switch_to_preamp(self) -> None:
        """This method is used to send the command 'cp' to the atm system. This switches the signal pathway of the atm system to 'RX' to 'Preamp'.
        This is the mode for either NQR or NMR measurements or if on wants to check the tuning of the probe coil on a network analyzer.
        """
        if self.module.model.signal_path == "preamp":
            logger.debug("Already in preamp")
            return
        
        TIMEOUT = 1  # s
        logger.debug("Switching to preamp")
        self.send_command("cp")

        start_time = time.time()
        while self.module.model.signal_path != "preamp":
            QApplication.processEvents()
            # Check for timeout
            if time.time() - start_time > TIMEOUT:
                logger.error("Switching to preamp timed out")
                break

    def switch_to_atm(self) -> None:
        """This method is used to send the command 'ca' to the atm system. This switches the signal pathway of the atm system to 'RX' to 'ATM.
        In this state the atm system can be used to measure the reflection coefficient of the probecoils.
        """
        if self.module.model.signal_path == "atm":
            logger.debug("Already in atm mode")
            return
        
        TIMEOUT = 1  # s
        logger.debug("Switching to atm")
        self.send_command("ca")

        start_time = time.time()
        while self.module.model.signal_path != "atm":
            QApplication.processEvents()
            # Check for timeout
            if time.time() - start_time > TIMEOUT:
                logger.error("Switching to atm timed out")
                break

    def process_signalpath_data(self, text : str) -> None:
        """This method is called when data is received from the serial connection.
        It processes the data and adds it to the model.
        
        Args:
            text (str): The data received from the serial connection.
        """
        if text.startswith("c"):
            text = text[1:]
            if text == "p":
                self.module.model.signal_path = "preamp"
            elif text == "a":
                self.module.model.signal_path = "atm"

    def send_command(self, command: str) -> bool:
        """This method is used to send a command to the active serial connection.

        Args:
            command (str): The command that should be send to the atm system.

        Returns:
            bool: True if the command was send successfully, False otherwise.
        """
        logger.debug("Sending command %s", command)
        timeout = 10000  # ms

        if self.module.model.serial is None:
            logger.error("Could not send command. No serial connection")
            self.module.view.add_error_text(
                "Could not send command. No serial connection"
            )
            return False

        if self.module.model.serial.isOpen() == False:
            logger.error("Could not send command. Serial connection is not open")
            self.module.view.add_error_text(
                "Could not send command. Serial connection is not open"
            )
            return False

        try:
            self.module.model.serial.write(command.encode("utf-8"))
            # Wait for the confirmation of the command ('c') to be read with a timeout of 1 second

            if not self.module.model.serial.waitForReadyRead(timeout):
                logger.error("Could not send command. Timeout")
                self.module.view.add_error_text("Could not send command. Timeout")
                return False

            confirmation = self.module.model.serial.readLine().data().decode("utf-8")
            logger.debug("Confirmation: %s", confirmation)

            if confirmation == "c":
                logger.debug("Command sent successfully")
                return True
            else:
                logger.error("Could not send command. No confirmation received")
                self.module.view.add_error_text(
                    "Could not send command. No confirmation received"
                )
                return False

        except Exception as e:
            logger.error("Could not send command. %s", e)
            self.module.view.add_error_text("Could not send command. %s" % e)

    ### Stepper Motor Control ###

    def homing(self) -> None:
        """This method is used to send the command 'h' to the atm system.
        This command is used to home the stepper motors of the atm system.
        """
        logger.debug("Homing")
        self.send_command("h")
        self.module.model.tuning_stepper.last_direction = 1
        self.module.model.matching_stepper.last_direction = 1

    @pyqtSlot(str)
    def on_stepper_changed(self, stepper: str) -> None:
        """This method is called when the stepper position is changed.
        It sends the command to the atm system to change the stepper position.

        Args:
            stepper (str): The stepper that is being changed. Either 'tuning' or 'matching'.
        """
        logger.debug("Stepper %s changed", stepper)
        stepper = stepper.lower()
        if stepper == "tuning":
            self.module.model.active_stepper = self.module.model.tuning_stepper
        elif stepper == "matching":
            self.module.model.active_stepper = self.module.model.matching_stepper

    def validate_position(self, future_position: int, stepper  : Stepper) -> bool:
        """Validate the stepper's future position."""
        if future_position < 0:
            self.module.view.add_error_text("Could not move stepper. Stepper position cannot be negative")
            return False

        if future_position > stepper.MAX_STEPS:
            self.module.view.add_error_text(f"Could not move stepper. Stepper position cannot be larger than {stepper.MAX_STEPS}")
            return False

        return True

    def calculate_steps_for_absolute_move(self, target_position: int, stepper : Stepper) -> int:
        """Calculate the number of steps for an absolute move."""
        current_position = stepper.position
        return target_position - current_position

    def send_stepper_command(self, steps: int, stepper : Stepper) -> None:
        """Send a command to the stepper motor based on the number of steps."""
        # Here we handle backlash of the tuner
        # Determine the direction of the current steps
        backlash = 0
        current_direction = np.sign(steps)  # This will be -1,or 1
        if stepper.TYPE == "Tuning":
            logger.debug("Stepper last direction: %s", stepper.last_direction)
            logger.debug("Current direction: %s", current_direction)
            if stepper.last_direction != current_direction:
                backlash = stepper.BACKLASH_STEPS * current_direction

            stepper.last_direction = current_direction
            logger.debug("Stepper last direction: %s", stepper.last_direction)

        motor_identifier = stepper.TYPE.lower()[0]
        command = f"m{motor_identifier}{steps},{backlash}"
        confirmation = self.send_command(command)
        return confirmation

    def on_relative_move(self, steps: str, stepper: Stepper = None) -> None:
        """This method is called when the relative move button is pressed."""
        timeout_duration = 15  # timeout in seconds
        start_time = time.time()

        if stepper is None:
            stepper = self.module.model.active_stepper

        stepper_position = stepper.position
        future_position = stepper.position + int(steps)
        if future_position == stepper_position:
            logger.debug("Stepper already at position")
            return
        
        if self.validate_position(future_position, stepper):
            confirmation = self.send_stepper_command(int(steps), stepper)  # Convert the steps string to an integer

            while stepper_position == stepper.position:
                QApplication.processEvents()
                # Check for timeout
                if time.time() - start_time > timeout_duration:
                    logger.error("Relative move timed out")
                    break  # or handle timeout differently

            return confirmation

    def on_absolute_move(self, steps: str, stepper: Stepper = None) -> None:
        """This method is called when the absolute move button is pressed."""
        timeout_duration = 15  # timeout in seconds
        start_time = time.time()

        if stepper is None:
            stepper = self.module.model.active_stepper

        stepper_position = stepper.position
        future_position = int(steps)

        if future_position == stepper_position:
            logger.debug("Stepper already at position")
            return

        if self.validate_position(future_position, stepper):
            actual_steps = self.calculate_steps_for_absolute_move(future_position, stepper)
            confirmation = self.send_stepper_command(actual_steps, stepper)

            while stepper_position == stepper.position:
                QApplication.processEvents()
                # Check for timeout
                if time.time() - start_time > timeout_duration:
                    logger.error("Absolute move timed out")
                    break  # or handle timeout differently

            return confirmation

    ### Position Saving and Loading ###

    def load_positions(self, path : str) -> None:
        """Load the saved positions from a json file.
        
        Args:
            path (str): The path to the json file.
        """
        # First clear the old positions
        self.module.model.saved_positions = []

        with open(path, "r") as f:
            positions = json.load(f)
            for position in positions:
                logger.debug("Loading position: %s", position)
                self.add_position(position["frequency"], position["tuning_position"], position["matching_position"])


    def save_positions(self, path: str) -> None:
        """Save the current positions to a json file.
        
        Args:
            path (str): The path to the json file.
        """
        positions = self.module.model.saved_positions
        with open(path, "w") as f:
            json_position = [position.to_json() for position in positions]
            json.dump(json_position, f)

    def add_position(self, frequency: str, tuning_position: str, matching_position: str) -> None:
        """Add a position to the lookup table.
        
        Args:
            frequency (str): The frequency of the position.
            tuning_position (str): The tuning position.
            matching_position (str): The matching position.
        """
        logger.debug("Adding new position at %s MHz", frequency)
        self.module.model.add_saved_position(frequency, tuning_position, matching_position)

    def on_go_to_position(self, position: SavedPosition) -> None:
        """Go to the specified position.
        
        Args:
            position (SavedPosition): The position to go to.
        """
        logger.debug("Going to position: %s", position)
        confirmation = self.on_absolute_move(position.tuning_position, self.module.model.tuning_stepper)
        if confirmation:
            self.on_absolute_move(position.matching_position, self.module.model.matching_stepper)

    def on_delete_position(self, position: SavedPosition) -> None:
        """Delete the specified position.
        
        Args:
            position (SavedPosition): The position to delete.
        """
        logger.debug("Deleting position: %s", position)
        self.module.model.delete_saved_position(position)


    #### Mechanical tuning and matching ####

    def generate_mechanical_lut(self, start_frequency: str, stop_frequency: str, frequency_step: str) -> None:
        """Generate a lookup table for the specified frequency range and voltage resolution.
        
        Args:
            start_frequency (str): The start frequency in Hz.
            stop_frequency (str): The stop frequency in Hz.
            frequency_step (str): The frequency step in Hz.
        """
        try:
            start_frequency = start_frequency.replace(",", ".")
            stop_frequency = stop_frequency.replace(",", ".")
            frequency_step = frequency_step.replace(",", ".")
            start_frequency = float(start_frequency)
            stop_frequency = float(stop_frequency)
            frequency_step = float(frequency_step)
        except ValueError:
            error = "Could not generate LUT. Start frequency, stop frequency, frequency step must be floats"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        if (
            start_frequency < 0
            or stop_frequency < 0
            or frequency_step < 0
        ):
            error = "Could not generate LUT. Start frequency, stop frequency, frequency step must be positive"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        if start_frequency > stop_frequency:
            error = "Could not generate LUT. Start frequency must be smaller than stop frequency"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        # - 0.1 is to prevent float errors
        if frequency_step - 0.1 > (stop_frequency - start_frequency):
            error = "Could not generate LUT. Frequency step must be smaller than the frequency range"
            logger.error(error)
            self.module.view.add_info_text(error)
            return

        logger.debug(
            "Generating LUT from %s MHz to %s MHz with a frequency step of %s MHz",
            start_frequency,
            stop_frequency,
            frequency_step,
        )

        self.switch_to_atm()

        # We create the lookup table
        LUT = MechanicalLookupTable(
            start_frequency, stop_frequency, frequency_step
        )

        # Lock GUI
        self.module.view.create_mech_LUT_spinner_dialog()

        self.module.model.mech_lut = LUT

        self.start_next_mechTM(LUT)


    def start_next_mechTM(self, LUT):
        """Start the next mechanical tuning and matching sweep."""

        next_frequency = LUT.get_next_frequency()
        LUT.started_frequency = next_frequency
        logger.debug("Starting next mechanical tuning and matching:")

        # Now we vary the tuning capacitor position and matching capacitor position
        # Step size tuner:
        TUNER_STEP_SIZE = 10
        # Step size matcher:
        MATCHER_STEP_SIZE = 50

        TUNING_RANGE = 40
        MATCHING_RANGE = 500

        tuning_backlash = self.module.model.tuning_stepper.BACKLASH_STEPS
        # I'm not sure about this value ...
        matching_backlash = 0

        # Command for the position sweep: p<frequency in MHz>t<range>,<step size>,<backlash>,<last_direction>m<range>,<step size>,<backlash>,<last_direction>"
        tuning_last_direction = self.module.model.tuning_stepper.last_direction
        matching_last_direction = self.module.model.matching_stepper.last_direction
        command = f"p{next_frequency}t{TUNING_RANGE},{TUNER_STEP_SIZE},{tuning_backlash},{tuning_last_direction}m{MATCHING_RANGE},{MATCHER_STEP_SIZE},{matching_backlash},{matching_last_direction}"

        confirmation = self.send_command(command)

    @pyqtSlot(str)
    def process_position_sweep_result(self, text):
        if text.startswith("z"):
            text = text[1:]
            # Format is z<tuning_position>,<tuning_last_direction>m<matching_position>,<matching_last_direction>
            text = text.split("m")
            tuning_position, tuning_last_direction = map(int, text[0].split(","))
            matching_position, matching_last_direction = map(int, text[1].split(","))

            # Keep backlash compensation consistent
            self.module.model.tuning_stepper.last_direction = tuning_last_direction
            self.module.model.matching_stepper.last_direction = matching_last_direction

            # Update the positions
            self.module.model.tuning_stepper.position = tuning_position
            self.module.model.matching_stepper.position = matching_position
            self.module.view.on_active_stepper_changed()

            logger.debug("Tuning position: %s, Matching position: %s", tuning_position, matching_position)

            LUT = self.module.model.mech_lut
            logger.debug("Received position sweep result: %s %s", matching_position, tuning_position)
            LUT.add_positions(tuning_position, matching_position)
            self.continue_or_finish_position_sweep(LUT)

    def continue_or_finish_position_sweep(self, LUT):
        """Continue or finish the position sweep."""
        if LUT.is_incomplete():
            self.start_next_mechTM(LUT)
        else:
            self.finish_position_sweep(LUT)

    def finish_position_sweep(self, LUT):
        """Finish the position sweep."""
        logger.debug("Finished position sweep")
        self.module.model.mech_lut = LUT
        self.module.model.LUT = LUT
        self.module.view.mech_LUT_spinner.hide()
        self.module.nqrduck_signal.emit("LUT_finished", LUT)

    def go_to_position(self, tuning_position : int, matching_position : int) -> None:
        """Go to the specified position.
        
        Args:
            position (SavedPosition): The position to go to.
        """
        confirmation = self.on_absolute_move(tuning_position, self.module.model.tuning_stepper)
        if confirmation:
            confirmation = self.on_absolute_move(matching_position, self.module.model.matching_stepper)
            if confirmation:
                return True

    
    # This method isn't used anymore but it might be useful in the future so I'll keep it here
    def read_reflection(self, frequency) -> float:
        """Starts a reflection measurement and reads the reflection at the specified frequency."""
        # We send the command to the atm system
        command = f"r{frequency}"
        try:
            confirmation = self.send_command(command)
            QApplication.processEvents()
            if confirmation:
                reflection = self.module.model.last_reflection

                # Set the timeout duration (e.g., 5 seconds)
                timeout_duration = 5
                # Record the start time
                start_time = time.time()

                # Wait for reflection data until the timeout is reached
                while reflection is None:
                    # Check if the timeout has been reached
                    if time.time() - start_time > timeout_duration:
                        logger.error("Reading reflection timed out after %d seconds", timeout_duration)
                        self.module.view.add_error_text(f"Could not read reflection. Timed out after {timeout_duration} seconds")
                        return None

                    # Refresh the reflection data
                    reflection = self.module.model.last_reflection
                    QApplication.processEvents()

                # Reset the reflection cache
                self.module.model.last_reflection = None

                magnitude = reflection[0]
                CENTER_POINT_MAGNITUDE = 900  # mV
                MAGNITUDE_SLOPE = 30  # dB/mV
                magnitude = (magnitude - CENTER_POINT_MAGNITUDE) / MAGNITUDE_SLOPE

                return -magnitude

            else:
                logger.error("Could not read reflection. No confirmation received")
                self.module.view.add_error_text("Could not read reflection. No confirmation received")
                return None

        except Exception as e:
            logger.error("Could not read reflection. %s", e)
            self.module.view.add_error_text(f"Could not read reflection. {e}")
            return None


