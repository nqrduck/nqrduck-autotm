import serial
import logging
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtSerialPort import QSerialPort
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)

class AutoTMModel(ModuleModel):
    available_devices_changed = pyqtSignal(list)
    serial_changed = pyqtSignal(QSerialPort)
    data_points_changed = pyqtSignal(list)

    short_calibration_finished = pyqtSignal(list)
    open_calibration_finished = pyqtSignal(list)
    load_calibration_finished = pyqtSignal(list)

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
        return self._serial

    @serial.setter
    def serial(self, value):
        self._serial = value
        self.serial_changed.emit(value)

    def add_data_point(self, frequency: float, return_loss: float, phase : float) -> None:
        """Add a data point to the model."""
        self.data_points.append((frequency, return_loss, phase))
        self.data_points_changed.emit(self.data_points)

    def clear_data_points(self) -> None:
        """Clear all data points from the model."""
        self.data_points.clear()
        self.data_points_changed.emit(self.data_points)

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
