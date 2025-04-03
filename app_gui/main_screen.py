# main_screen.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QFile, Signal, QSize
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt


class MainScreen(QWidget):
    # Signal to tell MainWindow to switch screens
    open_cocktail_book = Signal()

    def __init__(self, inventory_db, cocktail_db):
        super().__init__()
        self.inventory_db = inventory_db
        self.cocktail_db = cocktail_db

        # Load the .ui file

        loader = QUiLoader()
        ui_file = QFile("app_gui/main_screen.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # set size and name
        self.setMinimumSize(640, 530)
        self.setStyleSheet("""
            background-color: #000000;
            color: #ffffff;
        """)

        # Button: connect signal
        self.btnMake = self.ui.findChild(QPushButton, "btnMake")  # IOT open cocktail book
        self.btnMake.setStyleSheet("""
            QPushButton {
                border: none;
                background-image: url(app_gui/images/book_icon.png);
                background-repeat: no-repeat;
                background-position: center;
                background-origin: content;
            }
        """)

        # self.btnMake.setStyleSheet("""    hover shit
        # QPushButton:hover {
        #     background-color: #222;
        # }
        # QPushButton:pressed {
        #  background-color: #444;
        # }
        # """)
        self.btnMake.setIcon(QIcon("app_gui/images/book.png"))
        self.btnMake.clicked.connect(self.open_cocktail_book.emit)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

        # Show how many cocktails are makeable
        # (We do it in init, but you can do it in a separate refresh method)
        makeable_cocktails = self.cocktail_db.get_makeable_cocktails(self.inventory_db.cache)

        # Set the text into the label
        lbl = self.ui.findChild(QWidget, "lbl_can_make")
        if lbl:
            lbl.setText(f"cocktails you can make {len(makeable_cocktails)}")
        else:
            print("⚠️ QLabel 'lblMakeable' not found in .ui file")
