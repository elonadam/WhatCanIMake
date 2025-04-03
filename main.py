import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget,
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
)
from PySide6.QtWidgets import QApplication, QWidget
from app_database.cocktail_db import CocktailDB
from app_database.inventory_db import InventoryDB
from app_gui.main_screen import MainScreen
from app_gui.cocktail_book_screen import CocktailBookScreen
from app_gui.bar_screen import BarScreen

class MainWindow(QMainWindow):
    """Our main window with a QStackedWidget to switch screens."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Elon's app")

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
        self.main_screen.open_cocktail_book.connect(self.show_book_screen)


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
