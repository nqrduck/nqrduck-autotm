from PyQt6.QtCore import pyqtSignal
from nqrduck.module.module_model import ModuleModel

class AutoTMModel(ModuleModel):
    available_devices_changed = pyqtSignal(list)

    @property
    def available_devices(self):
        return self._available_devices
    
    @available_devices.setter
    def available_devices(self, value):
        self._available_devices = value
        self.available_devices_changed.emit(value)
