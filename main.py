import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from app_gui import AppGui
import qdarktheme


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image comparator v0.1")
        self.setMinimumSize(800, 600)
        self.app_gui = AppGui(self)

        central_widget = QWidget()
        central_widget.setLayout(self.app_gui)

        self.setCentralWidget(central_widget)


def main():
    app = QApplication()
    qdarktheme.setup_theme()
    window = MyApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
