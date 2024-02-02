import cmath
import numpy as np
import logging
from scipy.signal import find_peaks
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtSerialPort import QSerialPort
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)


class S11Data:
    FILE_EXTENSION = "s11"
    # Conversion factors - the data is generally sent and received in mV
    # These values are used to convert the data to dB and degrees
    CENTER_POINT_MAGNITUDE = 900  # mV
    CENTER_POINT_PHASE = 0  # mV
    MAGNITUDE_SLOPE = 30  # dB/mV
    PHASE_SLOPE = 10  # deg/mV

    def __init__(self, data_points: list) -> None:
        self.frequency = np.array([data_point[0] for data_point in data_points])
        self.return_loss_mv = np.array([data_point[1] for data_point in data_points])
        self.phase_mv = np.array([data_point[2] for data_point in data_points])

    @property
    def millivolts(self):
        return self.frequency, self.return_loss_mv, self.phase_mv

    @property
    def return_loss_db(self):
        return (
            self.return_loss_mv - self.CENTER_POINT_MAGNITUDE
        ) / self.MAGNITUDE_SLOPE

    @property
    def phase_deg(self, phase_correction=True):
        """Returns the absolute value of the phase in degrees

        Keyword Arguments:
            phase_correction {bool} -- If True, the phase correction is applied. (default: {False})
        """

        phase_deg = (self.phase_mv - self.CENTER_POINT_PHASE) / self.PHASE_SLOPE
        if phase_correction:
            phase_deg = self.phase_correction(self.frequency, phase_deg)

        return phase_deg

    @property
    def phase_rad(self):
        return self.phase_deg * cmath.pi / 180

    @property
    def gamma(self):
        """Complex reflection coefficient"""
        if len(self.return_loss_db) != len(self.phase_rad):
            raise ValueError("return_loss_db and phase_rad must be the same length")

        return [
            cmath.rect(10 ** (-loss_db / 20), phase_rad)
            for loss_db, phase_rad in zip(self.return_loss_db, self.phase_rad)
        ]

    def phase_correction(
        self, frequency_data: np.array, phase_data: np.array
    ) -> np.array:
        """This method fixes the phase sign of the phase data.
        The AD8302 can only measure the absolute value of the phase.
        Therefore we need to correct the phase sign. This can be done via the slope of the phase.
        If the slope is negative, the phase is positive and vice versa.

        Args:
            frequency_data (np.array): The frequency data.
            phase_data (np.array): The phase data.

        Returns:
            np.array: The corrected phase data.
        """
        # First we apply a moving average filter to the phase data
        WINDOW_SIZE = 5
        phase_data_filtered = (
            np.convolve(phase_data, np.ones(WINDOW_SIZE), "same") / WINDOW_SIZE
        )

        # Fix transient response
        phase_data_filtered[: WINDOW_SIZE // 2] = phase_data[: WINDOW_SIZE // 2]
        phase_data_filtered[-WINDOW_SIZE // 2 :] = phase_data[-WINDOW_SIZE // 2 :]

        # Now we find the peaks and valleys of the data
        HEIGHT = 100
        distance = len(phase_data_filtered) / 10

        peaks, _ = find_peaks(phase_data_filtered, distance=distance, height=HEIGHT)

        valleys, _ = find_peaks(
            180 - phase_data_filtered, distance=distance, height=HEIGHT
        )

        # Determine if the first point is a peak or a valley
        if phase_data_filtered[0] > phase_data_filtered[1]:
            peaks = np.insert(peaks, 0, 0)
        else:
            valleys = np.insert(valleys, 0, 0)

        # Determine if the last point is a peak or a valley
        if phase_data_filtered[-1] > phase_data_filtered[-2]:
            peaks = np.append(peaks, len(phase_data_filtered) - 1)
        else:
            valleys = np.append(valleys, len(phase_data_filtered) - 1)

        frequency_peaks = frequency_data[peaks]
        frequency_valleys = frequency_data[valleys]

        # Combine the peaks and valleys
        frequency_peaks_valleys = np.sort(
            np.concatenate((frequency_peaks, frequency_valleys))
        )
        peaks_valleys = np.sort(np.concatenate((peaks, valleys)))

        # Now we can determine the slope of the phase
        # For this we compare the phase of our peaks_valleys array to the next point
        # If the phase is increasing, the slope is positive, if it is decreasing, the slope is negative
        phase_slope = np.zeros(len(peaks_valleys) - 1)
        for i in range(len(peaks_valleys) - 1):
            phase_slope[i] = (
                phase_data_filtered[peaks_valleys[i + 1]]
                - phase_data_filtered[peaks_valleys[i]]
            )

        # Now we can determine the sign of the phase
        # If the slope is negative, the phase is positive and vice versa
        phase_sign = np.sign(phase_slope) * -1

        # Now we can correct the phase for the different sections
        phase_data_corrected = np.zeros(len(phase_data))
        for i in range(len(peaks_valleys) - 1):
            phase_data_corrected[peaks_valleys[i] : peaks_valleys[i + 1]] = (
                phase_data_filtered[peaks_valleys[i] : peaks_valleys[i + 1]]
                * phase_sign[i]
            )

        # Murks: The last point is always wrong so just set it to the previous value
        phase_data_corrected[-1] = phase_data_corrected[-2]

        return phase_data_corrected

    def to_json(self):
        return {
            "frequency": self.frequency.tolist(),
            "return_loss_mv": self.return_loss_mv.tolist(),
            "phase_mv": self.phase_mv.tolist(),
        }

    @classmethod
    def from_json(cls, json):
        f = json["frequency"]
        rl = json["return_loss_mv"]
        p = json["phase_mv"]
        data = [(f[i], rl[i], p[i]) for i in range(len(f))]
        return cls(data)


class LookupTable:
    """This class is used to store a lookup table for tuning and matching of electrical probeheads."""

    data = dict()

    def __init__(
        self,
        start_frequency: float,
        stop_frequency: float,
        frequency_step: float,
    ) -> None:
        self.start_frequency = start_frequency
        self.stop_frequency = stop_frequency
        self.frequency_step = frequency_step

        # This is the frequency at which the tuning and matching process was started
        self.started_frequency = None
    
    def get_entry_number(self, frequency: float) -> int:
        """This method returns the entry number of the given frequency.

        Args:
            frequency (float): The frequency for which the entry number should be returned.

        Returns:
            int: The entry number of the given frequency.
        """
        # Round to closest integer
        return int(round((frequency - self.start_frequency) / self.frequency_step))

class Stepper:

    def __init__(self) -> None:
        self.homed = False
        self.position = 0

class SavedPosition():
    """This class is used to store a saved position for tuning and matching of electrical probeheads."""
    def __init__(self, frequency: float, tuning_position : int, matching_position : int) -> None:
        self.frequency = frequency
        self.tuning_position = tuning_position
        self.matching_position = matching_position

    def to_json(self):
        return {
            "frequency": self.frequency,
            "tuning_position": self.tuning_position,
            "matching_position": self.matching_position,
        }

class TuningStepper(Stepper):
    TYPE = "Tuning"
    MAX_STEPS = 1e6
    BACKLASH_STEPS = 60

    def __init__(self) -> None:
        super().__init__()
        # Backlash stepper 
        self.last_direction = None
    
class MatchingStepper(Stepper):
    TYPE = "Matching"
    MAX_STEPS = 1e6

    BACKLASH_STEPS = 0

    def __init__(self) -> None:
        super().__init__()
        self.last_direction = None

class ElectricalLookupTable(LookupTable):
    TYPE = "Electrical"

    def __init__(self, start_frequency: float, stop_frequency: float, frequency_step: float) -> None:
        super().__init__(start_frequency, stop_frequency, frequency_step)
        self.init_voltages()

    def init_voltages(self) -> None:
        """Initialize the lookup table with default values."""
        for frequency in np.arange(
            self.start_frequency, self.stop_frequency + self.frequency_step, self.frequency_step
        ):
            self.started_frequency = frequency
            self.add_voltages(None, None)

    def add_voltages(self, tuning_voltage: float, matching_voltage: float) -> None:
        """Add a tuning and matching voltage for the last started frequency to the lookup table.

        Args:
            tuning_voltage (float): The tuning voltage for the given frequency.
            matching_voltage (float): The matching voltage for the given frequency."""
        self.data[self.started_frequency] = (tuning_voltage, matching_voltage)

    def get_voltages(self, frequency: float) -> tuple:
        """Get the tuning and matching voltage for the given frequency.

        Args:
            frequency (float): The frequency for which the tuning and matching voltage should be returned.

        Returns:
            tuple: The tuning and matching voltage for the given frequency.
        """
        entry_number = self.get_entry_number(frequency)
        key = list(self.data.keys())[entry_number]
        return self.data[key]
    
    def is_incomplete(self) -> bool:
        """This method returns True if the lookup table is incomplete,
        i.e. if there are frequencies for which no the tuning or matching voltage is none.

        Returns:
            bool: True if the lookup table is incomplete, False otherwise.
        """
        return any(
            [
                tuning_voltage is None or matching_voltage is None
                for tuning_voltage, matching_voltage in self.data.values()
            ]
        )

    def get_next_frequency(self) -> float:
        """This method returns the next frequency for which the tuning and matching voltage is not yet set.

        Returns:
            float: The next frequency for which the tuning and matching voltage is not yet set.
        """

        for frequency, (tuning_voltage, matching_voltage) in self.data.items():
            if tuning_voltage is None or matching_voltage is None:
                return frequency

        return None

class MechanicalLookupTable(LookupTable):
    # Hmm duplicate code
    TYPE = "Mechanical"
    

    def __init__(self, start_frequency: float, stop_frequency: float, frequency_step: float) -> None:
        super().__init__(start_frequency, stop_frequency, frequency_step)
        self.init_positions()

    def init_positions(self) -> None:
        """Initialize the lookup table with default values."""
        for frequency in np.arange(
            self.start_frequency, self.stop_frequency + self.frequency_step, self.frequency_step
        ):
            self.started_frequency = frequency
            self.add_positions(None, None)

    def add_positions(self, tuning_position: int, matching_position: int) -> None:
        """Add a tuning and matching position for the last started frequency to the lookup table.

        Args:
            tuning_position (int): The tuning position for the given frequency.
            matching_position (int): The matching position for the given frequency."""
        self.data[self.started_frequency] = (tuning_position, matching_position)

    def get_positions(self, frequency: float) -> tuple:
        """Get the tuning and matching position for the given frequency.

        Args:
            frequency (float): The frequency for which the tuning and matching position should be returned.

        Returns:
            tuple: The tuning and matching position for the given frequency.
        """
        entry_number = self.get_entry_number(frequency)
        key = list(self.data.keys())[entry_number]
        return self.data[key]
    
    def is_incomplete(self) -> bool:
        """This method returns True if the lookup table is incomplete,
        i.e. if there are frequencies for which no the tuning or matching position is none.

        Returns:
            bool: True if the lookup table is incomplete, False otherwise.
        """
        return any(
            [
                tuning_position is None or matching_position is None
                for tuning_position, matching_position in self.data.values()
            ]
        )
    
    def get_next_frequency(self) -> float:
        """This method returns the next frequency for which the tuning and matching position is not yet set.

        Returns:
            float: The next frequency for which the tuning and matching position is not yet set.
        """

        for frequency, (tuning_position, matching_position) in self.data.items():
            if tuning_position is None or matching_position is None:
                return frequency

        return None
class AutoTMModel(ModuleModel):

    available_devices_changed = pyqtSignal(list)
    serial_changed = pyqtSignal(QSerialPort)
    data_points_changed = pyqtSignal(list)
    active_stepper_changed = pyqtSignal(Stepper)
    saved_positions_changed = pyqtSignal(list)
    serial_data_received = pyqtSignal(str)

    short_calibration_finished = pyqtSignal(S11Data)
    open_calibration_finished = pyqtSignal(S11Data)
    load_calibration_finished = pyqtSignal(S11Data)
    measurement_finished = pyqtSignal(S11Data)

    def __init__(self, module) -> None:
        super().__init__(module)
        self.data_points = []
        self.active_calibration = None
        self.calibration = None
        self.serial = None

        self.tuning_stepper = TuningStepper()
        self.matching_stepper = MatchingStepper()
        self.active_stepper = self.tuning_stepper

        self.saved_positions = []

        self.el_lut = None
        self.mech_lut = None
        self.LUT = None

        self.last_reflection = None

        self.tuning_voltage = None
        self.matching_voltage = None

        # AutoTM system or preamp
        self.signal_path = None

    @property
    def available_devices(self):
        return self._available_devices

    @available_devices.setter
    def available_devices(self, value):
        self._available_devices = value
        self.available_devices_changed.emit(value)

    @property
    def serial(self):
        """The serial property is used to store the current serial connection."""
        return self._serial

    @serial.setter
    def serial(self, value):
        self._serial = value
        self.serial_changed.emit(value)

    def add_data_point(
        self, frequency: float, return_loss: float, phase: float
    ) -> None:
        """Add a data point to the model. These data points are our intermediate data points read in via the serial connection.
        They will be saved in the according properties later on.
        """
        self.data_points.append((frequency, return_loss, phase))
        self.data_points_changed.emit(self.data_points)

    def clear_data_points(self) -> None:
        """Clear all data points from the model."""
        self.data_points.clear()
        self.data_points_changed.emit(self.data_points)

    @property
    def saved_positions(self):
        return self._saved_positions
    
    @saved_positions.setter
    def saved_positions(self, value):
        self._saved_positions = value
        self.saved_positions_changed.emit(value)

    def add_saved_position(self, frequency: float, tuning_position: int, matching_position: int) -> None:
        """Add a saved position to the model."""
        self.saved_positions.append(SavedPosition(frequency, tuning_position, matching_position))
        self.saved_positions_changed.emit(self.saved_positions)

    def delete_saved_position(self, position: SavedPosition) -> None:
        """Delete a saved position from the model."""
        self.saved_positions.remove(position)
        self.saved_positions_changed.emit(self.saved_positions)

    @property
    def measurement(self):
        """The measurement property is used to store the current measurement.
        This is the measurement that is shown in the main S11 plot"""
        return self._measurement

    @measurement.setter
    def measurement(self, value):
        """The measurement value is a tuple of three lists: frequency, return loss and phase."""
        self._measurement = value
        self.measurement_finished.emit(value)

    @property
    def active_stepper(self):
        return self._active_stepper
    
    @active_stepper.setter
    def active_stepper(self, value):
        self._active_stepper = value
        self.active_stepper_changed.emit(value)

    # Calibration properties

    @property
    def active_calibration(self):
        return self._active_calibration

    @active_calibration.setter
    def active_calibration(self, value):
        self._active_calibration = value

    @property
    def short_calibration(self):
        return self._short_calibration

    @short_calibration.setter
    def short_calibration(self, value):
        logger.debug("Setting short calibration")
        self._short_calibration = value
        self.short_calibration_finished.emit(value)

    def init_short_calibration(self):
        """This method is called when a frequency sweep has been started for a short calibration in this way the module knows that the next data points are for a short calibration."""
        self.active_calibration = "short"
        self.clear_data_points()

    @property
    def open_calibration(self):
        return self._open_calibration

    @open_calibration.setter
    def open_calibration(self, value):
        logger.debug("Setting open calibration")
        self._open_calibration = value
        self.open_calibration_finished.emit(value)

    def init_open_calibration(self):
        """This method is called when a frequency sweep has been started for an open calibration in this way the module knows that the next data points are for an open calibration."""
        self.active_calibration = "open"
        self.clear_data_points()

    @property
    def load_calibration(self):
        return self._load_calibration

    @load_calibration.setter
    def load_calibration(self, value):
        logger.debug("Setting load calibration")
        self._load_calibration = value
        self.load_calibration_finished.emit(value)

    def init_load_calibration(self):
        """This method is called when a frequency sweep has been started for a load calibration in this way the module knows that the next data points are for a load calibration."""
        self.active_calibration = "load"
        self.clear_data_points()

    @property
    def calibration(self):
        return self._calibration

    @calibration.setter
    def calibration(self, value):
        logger.debug("Setting calibration")
        self._calibration = value

    @property
    def LUT(self):
        return self._LUT

    @LUT.setter
    def LUT(self, value):
        self._LUT = value

    @property
    def frequency_sweep_start(self):
        """The timestamp for when the frequency sweep has been started. This is used for timing of the frequency sweep."""
        return self._frequency_sweep_start

    @frequency_sweep_start.setter
    def frequency_sweep_start(self, value):
        self._frequency_sweep_start = value

    @property
    def frequency_sweep_end(self):
        """The timestamp for when the frequency sweep has been ended. This is used for timing of the frequency sweep."""
        return self._frequency_sweep_end

    @frequency_sweep_end.setter
    def frequency_sweep_end(self, value):
        self._frequency_sweep_end = value
