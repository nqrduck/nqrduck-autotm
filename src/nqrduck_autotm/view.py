import logging
from datetime import datetime
import cmath
from PyQt6.QtSerialPort import QSerialPort
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QDialog,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
)
from PyQt6.QtCore import pyqtSlot, Qt
from nqrduck.module.module_view import ModuleView
from nqrduck.contrib.mplwidget import MplWidget
from nqrduck.assets.icons import Logos
from nqrduck.assets.animations import DuckAnimations
from .widget import Ui_Form
from .model import S11Data

logger = logging.getLogger(__name__)


class AutoTMView(ModuleView):
    def __init__(self, module):
        super().__init__(module)

        widget = QWidget()
        self._ui_form = Ui_Form()
        self._ui_form.setupUi(self)
        self.widget = widget

        self.frequency_sweep_spinner = self.LoadingSpinner(self)
        self.frequency_sweep_spinner.hide()

        # Disable the connectButton while no devices are selected
        self._ui_form.connectButton.setDisabled(True)
        self._ui_form.decreaseButton.setEnabled(False)
        self._ui_form.increaseButton.setEnabled(False)
        self._ui_form.absoluteGoButton.setEnabled(False)

        # On clicking of the refresh button scan for available usb devices
        self._ui_form.refreshButton.clicked.connect(self.module.controller.find_devices)

        # Connect the available devices changed signal to the on_available_devices_changed slot
        self.module.model.available_devices_changed.connect(
            self.on_available_devices_changed
        )

        # Connect the serial changed signal to the on_serial_changed slot
        self.module.model.serial_changed.connect(self.on_serial_changed)

        # On clicking of the connect button call the connect method
        self._ui_form.connectButton.clicked.connect(self.on_connect_button_clicked)

        # On clicking of the start button call the start_frequency_sweep method
        self._ui_form.startButton.clicked.connect(
            lambda: self.module.controller.start_frequency_sweep(
                self._ui_form.startEdit.text(), self._ui_form.stopEdit.text()
            )
        )

        # On clicking of the generateLUTButton call the generate_mechanical_lut method
        self._ui_form.generateLUTButton.clicked.connect(
            lambda: self.module.controller.generate_electrical_lut(
                self._ui_form.startfrequencyBox.text(),
                self._ui_form.stopfrequencyBox.text(),
                self._ui_form.frequencystepBox.text(),
            )
        )

        # On clicking of the generateLUTButton call the generate_electrical_lut method
        self._ui_form.mechLUTButton.clicked.connect(
            lambda: self.module.controller.generate_mechanical_lut(
                self._ui_form.startfrequencyBox.text(),
                self._ui_form.stopfrequencyBox.text(),
                self._ui_form.frequencystepBox.text(),
            )
        )

        # On clicking of the viewLUTButton call the view_lut method
        self._ui_form.viewelLUTButton.clicked.connect(self.view_el_lut)

        self._ui_form.viewmechLUTButton.clicked.connect(self.view_mech_lut)

        # On clicking of the setvoltagesButton call the set_voltages method
        self._ui_form.setvoltagesButton.clicked.connect(
            lambda: self.module.controller.set_voltages(
                self._ui_form.tuningBox.text(), self._ui_form.matchingBox.text()
            )
        )

        # On clicking of the calibration button call the on_calibration_button_clicked method
        self._ui_form.calibrationButton.clicked.connect(
            self.on_calibration_button_clicked
        )

        # On clicking of the switchpreampButton call the switch_preamp method
        self._ui_form.switchpreampButton.clicked.connect(
            self.module.controller.switch_to_preamp
        )

        # On clicking of the switchATMButton call the switch_atm method
        self._ui_form.switchATMButton.clicked.connect(
            self.module.controller.switch_to_atm
        )

        # On clicking of the homingButton call the homing method
        self._ui_form.homeButton.clicked.connect(self.module.controller.homing)

        # Connect the measurement finished signal to the plot_measurement slot
        self.module.model.measurement_finished.connect(self.plot_measurement)

        # Add a vertical layout to the info box
        self._ui_form.scrollAreaWidgetContents.setLayout(QVBoxLayout())
        self._ui_form.scrollAreaWidgetContents.layout().setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        # Add button Icons
        self._ui_form.startButton.setIcon(Logos.Play_16x16())
        self._ui_form.startButton.setIconSize(self._ui_form.startButton.size())

        # Stepper selection
        self._ui_form.stepperselectBox.currentIndexChanged.connect(lambda: self.module.controller.on_stepper_changed(self._ui_form.stepperselectBox.currentText()))
        self._ui_form.increaseButton.clicked.connect(lambda: self.module.controller.on_relative_move(self._ui_form.stepsizeBox.text()))
        self._ui_form.decreaseButton.clicked.connect(lambda: self.module.controller.on_relative_move("-" + self._ui_form.stepsizeBox.text()))

        self._ui_form.absoluteGoButton.clicked.connect(lambda: self.module.controller.on_absolute_move(self._ui_form.absoluteposBox.text()))

        # Active  stepper changed
        self.module.model.active_stepper_changed.connect(self.on_active_stepper_changed)

        # Position Button
        self._ui_form.positionButton.clicked.connect(self.on_position_button_clicked)

        # Import  and export buttons

        self._ui_form.exportButton.setIcon(Logos.Save16x16())
        self._ui_form.exportButton.setIconSize(self._ui_form.exportButton.size())
        self._ui_form.exportButton.clicked.connect(self.on_export_button_clicked)

        self._ui_form.importButton.setIcon(Logos.Load16x16())
        self._ui_form.importButton.setIconSize(self._ui_form.importButton.size())
        self._ui_form.importButton.clicked.connect(self.on_import_button_clicked)

        self.init_plot()
        self.init_labels()

    def init_labels(self) -> None:
        """Makes some of the labels bold for better readability."""
        self._ui_form.tmsettingsLabel.setStyleSheet("font-weight: bold;")
        self._ui_form.titleconnectionLabel.setStyleSheet("font-weight: bold;")
        self._ui_form.titlefrequencyLabel.setStyleSheet("font-weight: bold;")
        self._ui_form.titletypeLabel.setStyleSheet("font-weight: bold;")
        self._ui_form.titleinfoLabel.setStyleSheet("font-weight: bold;")

    def init_plot(self) -> None:
        """Initialize the S11 plot."""
        ax = self._ui_form.S11Plot.canvas.ax
        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("S11 (dB)", loc="center")
        ax.set_title("S11")
        ax.grid(True)
        ax.set_xlim(0, 100)
        ax.set_ylim(-100, 0)
        self._ui_form.S11Plot.canvas.draw()

        self.phase_ax = self._ui_form.S11Plot.canvas.ax.twinx()

    def on_calibration_button_clicked(self) -> None:
        """This method is called when the calibration button is clicked.
        It opens the calibration window.
        """
        logger.debug("Calibration button clicked")
        self.calibration_window = self.CalibrationWindow(self.module, self)
        self.calibration_window.show()

    @pyqtSlot(list)
    def on_available_devices_changed(self, available_devices: list) -> None:
        """Update the available devices list in the view."""
        logger.debug("Updating available devices list")
        self._ui_form.portBox.clear()
        self._ui_form.portBox.addItems(available_devices)
        # Enable the connectButton if there are available devices
        if available_devices:
            self._ui_form.connectButton.setEnabled(True)
        else:
            self._ui_form.connectButton.setEnabled(False)
        logger.debug("Updated available devices list")

    def on_stepper_changed():
        """Update the stepper position label according to the current stepper position."""
        logger.debug("Updating stepper position label")

    @pyqtSlot()
    def on_connect_button_clicked(self) -> None:
        """This method is called when the connect button is clicked.
        It calls the connect method of the controller with the currently selected device.
        """
        logger.debug("Connect button clicked")
        selected_device = self._ui_form.portBox.currentText()
        self.module.controller.handle_connection(selected_device)

    @pyqtSlot(QSerialPort)
    def on_serial_changed(self, serial: QSerialPort) -> None:
        """Update the serial 'connectionLabel' according to the current serial connection.

        Args:
            serial (serial.Serial): The current serial connection."""
        logger.debug("Updating serial connection label")
        if serial.isOpen():
            self._ui_form.connectionLabel.setText(serial.portName())
            self.add_info_text("Connected to device %s" % serial.portName())
            # Change the connectButton to a disconnectButton
            self._ui_form.connectButton.setText("Disconnect")
        else:
            self._ui_form.connectionLabel.setText("Disconnected")
            self.add_info_text("Disconnected from device")
            self._ui_form.connectButton.setText("Connect")

        logger.debug("Updated serial connection label")

    @pyqtSlot()
    def on_active_stepper_changed(self) -> None:
        """Update the stepper position label according to the current stepper position."""
        logger.debug("Updating stepper position label")
        self._ui_form.stepperposLabel.setText(str(self.module.model.active_stepper.position))
        logger.debug("Updated stepper position label")

        # Only allow position change when stepper is  homed
        if self.module.model.active_stepper.homed:
            self._ui_form.decreaseButton.setEnabled(True)
            self._ui_form.increaseButton.setEnabled(True)
            self._ui_form.absoluteGoButton.setEnabled(True)
            self._ui_form.positionButton.setEnabled(True)
            self._ui_form.mechLUTButton.setEnabled(True)
            self._ui_form.viewmechLUTButton.setEnabled(True)
        else:
            self._ui_form.decreaseButton.setEnabled(False)
            self._ui_form.increaseButton.setEnabled(False)
            self._ui_form.absoluteGoButton.setEnabled(False)
            self._ui_form.positionButton.setEnabled(False)
            self._ui_form.mechLUTButton.setEnabled(False)
            self._ui_form.viewmechLUTButton.setEnabled(False)

    @pyqtSlot()
    def on_position_button_clicked(self) -> None:
        """This method is called when the position button is clicked.
        It opens the position window.
        """
        logger.debug("Position button clicked")
        self.position_window = self.StepperSavedPositionsWindow(self.module, self)
        self.position_window.show()

    def plot_measurement(self, data: "S11Data") -> None:
        """Update the S11 plot with the current data points.

        Args:
            data_points (list): List of data points to plot.

        @TODO: implement proper calibration. See the controller class for more information.
        """
        frequency = data.frequency
        return_loss_db = data.return_loss_db
        phase = data.phase_deg

        gamma = data.gamma

        self._ui_form.S11Plot.canvas.ax.clear()

        magnitude_ax = self._ui_form.S11Plot.canvas.ax
        magnitude_ax.clear()

        self.phase_ax.clear()
        logger.debug("Shape of phase: %s", phase.shape)

        # Calibration for visualization happens here.
        if self.module.model.calibration is not None:
            calibration = self.module.model.calibration
            e_00 = calibration[0]
            e11 = calibration[1]
            delta_e = calibration[2]

            gamma_corr = [
                (data_point - e_00[i]) / (data_point * e11[i] - delta_e[i])
                for i, data_point in enumerate(gamma)
            ]

            return_loss_db_corr = [
                -20 * cmath.log10(abs(g + 1e-12)) for g in gamma_corr
            ]
            magnitude_ax.plot(frequency, return_loss_db_corr, color="red")

        else:
            magnitude_ax.plot(frequency, return_loss_db, color="blue")

        self.phase_ax.yaxis.tick_right()
        self.phase_ax.yaxis.set_label_position("right")
        self.phase_ax.set_ylabel("Phase (deg)")
        self.phase_ax.plot(frequency, phase, color="orange", linestyle="--")
        # self.phase_ax.invert_yaxis()

        magnitude_ax.set_xlabel("Frequency (MHz)")
        magnitude_ax.set_ylabel("S11 (dB)")
        magnitude_ax.set_title("S11")
        magnitude_ax.grid(True)

        # make the y axis go down instead of up
        magnitude_ax.invert_yaxis()

        self._ui_form.S11Plot.canvas.draw()
        self._ui_form.S11Plot.canvas.flush_events()
        # Wait for the signals to be processed before adding the info text
        QApplication.processEvents()

    def add_info_text(self, text: str) -> None:
        """Adds text to the info text box.

        Args:
            text (str): Text to add to the info text box.
        """
        # Add a timestamp to the text
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = "[%s] %s" % (timestamp, text)
        text_label = QLabel(text)
        text_label.setStyleSheet("font-size: 25px;")
        self._ui_form.scrollAreaWidgetContents.layout().addWidget(text_label)
        self._ui_form.scrollArea.verticalScrollBar().setValue(
            self._ui_form.scrollArea.verticalScrollBar().maximum()
        )

    def add_error_text(self, text: str) -> None:
        """Adds text to the error text box.

        Args:
            text (str): Text to add to the error text box.
        """
        message_widget = QWidget()
        message_widget.setLayout(QHBoxLayout())

        error_icon = QLabel()
        error_icon.setPixmap(
            Logos.Error_16x16().pixmap(Logos.Error_16x16().availableSizes()[0])
        )
        # Add a timestamp to the text
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = "[%s] %s" % (timestamp, text)
        text_label = QLabel(text)
        text_label.setStyleSheet("font-size: 25px; color: red;")

        message_widget.layout().addWidget(error_icon)
        message_widget.layout().addWidget(text_label)

        self._ui_form.scrollAreaWidgetContents.layout().addWidget(message_widget)
        self._ui_form.scrollArea.verticalScrollBar().setValue(
            self._ui_form.scrollArea.verticalScrollBar().maximum()
        )

    def create_frequency_sweep_spinner_dialog(self) -> None:
        """Creates a frequency sweep spinner dialog."""
        self.frequency_sweep_spinner = self.LoadingSpinner("Performing frequency sweep ...", self)
        self.frequency_sweep_spinner.show()

    def create_el_LUT_spinner_dialog(self) -> None:
        """Creates a electrical LUT spinner dialog."""
        self.el_LUT_spinner = self.LoadingSpinner("Generating electrical LUT ...", self)
        self.el_LUT_spinner.show()

    def create_mech_LUT_spinner_dialog(self) -> None:
        """Creates a mechanical LUT spinner dialog."""
        self.mech_LUT_spinner = self.LoadingSpinner("Generating mechanical LUT ...", self)
        self.mech_LUT_spinner.show()

    def view_el_lut(self) -> None:
        """Creates a new Dialog that shows the currently active electrical LUT."""
        logger.debug("View LUT")
        if self.module.model.el_lut is None:
            logger.debug("No LUT available")
            self.add_error_text("No LUT available")
            return
        self.lut_window = self.LutWindow(self.module)
        self.lut_window.show()

    def view_mech_lut(self) -> None:
        """Creates a new Dialog that shows the currently active mechanical LUT."""
        logger.debug("View mechanical LUT")
        if self.module.model.mech_lut is None:
            logger.debug("No LUT available")
            self.add_error_text("No LUT available")
            return
        self.lut_window = self.LutWindow(self.module)
        self.lut_window.show()

    @pyqtSlot()
    def on_export_button_clicked(self) -> None:
        """Slot for when the export button is clicked."""
        logger.debug("Export button clicked")
        file_manager = self.QFileManager(S11Data.FILE_EXTENSION, parent=self.widget)
        file_name = file_manager.saveFileDialog()
        if file_name:
            self.module.controller.save_measurement(file_name)

    @pyqtSlot()
    def on_import_button_clicked(self) -> None:
        """Slot for when the import button is clicked."""
        logger.debug("Import button clicked")
        file_manager = self.QFileManager(S11Data.FILE_EXTENSION, parent=self.widget)
        file_name = file_manager.loadFileDialog()
        if file_name:
            self.module.controller.load_measurement(file_name)

    class StepperSavedPositionsWindow(QDialog):
        def __init__(self, module, parent=None):
            super().__init__(parent)
            self.setParent(parent)
            self.module = module
            self.setWindowTitle("Saved positions")
            # make window larger
            self.resize(800, 800)

            # Add vertical main layout
            main_layout = QVBoxLayout()

            # Create table widget
            self.table_widget = QTableWidget()
            self.table_widget.setColumnCount(5)
            self.table_widget.setHorizontalHeaderLabels(
                ["Frequency (MHz)", "Tuning Position", "Matching Position", "Button", "Delete"]
            )

            self.table_widget.setColumnWidth(0, 150)
            self.table_widget.setColumnWidth(1, 200)
            self.table_widget.setColumnWidth(2, 200)
            self.table_widget.setColumnWidth(3, 100)
            self.table_widget.setColumnWidth(4, 100)
            self.on_saved_positions_changed()

            # Add a 'Load Position' button (File selector)
            load_position_button = QPushButton("Load Positions File")
            load_position_button.clicked.connect(self.on_load_position_button_clicked)
            main_layout.addWidget(load_position_button)

            # Add a 'Save Position' button (File selector)
            save_position_button = QPushButton("Save Positions File")
            save_position_button.clicked.connect(self.on_save_position_button_clicked)
            main_layout.addWidget(save_position_button)

            # Add a 'New Position' button
            new_position_button = QPushButton("New Position")
            new_position_button.clicked.connect(self.on_new_position_button_clicked)
            main_layout.addWidget(new_position_button)

            # Add table widget to main layout
            main_layout.addWidget(self.table_widget)

            # On saved positions changed
            self.module.model.saved_positions_changed.connect(self.on_saved_positions_changed)


            self.setLayout(main_layout)

        def file_selector(self, mode) -> str:
            """Opens a file selector and returns the selected file."""
            filedialog = QFileDialog()
            if mode == "load":
                filedialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            elif mode == "save":
                filedialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            filedialog.setNameFilter("position files (*.pos)")
            filedialog.setDefaultSuffix("pos")
            filedialog.exec()
            filename = filedialog.selectedFiles()[0]
            return filename

        def on_load_position_button_clicked(self) -> None:
            """File picker for loading a position from a file."""
            filename = self.file_selector("load")
            logger.debug("Loading position from %s" % filename)
            self.module.controller.load_positions(filename)

        def on_save_position_button_clicked(self) -> None:
            """File picker for saving a position to a file."""
            filename = self.file_selector("save")
            logger.debug("Saving position to %s" % filename)
            self.module.controller.save_positions(filename)

        def on_new_position_button_clicked(self) -> None:
            """Opens a new position dialog."""
            logger.debug("New position button clicked")
            self.new_position_window = self.NewPositionWindow(self.module, self)
            self.new_position_window.show()


        def on_saved_positions_changed(self) -> None:
            """This method is called when the saved positions changed.
            It updates the table widget.
            """
            logger.debug("Updating saved positions table")
            self.table_widget.clearContents()
            self.table_widget.setRowCount(0)

            for row, position in enumerate(self.module.model.saved_positions):
                self.table_widget.insertRow(row)
                self.table_widget.setItem(row, 0, QTableWidgetItem(str(position.frequency)))
                self.table_widget.setItem(
                    row, 1, QTableWidgetItem(position.tuning_position)
                )
                self.table_widget.setItem(
                    row, 2, QTableWidgetItem(position.matching_position)
                )
                go_button = QPushButton("Go")
                go_button.clicked.connect(
                    lambda _, position=position: self.module.controller.on_go_to_position(
                        position
                    )
                )
                self.table_widget.setCellWidget(row, 3, go_button)

                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(
                    lambda _, position=position: self.module.controller.on_delete_position(
                        position
                    )
                )
                self.table_widget.setCellWidget(row, 4, delete_button)
                
            logger.debug("Updated saved positions table")

        class NewPositionWindow(QDialog):
            def __init__(self, module, parent=None):
                super().__init__(parent)
                self.setParent(parent)
                self.module = module
                self.setWindowTitle("New Position")

                # Add vertical main layout
                main_layout = QVBoxLayout()

                # Add horizontal layout for the frequency range
                frequency_layout = QHBoxLayout()
                main_layout.addLayout(frequency_layout)
                frequency_label = QLabel("Frequency")
                frequency_layout.addWidget(frequency_label)
                frequency_edit = QLineEdit()
                frequency_layout.addWidget(frequency_edit)
                unit_label = QLabel("MHz")
                frequency_layout.addWidget(unit_label)
                frequency_layout.addStretch()

                # Add horizontal layout for the calibration type
                type_layout = QHBoxLayout()
                main_layout.addLayout(type_layout)

                # Add vertical layout for short calibration
                tuning_layout = QVBoxLayout()
                tuning_label = QLabel("Tuning Position")
                tuning_layout.addWidget(tuning_label)
                tuning_edit = QLineEdit()
                tuning_layout.addWidget(tuning_edit)
                type_layout.addLayout(tuning_layout)

                # Add vertical layout for open calibration
                matching_layout = QVBoxLayout()
                matching_label = QLabel("Matching Position")
                matching_layout.addWidget(matching_label)
                matching_edit = QLineEdit()
                matching_layout.addWidget(matching_edit)
                type_layout.addLayout(matching_layout)

                # Add vertical layout for save calibration
                data_layout = QVBoxLayout()
                # Apply button
                apply_button = QPushButton("Apply")
                apply_button.clicked.connect(lambda: self.on_apply_button_clicked(frequency_edit.text(), tuning_edit.text(), matching_edit.text()))
                data_layout.addWidget(apply_button)

                main_layout.addLayout(data_layout)

                self.setLayout(main_layout)

            def on_apply_button_clicked(self, frequency: str, tuning_position: str, matching_position: str) -> None:
                """This method is called when the apply button is clicked."""
                self.module.controller.add_position(frequency, tuning_position, matching_position)
                # Close the calibration window
                self.close()
    class LoadingSpinner(QDialog):
        """This class implements a spinner dialog that is shown during a frequency sweep."""

        def __init__(self, text : str, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Loading")
            self.setModal(True)
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            self.spinner_movie = DuckAnimations.DuckSleep128x128()
            self.spinner_label = QLabel(self)
            self.spinner_label.setMovie(self.spinner_movie)

            self.layout = QVBoxLayout(self)
            self.layout.addWidget(QLabel(text))
            self.layout.addWidget(self.spinner_label)

            self.spinner_movie.start()

    class LutWindow(QDialog):
        def __init__(self, module, parent=None):
            super().__init__()
            self.module = module
            self.setParent(parent)
            self.setWindowTitle("LUT")

            # Set  size
            self.resize(800, 800)

            # Add vertical main layout
            main_layout = QVBoxLayout()

            LUT = self.module.model.LUT

            # Create table widget
            self.table_widget = QTableWidget()
            self.table_widget.setColumnCount(4)
            self.table_widget.setColumnWidth(0, 150)
            self.table_widget.setColumnWidth(1, 200)
            self.table_widget.setColumnWidth(2, 200)
            self.table_widget.setColumnWidth(3, 100)

            if LUT.TYPE == "Mechanical":
                self.table_widget.setHorizontalHeaderLabels(
                    ["Frequency (MHz)", "Tuning Position", "Matching Position"]
                )
            elif LUT.TYPE == "Electrical":
                self.table_widget.setHorizontalHeaderLabels(
                    ["Frequency (MHz)", "Tuning Voltage", "Matching Voltage"]
                )
            
            for row, frequency in enumerate(LUT.data.keys()):
                self.table_widget.insertRow(row)
                self.table_widget.setItem(row, 0, QTableWidgetItem(str(frequency)))
                self.table_widget.setItem(
                    row, 1, QTableWidgetItem(str(LUT.data[frequency][0]))
                )
                self.table_widget.setItem(
                    row, 2, QTableWidgetItem(str(LUT.data[frequency][1]))
                )

                # Button to test the specific entry in the LUT
                test_button = QPushButton("Test")
                # For electrical probe coils the matching voltage is the first entry in the LUT
                if LUT.TYPE == "Electrical":
                    tuning_voltage = str(LUT.data[frequency][0])
                    matching_voltage = str(LUT.data[frequency][1])
                    test_button.clicked.connect(
                        lambda _, tuning_voltage=tuning_voltage, matching_voltage=matching_voltage: self.module.controller.set_voltages(
                            tuning_voltage, matching_voltage
                        )
                    )
                # For mechanical probe coils the tuning voltage is the first entry in the LUT
                elif LUT.TYPE == "Mechanical":
                    tuning_position = str(LUT.data[frequency][0])
                    matching_position = str(LUT.data[frequency][1])
                    test_button.clicked.connect(
                        lambda _, tuning_position=tuning_position, matching_position=matching_position: self.module.controller.go_to_position(
                            tuning_position, matching_position
                        )
                    )
                
                self.table_widget.setCellWidget(row, 3, test_button)

            # Add table widget to main layout
            main_layout.addWidget(self.table_widget)
            self.setLayout(main_layout)

        def test_lut(self):
            """This method is called when the Test LUT button is clicked. It sets all of the voltages from the lut with a small delay.
            One can then view the matching on a seperate VNA.
            """
            # This should be in the controller
            for frequency in self.module.model.LUT.data.keys():
                tuning_voltage = str(self.module.model.LUT.data[frequency][1])
                matching_voltage = str(self.module.model.LUT.data[frequency][0])
                self.module.controller.set_voltages(tuning_voltage, matching_voltage)

    class CalibrationWindow(QDialog):
        def __init__(self, module, parent=None):
            super().__init__(parent)
            self.setParent(parent)
            self.module = module
            self.setWindowTitle("Calibration")

            # Add vertical main layout
            main_layout = QVBoxLayout()

            # Add horizontal layout for the frequency range
            frequency_layout = QHBoxLayout()
            main_layout.addLayout(frequency_layout)
            frequency_label = QLabel("Frequency range")
            frequency_layout.addWidget(frequency_label)
            start_edit = QLineEdit()
            start_edit.setPlaceholderText("Start")
            frequency_layout.addWidget(start_edit)
            stop_edit = QLineEdit()
            stop_edit.setPlaceholderText("Stop")
            frequency_layout.addWidget(stop_edit)
            unit_label = QLabel("MHz")
            frequency_layout.addWidget(unit_label)
            frequency_layout.addStretch()

            # Add horizontal layout for the calibration type
            type_layout = QHBoxLayout()
            main_layout.addLayout(type_layout)

            # Add vertical layout for short calibration
            short_layout = QVBoxLayout()
            short_button = QPushButton("Short")
            short_button.clicked.connect(
                lambda: self.module.controller.on_short_calibration(
                    start_edit.text(), stop_edit.text()
                )
            )
            # Short plot widget
            self.short_plot = MplWidget()
            short_layout.addWidget(self.short_plot)
            short_layout.addWidget(short_button)
            type_layout.addLayout(short_layout)

            # Add vertical layout for open calibration
            open_layout = QVBoxLayout()
            open_button = QPushButton("Open")
            open_button.clicked.connect(
                lambda: self.module.controller.on_open_calibration(
                    start_edit.text(), stop_edit.text()
                )
            )
            # Open plot widget
            self.open_plot = MplWidget()
            open_layout.addWidget(self.open_plot)
            open_layout.addWidget(open_button)
            type_layout.addLayout(open_layout)

            # Add vertical layout for load calibration
            load_layout = QVBoxLayout()
            load_button = QPushButton("Load")
            load_button.clicked.connect(
                lambda: self.module.controller.on_load_calibration(
                    start_edit.text(), stop_edit.text()
                )
            )
            # Load plot widget
            self.load_plot = MplWidget()
            load_layout.addWidget(self.load_plot)
            load_layout.addWidget(load_button)
            type_layout.addLayout(load_layout)

            # Add vertical layout for save calibration
            data_layout = QVBoxLayout()
            # Export button
            export_button = QPushButton("Export")
            export_button.clicked.connect(self.on_export_button_clicked)
            data_layout.addWidget(export_button)
            # Import button
            import_button = QPushButton("Import")
            import_button.clicked.connect(self.on_import_button_clicked)
            data_layout.addWidget(import_button)
            # Apply button
            apply_button = QPushButton("Apply calibration")
            apply_button.clicked.connect(self.on_apply_button_clicked)
            data_layout.addWidget(apply_button)

            main_layout.addLayout(data_layout)

            self.setLayout(main_layout)

            # Connect the calibration finished signals to the on_calibration_finished slot
            self.module.model.short_calibration_finished.connect(
                self.on_short_calibration_finished
            )
            self.module.model.open_calibration_finished.connect(
                self.on_open_calibration_finished
            )
            self.module.model.load_calibration_finished.connect(
                self.on_load_calibration_finished
            )

        def on_short_calibration_finished(self, short_calibration: "S11Data") -> None:
            self.on_calibration_finished("short", self.short_plot, short_calibration)

        def on_open_calibration_finished(self, open_calibration: "S11Data") -> None:
            self.on_calibration_finished("open", self.open_plot, open_calibration)

        def on_load_calibration_finished(self, load_calibration: "S11Data") -> None:
            self.on_calibration_finished("load", self.load_plot, load_calibration)

        def on_calibration_finished(
            self, type: str, widget: MplWidget, data: "S11Data"
        ) -> None:
            """This method is called when a calibration has finished.
            It plots the calibration data on the given widget.
            """
            frequency = data.frequency
            return_loss_db = data.return_loss_db
            phase = data.phase_deg

            phase_ax = widget.canvas.ax.twinx()
            phase_ax.set_ylabel("Phase (deg)")
            phase_ax.plot(frequency, phase, color="orange", linestyle="--")
            phase_ax.set_ylim(-180, 180)
            phase_ax.invert_yaxis()

            magnitude_ax = widget.canvas.ax
            magnitude_ax.clear()
            magnitude_ax.set_xlabel("Frequency (MHz)")
            magnitude_ax.set_ylabel("S11 (dB)")
            magnitude_ax.set_title("S11")
            magnitude_ax.grid(True)
            magnitude_ax.plot(frequency, return_loss_db, color="blue")
            # make the y axis go down instead of up
            magnitude_ax.invert_yaxis()

            widget.canvas.draw()
            widget.canvas.flush_events()

        def on_export_button_clicked(self) -> None:
            filedialog = QFileDialog()
            filedialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            filedialog.setNameFilter("calibration files (*.cal)")
            filedialog.setDefaultSuffix("cal")
            filedialog.exec()
            filename = filedialog.selectedFiles()[0]
            logger.debug("Exporting calibration to %s" % filename)
            self.module.controller.export_calibration(filename)

        def on_import_button_clicked(self) -> None:
            """This method is called when the import button is clicked."""
            filedialog = QFileDialog()
            filedialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
            filedialog.setNameFilter("calibration files (*.cal)")
            filedialog.setDefaultSuffix("cal")
            filedialog.exec()
            filename = filedialog.selectedFiles()[0]
            logger.debug("Importing calibration from %s" % filename)
            self.module.controller.import_calibration(filename)

        def on_apply_button_clicked(self) -> None:
            """This method is called when the apply button is clicked."""
            self.module.controller.calculate_calibration()
            # Close the calibration window
            self.close()
