import serial
from PyQt6.QtCore import pyqtSignal
from nqrduck.module.module_model import ModuleModel

class AutoTMModel(ModuleModel):
    available_devices_changed = pyqtSignal(list)
    serial_changed = pyqtSignal(serial.Serial)

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
