import logging
import serial
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSlot, Qt 
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

        # Disable the connectButton while no devices are selected
        self._ui_form.connectButton.setDisabled(True)

        # On clicking of the refresh button scan for available usb devices
        self._ui_form.refreshButton.clicked.connect(self.module.controller.find_devices)

        # Connect the available devices changed signal to the on_available_devices_changed slot
        self.module.model.available_devices_changed.connect(self.on_available_devices_changed)

        # Connect the serial changed signal to the on_serial_changed slot
        self.module.model.serial_changed.connect(self.on_serial_changed)

        # On clicking of the connect button call the connect method
        self._ui_form.connectButton.clicked.connect(self.on_connect_button_clicked)

        # Add a vertical layout to the info box
        self._ui_form.scrollAreaWidgetContents.setLayout(QVBoxLayout())
        self._ui_form.scrollAreaWidgetContents.layout().setAlignment(Qt.AlignmentFlag.AlignTop)

        self.init_plot()
        self.init_labels()

    def init_labels(self) -> None:
        """Makes some of the labels bold for better readability. 
        """
        self._ui_form.titleconnectionLabel.setStyleSheet("font-weight: bold;")
        self._ui_form.titlefrequencyLabel.setStyleSheet("font-weight: bold;")
        self._ui_form.titletypeLabel.setStyleSheet("font-weight: bold;")
        self._ui_form.titleinfoLabel.setStyleSheet("font-weight: bold;")

    def init_plot(self) -> None:
        """Initialize the S11 plot. """
        ax = self._ui_form.S11Plot.canvas.ax
        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("S11 (dB)")
        ax.set_title("S11")
        ax.grid(True)
        ax.set_xlim(0, 100)
        ax.set_ylim(-100, 0)
        self._ui_form.S11Plot.canvas.draw()

    @pyqtSlot(list)
    def on_available_devices_changed(self, available_devices : list) -> None:
        """Update the available devices list in the view. """
        logger.debug("Updating available devices list")
        self._ui_form.portBox.clear()
        self._ui_form.portBox.addItems(available_devices)
        # Enable the connectButton if there are available devices
        if available_devices:
            self._ui_form.connectButton.setEnabled(True)
        else:
            self._ui_form.connectButton.setEnabled(False)
        logger.debug("Updated available devices list")

    @pyqtSlot()
    def on_connect_button_clicked(self) -> None:
        """This method is called when the connect button is clicked. 
        It calls the connect method of the controller with the currently selected device.
        """
        logger.debug("Connect button clicked")
        selected_device = self._ui_form.portBox.currentText()
        self.module.controller.connect(selected_device)

    @pyqtSlot(serial.Serial)
    def on_serial_changed(self, serial : serial.Serial) -> None:
        """Update the serial 'connectionLabel' according to the current serial connection. 
        
        Args:
            serial (serial.Serial): The current serial connection."""
        logger.debug("Updating serial connection label")
        if serial.is_open:
            self._ui_form.connectionLabel.setText(serial.port)
            self.add_info_text("Connected to device %s" % serial.port)
        else:
            self._ui_form.connectionLabel.setText("Disconnected")
        logger.debug("Updated serial connection label")

    def add_info_text(self, text : str) -> None:
        """ Adds text to the info text box. 
        
        Args:
            text (str): Text to add to the info text box. 
        """
        # Add a timestamp to the text
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = "[%s] %s" % (timestamp, text)
        text_label = QLabel(text)
        text_label.setStyleSheet("font-size: 25px;")
        self._ui_form.scrollAreaWidgetContents.layout().addWidget(text_label)
        self._ui_form.scrollArea.verticalScrollBar().setValue(self._ui_form.scrollArea.verticalScrollBar().maximum())