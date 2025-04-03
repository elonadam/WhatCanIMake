import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget,
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
)
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtCore import Qt
from app_database.cocktail_db import CocktailDB
from app_database.inventory_db import InventoryDB


class MainScreen(QWidget):
    def __init__(self, inventory_db, cocktail_db):
        super().__init__()

        # Load the .ui file
        loader = QUiLoader()
        ui_file = QFile("app_gui/main_screen.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.inventory_db = inventory_db
        self.cocktail_db = cocktail_db
        self.setWindowTitle("Cocktail App")

        # Layout
        layout = QVBoxLayout()


        # Button to navigate to Cocktail Book
        self.btn_open_book = QPushButton("Open Cocktail Book")
        layout.addWidget(self.btn_open_book)

        cocktails_book_button = self.ui.findChild(QWidget, "btnMake")


        # Show how many cocktails are makeable
        # (We do it in init, but you can do it in a separate refresh method)
        makeable_cocktails = self.cocktail_db.get_makeable_cocktails(self.inventory_db.cache)

        # Set the text into the label
        lbl = self.ui.findChild(QWidget, "lbl_can_make")
        if lbl:
            lbl.setText(f"{len(makeable_cocktails)} cocktails you can make")
        else:
            print("⚠️ QLabel 'lblMakeable' not found in .ui file")

        self.setLayout(layout)


class CocktailBookScreen(QWidget):
    """Replaces your Kivy CocktailBookScreen."""

    def __init__(self, inventory_db, cocktail_db):
        super().__init__()
        self.inventory_db = inventory_db
        self.cocktail_db = cocktail_db

        layout = QVBoxLayout()

        # Title
        layout.addWidget(QLabel("Cocktail Book"))

        # List widget to display makeable cocktails
        self.list_cocktails = QListWidget()
        layout.addWidget(self.list_cocktails)

        # Button to go back
        self.btn_back = QPushButton("Back to Main")
        layout.addWidget(self.btn_back)

        self.setLayout(layout)

        # Display cocktails on load
        self.refresh_cocktail_list()

    def refresh_cocktail_list(self):
        self.list_cocktails.clear()
        makeable = self.cocktail_db.get_makeable_cocktails(self.inventory_db.cache)
        if not makeable:
            self.list_cocktails.addItem("No cocktails available.")
        else:
            for c in makeable:
                txt = f"{c['name']} ({c.get('flavor', 'Unknown')})"
                self.list_cocktails.addItem(QListWidgetItem(txt))


class BarScreen(QWidget):
    """Replaces your Kivy BarScreen."""

    def __init__(self, inventory_db):
        super().__init__()
        self.inventory_db = inventory_db

        layout = QVBoxLayout()
        layout.addWidget(QLabel("My Bar Inventory Screen"))
        # You could list out the inventory here.
        self.setLayout(layout)


class MainWindow(QMainWindow):
    """Our main window with a QStackedWidget to switch screens."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cocktail App (PySide6)")

        # 1. Load or initialize your DB logic
        self.inventory_db = InventoryDB()
        self.cocktail_db = CocktailDB()
        self.inventory_db.load_cache()
        self.cocktail_db.load_cache()

        # 2. Create the stacked widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 3. Instantiate each "screen" (QWidget)
        self.main_screen = MainScreen(self.inventory_db, self.cocktail_db)
        self.book_screen = CocktailBookScreen(self.inventory_db, self.cocktail_db)
        self.bar_screen = BarScreen(self.inventory_db)

        # 4. Add them to the stack
        self.stacked_widget.addWidget(self.main_screen)  # index 0
        self.stacked_widget.addWidget(self.book_screen)  # index 1
        self.stacked_widget.addWidget(self.bar_screen)  # index 2

        # 5. Hook up signals: switch screens
        self.main_screen.btn_open_book.clicked.connect(self.show_book_screen)
        self.book_screen.btn_back.clicked.connect(self.show_main_screen)

        # Default to main screen
        self.stacked_widget.setCurrentIndex(0)

    # Navigation
    def show_book_screen(self):
        self.book_screen.refresh_cocktail_list()
        self.stacked_widget.setCurrentWidget(self.book_screen)

    def show_main_screen(self):
        self.stacked_widget.setCurrentWidget(self.main_screen)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
