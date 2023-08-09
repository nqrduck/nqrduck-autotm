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
    CENTER_POINT = 900 # mV
    MAGNITUDE_SLOPE = 30 # dB/mV
    PHASE_SLOPE = 10 # deg/mV

    def __init__(self, data_points : list) -> None:
        self.frequency = np.array([data_point[0] for data_point in data_points])
        self.return_loss_mv = np.array([data_point[1] for data_point in data_points])
        self.phase_mv = np.array([data_point[2] for data_point in data_points])


    @property
    def millivolts(self):
        return self.frequency, self.return_loss_mv, self.phase_mv
    
    @property
    def return_loss_db(self):
        return (self.return_loss_mv - self.CENTER_POINT) / self.MAGNITUDE_SLOPE

    @property
    def phase_deg(self):
        return (self.phase_mv - self.CENTER_POINT) / self.PHASE_SLOPE
    
    @property
    def phase_rad(self):
        return self.phase_deg * cmath.pi / 180
    
    @property
    def gamma(self):
        """Complex reflection coefficient"""
        return cmath.rect(10 ** (-self.return_loss_db / 20), self.phase_rad)

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

    @property
    def available_devices(self):
        return self._available_devices

    @available_devices.setter
    def available_devices(self, value):
        self._available_devices = value
        self.available_devices_changed.emit(value)

    @property
    def serial(self):
        """The serial property is used to store the current serial connection.
        """
        return self._serial

    @serial.setter
    def serial(self, value):
        self._serial = value
        self.serial_changed.emit(value)

    def add_data_point(self, frequency: float, return_loss: float, phase : float) -> None:
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
        self._measurement = S11Data(value)
        self.measurement_finished.emit(self._measurement)

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
        self._short_calibration = S11Data(value)
        self.short_calibration_finished.emit(self._short_calibration)

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
        self._open_calibration = S11Data(value)
        self.open_calibration_finished.emit(self._open_calibration)

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
        self._load_calibration = S11Data(value)
        self.load_calibration_finished.emit(self._load_calibration)

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
    