from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QPoint


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setObjectName("CustomTitleBar")

        # Title label (centered)
        self.title = QLabel("Elon's Bar")
        self.title.setStyleSheet("color: #f8f8f2; font-size: 14px; padding-left: 8px;")
        self.title.setAlignment(Qt.AlignCenter)

        # Buttons
        self.btnGoBack = QPushButton("←")
        self.btnMinimize = QPushButton("—")
        self.btnClose = QPushButton("X")

        for btn in [self.btnGoBack, self.btnMinimize, self.btnClose]:
            btn.setFixedSize(40, 30)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("border: none;")

            # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addWidget(self.btnGoBack)
        layout.addStretch()
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.btnMinimize)
        layout.addWidget(self.btnClose)

        # Connections
        self.btnClose.clicked.connect(self.parent.close)
        self.btnMinimize.clicked.connect(self.parent.showMinimized)

        # Drag support
        self.oldPos = None

        # Style
        self.setStyleSheet("""
            QWidget#CustomTitleBar {
                background-color: #282a36;
            }
            QPushButton {
                color: #f8f8f2;
                background-color: #44475a;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6272a4;
            }
            QLabel {
                color: #f8f8f2;
                font-size: 14px;
            }
        """)

    def toggle_max_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self.oldPos
            self.parent.move(self.parent.pos() + delta)
            self.oldPos = event.globalPosition().toPoint()