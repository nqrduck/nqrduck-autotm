import cmath
import numpy as np
import logging
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtSerialPort import QSerialPort
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)


class S11Data:
    # Conversion factors - the data is generally sent and received in mV
    # These values are used to convert the data to dB and degrees
    CENTER_POINT_MAGNITUDE = 900  # mV
    CENTER_POINT_PHASE = 1800  # mV
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
    def phase_deg(self):
        """Returns the absolute value of the phase in degrees"""
        return (self.phase_mv - self.CENTER_POINT_PHASE) / self.PHASE_SLOPE

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
        voltage_resolution: float,
    ) -> None:
        self.start_frequency = start_frequency
        self.stop_frequency = stop_frequency
        self.frequency_step = frequency_step
        self.voltage_resolution = voltage_resolution

        # This is the frequency at which the tuning and matching process was started
        self.started_frequency = None

        self.init_voltages()

    def init_voltages(self) -> None:
        """Initialize the lookup table with default values."""
        for frequency in np.arange(
            self.start_frequency, self.stop_frequency, self.frequency_step
        ):
            self.started_frequency = frequency
            self.add_voltages(None, None)

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

    def add_voltages(self, tuning_voltage: float, matching_voltage: float) -> None:
        """Add a tuning and matching voltage for the last started frequency to the lookup table.

        Args:
            tuning_voltage (float): The tuning voltage for the given frequency.
            matching_voltage (float): The matching voltage for the given frequency."""
        self.data[self.started_frequency] = (tuning_voltage, matching_voltage)


class AutoTMModel(ModuleModel):
    available_devices_changed = pyqtSignal(list)
    serial_changed = pyqtSignal(QSerialPort)
    data_points_changed = pyqtSignal(list)

    short_calibration_finished = pyqtSignal(S11Data)
    open_calibration_finished = pyqtSignal(S11Data)
    load_calibration_finished = pyqtSignal(S11Data)
    measurement_finished = pyqtSignal(S11Data)

    def __init__(self, module) -> None:
        super().__init__(module)
        self.data_points = []
        self.active_calibration = None
        self.calibration = None

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
    def measurement(self):
        """The measurement property is used to store the current measurement.
        This is the measurement that is shown in the main S11 plot"""
        return self._measurement

    @measurement.setter
    def measurement(self, value):
        """The measurement value is a tuple of three lists: frequency, return loss and phase."""
        self._measurement = value
        self.measurement_finished.emit(value)

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
