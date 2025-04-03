# cocktail_book_screen.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import QFile, Signal
from PySide6.QtUiTools import QUiLoader


class CocktailBookScreen(QWidget):

    back_to_main = Signal()

    def __init__(self, inventory_db, cocktail_db):
        super().__init__()
        self.inventory_db = inventory_db
        self.cocktail_db = cocktail_db

        layout = QVBoxLayout()

        # # Title
        # layout.addWidget(QLabel("Cocktail Book"))

        # List widget to display makeable cocktails
        self.list_cocktails = QListWidget()
        layout.addWidget(self.list_cocktails)

        # Button to go back
        #write me

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
