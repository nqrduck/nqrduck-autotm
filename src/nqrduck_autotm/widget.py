# Form implementation generated from reading ui file '../Modules/nqrduck-autotm/src/nqrduck_autotm/resources/autotm_widget.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1280, 777)
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
        self.titletypeLabel = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setBold(True)
        self.titletypeLabel.setFont(font)
        self.titletypeLabel.setObjectName("titletypeLabel")
        self.verticalLayout_2.addWidget(self.titletypeLabel)
        self.typeTab = QtWidgets.QTabWidget(parent=Form)
        self.typeTab.setObjectName("typeTab")
        self.mechTab = QtWidgets.QWidget()
        self.mechTab.setObjectName("mechTab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.mechTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton = QtWidgets.QPushButton(parent=self.mechTab)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        self.typeTab.addTab(self.mechTab, "")
        self.elecTab = QtWidgets.QWidget()
        self.elecTab.setObjectName("elecTab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.elecTab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.setvoltagesButton = QtWidgets.QPushButton(parent=self.elecTab)
        self.setvoltagesButton.setObjectName("setvoltagesButton")
        self.gridLayout_3.addWidget(self.setvoltagesButton, 3, 0, 1, 2)
        self.stopfrequencyBox = QtWidgets.QDoubleSpinBox(parent=self.elecTab)
        self.stopfrequencyBox.setObjectName("stopfrequencyBox")
        self.gridLayout_3.addWidget(self.stopfrequencyBox, 7, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(parent=self.elecTab)
        font = QtGui.QFont()
        font.setBold(True)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.gridLayout_3.addWidget(self.label_9, 0, 0, 1, 1)
        self.label_14 = QtWidgets.QLabel(parent=self.elecTab)
        self.label_14.setObjectName("label_14")
        self.gridLayout_3.addWidget(self.label_14, 8, 0, 1, 1)
        self.startfrequencyBox = QtWidgets.QDoubleSpinBox(parent=self.elecTab)
        self.startfrequencyBox.setObjectName("startfrequencyBox")
        self.gridLayout_3.addWidget(self.startfrequencyBox, 6, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(parent=self.elecTab)
        font = QtGui.QFont()
        font.setBold(True)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.gridLayout_3.addWidget(self.label_11, 4, 0, 1, 1)
        self.resolutionBox = QtWidgets.QDoubleSpinBox(parent=self.elecTab)
        self.resolutionBox.setObjectName("resolutionBox")
        self.gridLayout_3.addWidget(self.resolutionBox, 5, 1, 1, 1)
        self.matchingBox = QtWidgets.QDoubleSpinBox(parent=self.elecTab)
        self.matchingBox.setObjectName("matchingBox")
        self.gridLayout_3.addWidget(self.matchingBox, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(parent=self.elecTab)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 5, 0, 1, 1)
        self.generateLUTButton = QtWidgets.QPushButton(parent=self.elecTab)
        self.generateLUTButton.setObjectName("generateLUTButton")
        self.gridLayout_3.addWidget(self.generateLUTButton, 9, 0, 1, 2)
        self.frequencystepBox = QtWidgets.QDoubleSpinBox(parent=self.elecTab)
        self.frequencystepBox.setObjectName("frequencystepBox")
        self.gridLayout_3.addWidget(self.frequencystepBox, 8, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(parent=self.elecTab)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(parent=self.elecTab)
        self.label_13.setObjectName("label_13")
        self.gridLayout_3.addWidget(self.label_13, 7, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(parent=self.elecTab)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_12 = QtWidgets.QLabel(parent=self.elecTab)
        self.label_12.setObjectName("label_12")
        self.gridLayout_3.addWidget(self.label_12, 6, 0, 1, 1)
        self.tuningBox = QtWidgets.QDoubleSpinBox(parent=self.elecTab)
        self.tuningBox.setObjectName("tuningBox")
        self.gridLayout_3.addWidget(self.tuningBox, 1, 1, 1, 1)
        self.viewLUTButton = QtWidgets.QPushButton(parent=self.elecTab)
        self.viewLUTButton.setObjectName("viewLUTButton")
        self.gridLayout_3.addWidget(self.viewLUTButton, 10, 0, 1, 2)
        self.typeTab.addTab(self.elecTab, "")
        self.verticalLayout_2.addWidget(self.typeTab)
        self.titlefrequencyLabel = QtWidgets.QLabel(parent=Form)
        font = QtGui.QFont()
        font.setBold(True)
        self.titlefrequencyLabel.setFont(font)
        self.titlefrequencyLabel.setObjectName("titlefrequencyLabel")
        self.verticalLayout_2.addWidget(self.titlefrequencyLabel)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.startEdit = QtWidgets.QLineEdit(parent=Form)
        self.startEdit.setObjectName("startEdit")
        self.gridLayout.addWidget(self.startEdit, 0, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(parent=Form)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 1, 2, 1, 1)
        self.stopEdit = QtWidgets.QLineEdit(parent=Form)
        self.stopEdit.setObjectName("stopEdit")
        self.gridLayout.addWidget(self.stopEdit, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(parent=Form)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 0, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(parent=Form)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 1, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(parent=Form)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 1)
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
        self.titleinfoLabel.setFont(font)
        self.titleinfoLabel.setObjectName("titleinfoLabel")
        self.verticalLayout_2.addWidget(self.titleinfoLabel)
        self.scrollArea = QtWidgets.QScrollArea(parent=Form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 297, 68))
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
        self.titletypeLabel.setText(_translate("Form", "T&M Type:"))
        self.pushButton.setText(_translate("Form", "Homing"))
        self.typeTab.setTabText(self.typeTab.indexOf(self.mechTab), _translate("Form", "Mechanical"))
        self.setvoltagesButton.setText(_translate("Form", "Set Voltages"))
        self.label_9.setText(_translate("Form", "Set Voltages:"))
        self.label_14.setText(_translate("Form", "Frequency Step (MHz)"))
        self.label_11.setText(_translate("Form", "Generate LUT:"))
        self.label_4.setText(_translate("Form", "Voltage Resolution"))
        self.generateLUTButton.setText(_translate("Form", "Start Voltage Sweep"))
        self.label_3.setText(_translate("Form", "Voltage Matching"))
        self.label_13.setText(_translate("Form", "Stop Frequency (MHz)"))
        self.label_2.setText(_translate("Form", "Voltage Tuning"))
        self.label_12.setText(_translate("Form", "Start Frequency (MHz)"))
        self.viewLUTButton.setText(_translate("Form", "View LUT"))
        self.typeTab.setTabText(self.typeTab.indexOf(self.elecTab), _translate("Form", "Electrical"))
        self.titlefrequencyLabel.setText(_translate("Form", "Frequency Sweep:"))
        self.label_8.setText(_translate("Form", "MHz"))
        self.label_6.setText(_translate("Form", "MHz"))
        self.label_7.setText(_translate("Form", "Stop Frequency:"))
        self.label_5.setText(_translate("Form", "Start Frequency:"))
        self.startButton.setText(_translate("Form", "Start Sweep"))
        self.calibrationButton.setText(_translate("Form", "Calibrate"))
        self.pushButton_3.setText(_translate("Form", "T&M Settings"))
        self.titleinfoLabel.setText(_translate("Form", "Info Box:"))
from nqrduck.contrib.mplwidget import MplWidget
