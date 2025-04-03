# bar_screen.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


class BarScreen(QWidget):
    """Replaces your Kivy BarScreen."""

    def __init__(self, inventory_db):
        super().__init__()
        self.inventory_db = inventory_db

        layout = QVBoxLayout()
        layout.addWidget(QLabel("My Bar Inventory Screen"))
        # You could list out the inventory here.
        self.setLayout(layout)

