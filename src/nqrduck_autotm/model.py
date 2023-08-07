import serial
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtSerialPort import QSerialPort
from nqrduck.module.module_model import ModuleModel

class AutoTMModel(ModuleModel):
    available_devices_changed = pyqtSignal(list)
    serial_changed = pyqtSignal(QSerialPort)
    data_points_changed = pyqtSignal(list)
    

    def __init__(self, module) -> None:
        super().__init__(module)
        self.data_points = []

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

    def add_data_point(self, frequency : float, return_loss : float) -> None:
        """Add a data point to the model. """
        self.data_points.append((frequency, return_loss))
        self.data_points_changed.emit(self.data_points)

    def clear_data_points(self) -> None:
        """Clear all data points from the model. """
        self.data_points.clear()
        self.data_points_changed.emit(self.data_points)
