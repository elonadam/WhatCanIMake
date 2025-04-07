# cocktail_book_screen.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QDialog, \
    QLineEdit, QHBoxLayout, QAbstractItemView, QComboBox
from PySide6.QtCore import QFile, Signal, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QIcon, QFont


class CocktailDetailDialog(QDialog):
    def __init__(self, cocktail):
        super().__init__()
        self.setWindowTitle(cocktail["name"])
        layout = QVBoxLayout(self)

        details = f"""
        Name: {cocktail["name"]}
        ABV: {cocktail.get("abv", "Unknown")}
        Glass: {cocktail.get("glass", "Unknown")}
        Garnish: {cocktail.get("garnish", "None")}
        Times Made: {cocktail.get("times_made", 0)}

        Ingredients: {cocktail.get('ingredients')}


        Instructions:
        {cocktail.get('instructions', 'No instructions available.')}
        """
        lbl_details = QLabel(details)
        lbl_details.setWordWrap(True)
        layout.addWidget(lbl_details)


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
        self.show_stirred = False

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
        self.btn_back = self.ui.findChild(QPushButton, "btn_back")  # not showing TODO 4 delete this
        self.lbl_title = self.ui.findChild(QLabel, "lbl_title")
        self.name_search = self.ui.findChild(QLineEdit, "name_search")
        self.btn_favorites = self.ui.findChild(QPushButton, "btn_favorites")
        self.btn_easy = self.ui.findChild(QPushButton, "btn_easy")
        self.btn_stirred = self.ui.findChild(QPushButton, "btn_stirred")
        self.list_cocktails = self.ui.findChild(QListWidget, "list_cocktails")
        self.combo_flavor = self.ui.findChild(QComboBox, "combo_flavor") # the drop down menu

        print([btn.objectName() for btn in self.ui.findChildren(QPushButton)])

        # 4. Connect signals
        self.name_search.textChanged.connect(self.handle_search)
        self.btn_favorites.clicked.connect(self.toggle_favorites)
        self.btn_easy.clicked.connect(self.toggle_easy)
        self.btn_stirred.clicked.connect(self.toggle_stirred)

        self.list_cocktails.itemClicked.connect(self.show_cocktail_details)

        #load the drop down with flavors
        self.combo_flavor.addItem("All")
        self.combo_flavor.addItems(["Fruity & Tropical", "Bitter & Herbal", "Floral & Aromatic", "Sour & Tart", "Sweet & Dessert-Like"])  # use your actual flavors
        self.combo_flavor.currentTextChanged.connect(self.refresh_cocktail_list)

        #  smooth scroll
        self.list_cocktails.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.list_cocktails.verticalScrollBar().setSingleStep(9)

        # 5. Initialize
        self.apply_style()  # optional
        self.refresh_cocktail_list()

    def show_cocktail_details(self, item):
        row = self.list_cocktails.row(item)
        cocktail = self.filtered[row]  # Use the current filtered list
        # Now open a detail dialog (you'll need to implement CocktailDetailDialog)
        dialog = CocktailDetailDialog(cocktail)
        dialog.exec()

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

        QListWidget::item {
            background-color: #2c2c2c;
            margin-top: 3px;
            margin-bottom: 2px;
            margin-left: 3px;
            margin-right: 3px;
            border-radius: 5px;
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
        
        QScrollBar:vertical {
            border: none;
            background: #1e1e1e;
            width: 12px;
            margin: 0px 0px 0px 0px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background: #44475a;
            min-height: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #6272a4;
        }
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
            background: none;
        }
        
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: none;
        }
        
        QComboBox {
            background-color: #444444;
            border: none;
            padding: 8px 12px;
            margin: 4px;
            border-radius: 6px;
            color: white;
        }
        
        QComboBox:hover {
            background-color: #555555;
        }
        
        QComboBox::drop-down {
            border: none;
            background: transparent;
        }

        
        """)

    def refresh_cocktail_list(self):
        self.list_cocktails.clear()
        self.filtered = self.all_cocktails  # 1) Start with all cocktails

        if self.search_text:  # 2) Apply search filter
            self.filtered = [
                c for c in self.filtered
                if self.search_text.lower() in c["name"].lower()
            ]

        if self.show_favorites:  # 3) Apply toggles
            self.filtered = [
                c for c in self.filtered
                if c.get("is_favorite", False)
            ]

        if self.show_stirred:
            self.filtered = [
                c for c in self.filtered
                if (c.get("prep_method") or "") == "Stirred"
            ]

        if self.show_easy:
            # or c['is_easy_to_make'] if that’s your DB property
            self.filtered = [
                c for c in self.filtered
                if c.get("is_easy_to_make", False)
            ]

        selected_flavor = self.combo_flavor.currentText()

        if selected_flavor.lower() != "all":
            selected = selected_flavor.strip().lower()
            self.filtered = [
                c for c in self.filtered
                if selected in c.get("flavor", "").strip().lower()
            ]

        if not self.filtered:  # 4) Show final results
            item = QListWidgetItem("No cocktails found.")
            self.list_cocktails.addItem(item)
        else:
            for cocktail in self.filtered:
                item_widget = self.create_cocktail_widget(cocktail)
                item = QListWidgetItem()
                item.setSizeHint(item_widget.sizeHint())
                self.list_cocktails.addItem(item)
                self.list_cocktails.setItemWidget(item, item_widget)

    def create_cocktail_widget(self, cocktail):
        outer = QWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 15)  # 10px bottom margin
        outer_layout.setSpacing(0)

        inner = QWidget()
        layout = QHBoxLayout(inner)
        layout.setContentsMargins(5, 5, 5, 5)

        # Circle with initial
        circle_label = QLabel(cocktail["name"][0].upper())
        circle_label.setFixedSize(40, 40)
        circle_label.setAlignment(Qt.AlignCenter)
        circle_label.setStyleSheet("""
            QLabel {
                background-color: #6272a4;
                border-radius: 20px;
                color: #f8f8f2;
                font-weight: bold;
                font-size: 18px;
            }
        """)

        # Cocktail name and ingredients vertical layout
        text_layout = QVBoxLayout()
        name_layout = QHBoxLayout()

        # Cocktail Name
        lbl_name = QLabel(cocktail["name"])
        lbl_name.setFont(QFont("Segoe UI", 12, QFont.Bold))

        name_layout.addWidget(lbl_name)

        # Favorite Icon
        if cocktail.get("is_favorite"):
            heart_icon = QLabel("❤")
            heart_icon.setStyleSheet("color: #ff5555; font-size: 16px;")
            name_layout.addWidget(heart_icon)

        name_layout.addStretch()

        # Ingredients (made_from)
        ingredients = (cocktail.get("made_from"))
        lbl_ingredients = QLabel(ingredients)
        lbl_ingredients.setFont(QFont("Segoe UI", 10))
        lbl_ingredients.setStyleSheet("color: #bbbbbb;")

        text_layout.addLayout(name_layout)
        text_layout.addWidget(lbl_ingredients)

        layout.addWidget(circle_label)
        layout.addLayout(text_layout)
        inner.setLayout(layout)

        outer_layout.addWidget(inner)
        return outer

    def handle_search(self, txt):
        self.search_text = txt  # remember it
        self.refresh_cocktail_list()

    def toggle_favorites(self):
        self.show_favorites = self.btn_favorites.isChecked()
        self.refresh_cocktail_list()

    def toggle_easy(self):
        self.show_easy = self.btn_easy.isChecked()
        self.refresh_cocktail_list()

    def toggle_stirred(self):
        self.show_stirred = self.btn_stirred.isChecked()
        self.refresh_cocktail_list()