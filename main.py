import sys
from PySide6.QtCore import Qt, QPoint

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QStackedWidget
)

# Imports from your code:
from app_database.cocktail_db import CocktailDB
from app_database.inventory_db import InventoryDB
from app_gui.main_screen import MainScreen
from app_gui.cocktail_book_screen import CocktailBookScreen
from app_gui.bar_screen import BarScreen
from app_gui.title_bar import TitleBar
from utilities import slide_transition


class MainWindow(QMainWindow):
    """Our main window with a custom title bar + stacked widget."""

    def __init__(self):
        super().__init__()

        # --- Window Config ---
        self.setWindowTitle("Elon's app")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)  # finally without white bg
        self.setMinimumSize(640, 530)

        # *** 1) Main container & layout ***
        container = QWidget()
        container.setObjectName("MainContainer")
        container.setStyleSheet("background-color: #1f1f1f; border-radius: 10px;")
        self.setCentralWidget(container)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.titlebar = TitleBar(self)
        main_layout.addWidget(self.titlebar)
        # Hook up go back
        self.titlebar.btnGoBack.clicked.connect(self.goBack)

        # *** 3) Stacked Widget (below the title bar) ***
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)  # 1 = stretch factor

        # *** 4) Database logic + screens ***
        self.inventory_db = InventoryDB()
        self.cocktail_db = CocktailDB()
        self.inventory_db.load_cache()
        self.cocktail_db.load_cache()

        self.main_screen = MainScreen(self.inventory_db, self.cocktail_db)
        self.book_screen = CocktailBookScreen(self.inventory_db, self.cocktail_db)
        self.bar_screen = BarScreen(self.inventory_db)

        self.stacked_widget.addWidget(self.main_screen)  # index 0
        self.stacked_widget.addWidget(self.book_screen)  # index 1
        self.stacked_widget.addWidget(self.bar_screen)  # index 2

        # Hook up signals
        self.main_screen.open_cocktail_book.connect(self.show_book_screen)

        # Default screen
        self.stacked_widget.setCurrentIndex(0)


        # For window dragging
        self.oldPos = QPoint()

        # Apply style
        self.applyStyleSheet()
        self.setStyleSheet("""
            QMainWindow {
                border-radius: 10px;
                background-color: #1f1f1f;
            }
        """)

    def applyStyleSheet(self):
        """Dark theme + styling for the title bar."""
        self.setStyleSheet("""
            QWidget#TitleBar {
                background-color: #333333;
            }
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton#CloseButton:hover {
                background-color: #ff4444;
            }
            QLabel {
                color: white;
            }
        """)

    # *** 6) Navigation ***
    def show_book_screen(self):
        self.book_screen.refresh_cocktail_list()
        # self.stacked_widget.setCurrentWidget(self.book_screen)
        slide_transition(self.stacked_widget, self.stacked_widget.indexOf(self.book_screen))

    def show_main_screen(self):
        # self.stacked_widget.setCurrentWidget(self.main_screen)
        slide_transition(self.stacked_widget, self.stacked_widget.indexOf(self.main_screen))
    def goBack(self):
        print("You clicked Go Back")
        # E.g. go to your main screen or handle custom logic:
        self.show_main_screen()

    # *** 7) Implement window dragging ***
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
