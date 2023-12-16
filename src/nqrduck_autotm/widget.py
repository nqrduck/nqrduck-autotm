# Form implementation generated from reading ui file 'Modules/nqrduck-autotm/src/nqrduck_autotm/resources/autotm_widget.ui'
#
# Created by: PyQt6 UI code generator 6.5.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1280, 1089)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.titleconnectionLabel = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.titleconnectionLabel.setFont(font)
        self.titleconnectionLabel.setObjectName("titleconnectionLabel")
        self.verticalLayout_2.addWidget(self.titleconnectionLabel)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.portBox = QtWidgets.QComboBox(parent=Form)
        self.portBox.setObjectName("portBox")
        self.gridLayout_2.addWidget(self.portBox, 0, 1, 1, 1)
        self.refreshButton = QtWidgets.QPushButton(parent=Form)
        self.refreshButton.setObjectName("refreshButton")
        self.gridLayout_2.addWidget(self.refreshButton, 0, 2, 1, 1)
        self.label = QtWidgets.QLabel(parent=Form)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.connectionLabel = QtWidgets.QLabel(parent=Form)
        self.connectionLabel.setText("")
        self.connectionLabel.setObjectName("connectionLabel")
        self.gridLayout_2.addWidget(self.connectionLabel, 1, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(parent=Form)
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 1, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.connectButton = QtWidgets.QPushButton(parent=Form)
        self.connectButton.setObjectName("connectButton")
        self.verticalLayout_2.addWidget(self.connectButton)
        self.tmsettingsLabel = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.tmsettingsLabel.setFont(font)
        self.tmsettingsLabel.setObjectName("tmsettingsLabel")
        self.verticalLayout_2.addWidget(self.tmsettingsLabel)
        self.gridLayout_8 = QtWidgets.QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.stopfrequencyBox = QtWidgets.QDoubleSpinBox(parent=Form)
        self.stopfrequencyBox.setProperty("value", 80.1)
        self.stopfrequencyBox.setObjectName("stopfrequencyBox")
        self.gridLayout_8.addWidget(self.stopfrequencyBox, 1, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(parent=Form)
        self.label_13.setObjectName("label_13")
        self.gridLayout_8.addWidget(self.label_13, 1, 0, 1, 1)
        self.startfrequencyBox = QtWidgets.QDoubleSpinBox(parent=Form)
        self.startfrequencyBox.setProperty("value", 80.0)
        self.startfrequencyBox.setObjectName("startfrequencyBox")
        self.gridLayout_8.addWidget(self.startfrequencyBox, 0, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(parent=Form)
        self.label_12.setObjectName("label_12")
        self.gridLayout_8.addWidget(self.label_12, 0, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(parent=Form)
        self.label_14.setObjectName("label_14")
        self.gridLayout_8.addWidget(self.label_14, 2, 0, 1, 1)
        self.frequencystepBox = QtWidgets.QDoubleSpinBox(parent=Form)
        self.frequencystepBox.setProperty("value", 0.1)
        self.frequencystepBox.setObjectName("frequencystepBox")
        self.gridLayout_8.addWidget(self.frequencystepBox, 2, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_8)
        self.titletypeLabel = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.titletypeLabel.setFont(font)
        self.titletypeLabel.setObjectName("titletypeLabel")
        self.verticalLayout_2.addWidget(self.titletypeLabel)
        self.typeTab = QtWidgets.QTabWidget(parent=Form)
        self.typeTab.setObjectName("typeTab")
        self.mechTab = QtWidgets.QWidget()
        self.mechTab.setObjectName("mechTab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.mechTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.homeButton = QtWidgets.QPushButton(parent=self.mechTab)
        self.homeButton.setObjectName("homeButton")
        self.gridLayout_4.addWidget(self.homeButton, 5, 1, 1, 1)
        self.label_16 = QtWidgets.QLabel(parent=self.mechTab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.gridLayout_4.addWidget(self.label_16, 0, 0, 1, 3)
        self.absoluteposBox = QtWidgets.QSpinBox(parent=self.mechTab)
        self.absoluteposBox.setMaximum(1000000)
        self.absoluteposBox.setObjectName("absoluteposBox")
        self.gridLayout_4.addWidget(self.absoluteposBox, 6, 1, 1, 1)
        self.stepperselectBox = QtWidgets.QComboBox(parent=self.mechTab)
        self.stepperselectBox.setObjectName("stepperselectBox")
        self.stepperselectBox.addItem("")
        self.stepperselectBox.addItem("")
        self.gridLayout_4.addWidget(self.stepperselectBox, 1, 1, 1, 1)
        self.decreaseButton = QtWidgets.QPushButton(parent=self.mechTab)
        self.decreaseButton.setObjectName("decreaseButton")
        self.gridLayout_4.addWidget(self.decreaseButton, 5, 0, 1, 1)
        self.increaseButton = QtWidgets.QPushButton(parent=self.mechTab)
        self.increaseButton.setObjectName("increaseButton")
        self.gridLayout_4.addWidget(self.increaseButton, 5, 2, 1, 1)
        self.label_18 = QtWidgets.QLabel(parent=self.mechTab)
        self.label_18.setObjectName("label_18")
        self.gridLayout_4.addWidget(self.label_18, 1, 0, 1, 1)
        self.label_20 = QtWidgets.QLabel(parent=self.mechTab)
        self.label_20.setObjectName("label_20")
        self.gridLayout_4.addWidget(self.label_20, 6, 0, 1, 1)
        self.stepsizeBox = QtWidgets.QSpinBox(parent=self.mechTab)
        self.stepsizeBox.setMinimum(0)
        self.stepsizeBox.setMaximum(1000000)
        self.stepsizeBox.setProperty("value", 500)
        self.stepsizeBox.setObjectName("stepsizeBox")
        self.gridLayout_4.addWidget(self.stepsizeBox, 3, 1, 1, 1)
        self.label_17 = QtWidgets.QLabel(parent=self.mechTab)
        self.label_17.setObjectName("label_17")
        self.gridLayout_4.addWidget(self.label_17, 3, 0, 1, 1)
        self.absoluteGoButton = QtWidgets.QPushButton(parent=self.mechTab)
        self.absoluteGoButton.setObjectName("absoluteGoButton")
        self.gridLayout_4.addWidget(self.absoluteGoButton, 6, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(parent=self.mechTab)
        self.label_4.setObjectName("label_4")
        self.gridLayout_4.addWidget(self.label_4, 2, 0, 1, 1)
        self.stepperposLabel = QtWidgets.QLabel(parent=self.mechTab)
        self.stepperposLabel.setObjectName("stepperposLabel")
        self.gridLayout_4.addWidget(self.stepperposLabel, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_4)
        self.positionButton = QtWidgets.QPushButton(parent=self.mechTab)
        self.positionButton.setObjectName("positionButton")
        self.verticalLayout.addWidget(self.positionButton)
        self.mechLUTButton = QtWidgets.QPushButton(parent=self.mechTab)
        self.mechLUTButton.setObjectName("mechLUTButton")
        self.verticalLayout.addWidget(self.mechLUTButton)
        self.viewmechLUTButton = QtWidgets.QPushButton(parent=self.mechTab)
        self.viewmechLUTButton.setObjectName("viewmechLUTButton")
        self.verticalLayout.addWidget(self.viewmechLUTButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout.setStretch(1, 1)
        self.typeTab.addTab(self.mechTab, "")
        self.elecTab = QtWidgets.QWidget()
        self.elecTab.setObjectName("elecTab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.elecTab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_9 = QtWidgets.QLabel(parent=self.elecTab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(parent=self.elecTab)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)
        self.matchingBox = QtWidgets.QDoubleSpinBox(parent=self.elecTab)
        self.matchingBox.setObjectName("matchingBox")
        self.gridLayout_3.addWidget(self.matchingBox, 2, 1, 1, 1)
        self.generateLUTButton = QtWidgets.QPushButton(parent=self.elecTab)
        self.generateLUTButton.setObjectName("generateLUTButton")
        self.gridLayout_3.addWidget(self.generateLUTButton, 8, 0, 1, 2)
        self.tuningBox = QtWidgets.QDoubleSpinBox(parent=self.elecTab)
        self.tuningBox.setObjectName("tuningBox")
        self.gridLayout_3.addWidget(self.tuningBox, 1, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(parent=self.elecTab)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridLayout_3.addWidget(self.label_11, 4, 0, 1, 1)
        self.viewelLUTButton = QtWidgets.QPushButton(parent=self.elecTab)
        self.viewelLUTButton.setObjectName("viewelLUTButton")
        self.gridLayout_3.addWidget(self.viewelLUTButton, 10, 0, 1, 2)
        self.setvoltagesButton = QtWidgets.QPushButton(parent=self.elecTab)
        self.setvoltagesButton.setObjectName("setvoltagesButton")
        self.gridLayout_3.addWidget(self.setvoltagesButton, 3, 0, 1, 2)
        self.label_3 = QtWidgets.QLabel(parent=self.elecTab)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 2, 0, 1, 1)
        self.prevVoltagecheckBox = QtWidgets.QCheckBox(parent=self.elecTab)
        self.prevVoltagecheckBox.setObjectName("prevVoltagecheckBox")
        self.gridLayout_3.addWidget(self.prevVoltagecheckBox, 9, 0, 1, 1)
        self.typeTab.addTab(self.elecTab, "")
        self.verticalLayout_2.addWidget(self.typeTab)
        self.rfswitchLabel = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.rfswitchLabel.setFont(font)
        self.rfswitchLabel.setObjectName("rfswitchLabel")
        self.verticalLayout_2.addWidget(self.rfswitchLabel)
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.switchATMButton = QtWidgets.QPushButton(parent=Form)
        self.switchATMButton.setObjectName("switchATMButton")
        self.gridLayout_7.addWidget(self.switchATMButton, 0, 0, 1, 1)
        self.switchpreampButton = QtWidgets.QPushButton(parent=Form)
        self.switchpreampButton.setObjectName("switchpreampButton")
        self.gridLayout_7.addWidget(self.switchpreampButton, 0, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_7)
        self.titlefrequencyLabel = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.titlefrequencyLabel.setFont(font)
        self.titlefrequencyLabel.setObjectName("titlefrequencyLabel")
        self.verticalLayout_2.addWidget(self.titlefrequencyLabel)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.startEdit = QtWidgets.QLineEdit(parent=Form)
        self.startEdit.setObjectName("startEdit")
        self.gridLayout.addWidget(self.startEdit, 0, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(parent=Form)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(parent=Form)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 0, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(parent=Form)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 1)
        self.stopEdit = QtWidgets.QLineEdit(parent=Form)
        self.stopEdit.setObjectName("stopEdit")
        self.gridLayout.addWidget(self.stopEdit, 1, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(parent=Form)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 1, 2, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.startButton = QtWidgets.QPushButton(parent=Form)
        self.startButton.setObjectName("startButton")
        self.verticalLayout_2.addWidget(self.startButton)
        self.calibrationButton = QtWidgets.QPushButton(parent=Form)
        self.calibrationButton.setObjectName("calibrationButton")
        self.verticalLayout_2.addWidget(self.calibrationButton)
        self.pushButton_3 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout_2.addWidget(self.pushButton_3)
        self.titleinfoLabel = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.titleinfoLabel.setFont(font)
        self.titleinfoLabel.setObjectName("titleinfoLabel")
        self.verticalLayout_2.addWidget(self.titleinfoLabel)
        self.scrollArea = QtWidgets.QScrollArea(parent=Form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 291, 83))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.S11Plot = MplWidget(parent=Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.S11Plot.sizePolicy().hasHeightForWidth())
        self.S11Plot.setSizePolicy(sizePolicy)
        self.S11Plot.setObjectName("S11Plot")
        self.verticalLayout_5.addWidget(self.S11Plot)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.importButton = QtWidgets.QPushButton(parent=Form)
        self.importButton.setObjectName("importButton")
        self.verticalLayout_4.addWidget(self.importButton)
        self.exportButton = QtWidgets.QPushButton(parent=Form)
        self.exportButton.setObjectName("exportButton")
        self.verticalLayout_4.addWidget(self.exportButton)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_5.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_5)
        self.horizontalLayout_2.setStretch(1, 1)

        self.retranslateUi(Form)
        self.typeTab.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.titleconnectionLabel.setText(_translate("Form", "Connection Settings:"))
        self.refreshButton.setText(_translate("Form", "Refresh"))
        self.label.setText(_translate("Form", "Port:"))
        self.label_10.setText(_translate("Form", "Connected to:"))
        self.connectButton.setText(_translate("Form", "Connect"))
        self.tmsettingsLabel.setText(_translate("Form", "T&M Settings:"))
        self.label_13.setText(_translate("Form", "Stop Frequency (MHz)"))
        self.label_12.setText(_translate("Form", "Start Frequency (MHz)"))
        self.label_14.setText(_translate("Form", "Frequency Step (MHz)"))
        self.titletypeLabel.setText(_translate("Form", "T&M Type:"))
        self.homeButton.setText(_translate("Form", "Home"))
        self.label_16.setText(_translate("Form", "Stepper Control:"))
        self.stepperselectBox.setItemText(0, _translate("Form", "Tuning"))
        self.stepperselectBox.setItemText(1, _translate("Form", "Matching"))
        self.decreaseButton.setText(_translate("Form", "-"))
        self.increaseButton.setText(_translate("Form", "+"))
        self.label_18.setText(_translate("Form", "Stepper:"))
        self.label_20.setText(_translate("Form", "Absolute:"))
        self.label_17.setText(_translate("Form", "Step Size:"))
        self.absoluteGoButton.setText(_translate("Form", "Go"))
        self.label_4.setText(_translate("Form", "Position:"))
        self.stepperposLabel.setText(_translate("Form", "0"))
        self.positionButton.setText(_translate("Form", "Saved Positions"))
        self.mechLUTButton.setText(_translate("Form", "Generate LUT"))
        self.viewmechLUTButton.setText(_translate("Form", "View LUT"))
        self.typeTab.setTabText(self.typeTab.indexOf(self.mechTab), _translate("Form", "Mechanical"))
        self.label_9.setText(_translate("Form", "Set Voltages:"))
        self.label_2.setText(_translate("Form", "Voltage Tuning"))
        self.generateLUTButton.setText(_translate("Form", "Generate LUT"))
        self.label_11.setText(_translate("Form", "Generate LUT:"))
        self.viewelLUTButton.setText(_translate("Form", "View LUT"))
        self.setvoltagesButton.setText(_translate("Form", "Set Voltages"))
        self.label_3.setText(_translate("Form", "Voltage Matching"))
        self.prevVoltagecheckBox.setText(_translate("Form", "Start from previous Voltage"))
        self.typeTab.setTabText(self.typeTab.indexOf(self.elecTab), _translate("Form", "Electrical"))
        self.rfswitchLabel.setText(_translate("Form", "RF Switch:"))
        self.switchATMButton.setText(_translate("Form", "ATM"))
        self.switchpreampButton.setText(_translate("Form", "Preamplifier"))
        self.titlefrequencyLabel.setText(_translate("Form", "Frequency Sweep:"))
        self.startEdit.setText(_translate("Form", "80"))
        self.label_7.setText(_translate("Form", "Stop Frequency:"))
        self.label_6.setText(_translate("Form", "MHz"))
        self.label_5.setText(_translate("Form", "Start Frequency:"))
        self.stopEdit.setText(_translate("Form", "100"))
        self.label_8.setText(_translate("Form", "MHz"))
        self.startButton.setText(_translate("Form", "Start Sweep"))
        self.calibrationButton.setText(_translate("Form", "Calibrate"))
        self.pushButton_3.setText(_translate("Form", "T&M Settings"))
        self.titleinfoLabel.setText(_translate("Form", "Info Box:"))
        self.importButton.setText(_translate("Form", "Import Measurement"))
        self.exportButton.setText(_translate("Form", "Export  Measurement"))
from nqrduck.contrib.mplwidget import MplWidget
