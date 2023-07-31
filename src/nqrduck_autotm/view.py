import logging
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSlot
from nqrduck.module.module_view import ModuleView
from .widget import Ui_Form

logger = logging.getLogger(__name__)

class AutoTMView(ModuleView):

    def __init__(self, module):
        super().__init__(module)

        widget = QWidget()
        self._ui_form = Ui_Form()
        self._ui_form.setupUi(self)
        self.widget = widget

        # On clicking of the refresh button scan for available usb devices
        self._ui_form.refreshButton.clicked.connect(self.module.controller.find_devices)

        # Connect the available devices changed signal to the on_available_devices_changed slot
        self.module.model.available_devices_changed.connect(self.on_available_devices_changed)

    @pyqtSlot(list)
    def on_available_devices_changed(self, available_devices):
        """Update the available devices list in the view. """
        logger.debug("Updating available devices list")
        self._ui_form.portBox.clear()
        self._ui_form.portBox.addItems(available_devices)
        logger.debug("Updated available devices list")