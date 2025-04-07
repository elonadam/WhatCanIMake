# main_screen.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
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

        self.btnMake.setIcon(QIcon("app_gui/images/book.png"))
        self.btnMake.clicked.connect(self.open_cocktail_book.emit)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)

        makeable_cocktails = self.cocktail_db.get_makeable_cocktails(self.inventory_db.cache)

        lbl = self.ui.findChild(QLabel, "lbl_num_can_make")
        lbl.setText(f"{len(makeable_cocktails)}")
        #lbl.setAlignment(Qt.AlignCenter)

        lbl = self.ui.findChild(QLabel, "lbl_num_enjoyed")  # the line under work bc use the cache in main
        cocktails_made_so_far = sum(c.get("times_made", 0) for c in self.cocktail_db.cache.values())
        lbl.setText(f"{cocktails_made_so_far}")
        #lbl.setAlignment(Qt.AlignCenter)

        lbl = self.ui.findChild(QLabel, "lbl_num_total")
        lbl.setText(f"{self.inventory_db.count_ingredients()}")
        #lbl.setAlignment(Qt.AlignCenter)






