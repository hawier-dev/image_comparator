import random

from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QVBoxLayout, QLineEdit

from image_view import ImageView


class GraphicsView(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.text_view = QLineEdit()
        color = random.choice(
            [
                "#37874c",
                "#374687",
                "#873783",
                "#873746",
                "#909639",
                "#966939",
                "#399681",
                "#399658",
                "#07677a",
                "#650a8c",
                "#802d06",
            ]
        )
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        self.text_view.setFont(font)
        self.text_view.setStyleSheet(f"background-color: {color}")
        self.text_view.setAlignment(Qt.AlignCenter)

        self.image_view = ImageView()

        self.addWidget(self.image_view)
        self.addWidget(self.text_view)
