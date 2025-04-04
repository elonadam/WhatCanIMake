# cocktail_book_screen.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QLineEdit
from PySide6.QtCore import QFile, Signal
from PySide6.QtUiTools import QUiLoader


class CocktailBookScreen(QWidget):
    back_to_main = Signal()

    def __init__(self, inventory_db, cocktail_db):
        super().__init__()
        self.inventory_db = inventory_db
        self.cocktail_db = cocktail_db
        self.all_cocktails = self.cocktail_db.get_makeable_cocktails(self.inventory_db.cache)

        self.search_text = ""
        self.show_favorites = False
        self.show_easy = False
        self.show_tasty = False

        # 1. Load .ui
        loader = QUiLoader()
        ui_file = QFile("app_gui/cocktail_book_screen.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # 2. Set layout - maybe to hide this question mark
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)

        # 3. Find widgets by objectName
        self.btn_back = self.ui.findChild(QPushButton, "btn_back")  # not showing
        self.lbl_title = self.ui.findChild(QLabel, "lbl_title")
        self.name_search = self.ui.findChild(QLineEdit, "name_search")
        self.btn_favorites = self.ui.findChild(QPushButton, "btn_favorites")
        self.btn_easy = self.ui.findChild(QPushButton, "btn_easy")
        self.btn_tasty = self.ui.findChild(QPushButton, "btn_tasty")
        self.list_cocktails = self.ui.findChild(QListWidget, "list_cocktails")

        # 4. Connect signals
        self.name_search.textChanged.connect(self.handle_search)
        self.btn_favorites.clicked.connect(self.toggle_favorites)
        self.btn_easy.clicked.connect(self.toggle_easy)
        self.btn_tasty.clicked.connect(self.toggle_tasty)

        # 5. Initialize
        self.apply_style()  # optional
        self.refresh_cocktail_list()

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
            background-color: #1f1f1f;
            color: #ffffff;
        }
        
        QWidget#MainContainer {
            background-color: #1f1f1f;
        }
        
        QWidget#TitleBar {
            background-color: #1a1a1a;
        }

        QLineEdit {
            background-color: #333333;
            border: 1px solid #444444;
            border-radius: 6px;
            padding: 6px;
        }

        QListWidget {
            background-color: #2c2c2c;
            border: none;
        }

        QPushButton {
            background-color: #444444;
            border: none;
            padding: 8px 12px;
            margin: 4px;
            border-radius: 6px;
        }

        QPushButton:hover {
            background-color: #555555;
        }

        QPushButton:checked {
            background-color: #ff4444;
        }

        QPushButton#CloseButton:hover {
            background-color: #ff4444;
        }

        QLabel {
            color: white;
        }
        """)
    def refresh_cocktail_list(self):
        self.list_cocktails.clear()

        # 1) Start with all cocktails
        filtered = self.all_cocktails

        # 2) Apply search filter
        if self.search_text:
            filtered = [
                c for c in filtered
                if self.search_text.lower() in c["name"].lower()
            ]

        # 3) Apply toggles
        if self.show_favorites:
            filtered = [
                c for c in filtered
                if c.get("is_favorite", False)
            ]
        if self.show_easy:
            # or c['is_easy_to_make'] if that’s your DB property
            filtered = [
                c for c in filtered
                if c.get("is_easy_to_make", False)
            ]
        if self.show_tasty:
            filtered = [
                c for c in filtered
                if c.get("flavor", "").lower() != "bad"
                # or however you define “tasty”
            ]

        # 4) Show final results
        if not filtered:
            self.list_cocktails.addItem("No cocktails found.")
        else:
            for c in filtered:
                txt = f"{c['name']} ({c.get('flavor', 'Unknown')})"
                self.list_cocktails.addItem(txt)

    def handle_search(self, txt):
        self.search_text = txt  # remember it
        self.refresh_cocktail_list()

    def toggle_favorites(self):
        self.show_favorites = self.btn_favorites.isChecked()
        self.refresh_cocktail_list()

    def toggle_easy(self):
        self.show_easy = self.btn_easy.isChecked()
        self.refresh_cocktail_list()

    def toggle_tasty(self):
        self.show_tasty = self.btn_tasty.isChecked()
        self.refresh_cocktail_list()

