import sys
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QDialog, QComboBox, QLabel
from PyQt5.QtCore import pyqtSignal

from serial.tools import list_ports

class SerialPortDialog(QDialog):
    port_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Serial Port")
        
        # Create the combo box and button
        self.combo_box = QComboBox()
        self.select_button = QPushButton("Select Port")
        
        # Get available serial ports and populate the combo box
        ports = list_ports.comports()
        for port in ports:
            self.combo_box.addItem(port.device)
        
        # Set up the layout for the dialog
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Available COM Ports:"))
        layout.addWidget(self.combo_box)
        layout.addWidget(self.select_button)
        self.setLayout(layout)
        
        # Connect button to function
        self.select_button.clicked.connect(self.select_port)
    
    def select_port(self):
        selected_port = self.combo_box.currentText()
        self.port_selected.emit(selected_port)
        print(f"Selected port: {selected_port}")
        self.accept()  # Close the dialog