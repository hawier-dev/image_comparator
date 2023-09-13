from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QSlider, QSplitter, QComboBox, QLabel, QPushButton, \
    QApplication, QWidget, QGridLayout, QFileDialog, QStatusBar

from image_view import ImageView


class AppGui(QVBoxLayout):
    def __init__(self, parent=None):
        super(AppGui, self).__init__(parent)
        self.main_window = parent

        # Bottom bar
        self.top_settings_layout = QHBoxLayout()

        # Change resolution based on selected images
        self.resolution_layout = QVBoxLayout()
        self.resolution_layout.setAlignment(Qt.AlignCenter)
        self.resolution_label = QLabel("Resolution")
        self.resolution_label.setAlignment(Qt.AlignCenter)
        self.resolution_combo = QComboBox()
        self.resolution_combo.setFixedWidth(100)
        self.resolution_combo.currentTextChanged.connect(self.set_resolution)

        self.resolution_layout.addWidget(self.resolution_label)
        self.resolution_layout.addWidget(self.resolution_combo)

        self.top_settings_layout.addLayout(self.resolution_layout)

        # Images comparison
        self.images_widget = QWidget()

        image_layout = QHBoxLayout()
        image_layout.setSpacing(0)

        # Save screenshot with comparison
        self.image_view1 = ImageView()
        self.image_view1.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view1.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view1.horizontalScrollBar().valueChanged.connect(
            partial(self.slider_sync, "horizontal", "image1")
        )
        self.image_view1.verticalScrollBar().valueChanged.connect(
            partial(self.slider_sync, "vertical", "image1")
        )
        self.image_view1.photoAdded.connect(self.add_resolution)

        self.image_view2 = ImageView()
        self.image_view2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view2.horizontalScrollBar().valueChanged.connect(
            partial(self.slider_sync, "horizontal", "image2")
        )
        self.image_view2.verticalScrollBar().valueChanged.connect(
            partial(self.slider_sync, "vertical", "image2")
        )
        self.image_view2.photoAdded.connect(self.add_resolution)

        image_layout.addWidget(self.image_view1)
        image_layout.addWidget(self.image_view2)

        self.image_view1.tranformChanged.connect(self.image_view2.set_transform)
        self.image_view2.tranformChanged.connect(self.image_view1.set_transform)

        # Bottom bar
        self.bottom_settings_layout = QHBoxLayout()

        self.save_comparison_button = QPushButton()
        self.save_comparison_button.setText("Save comparison")
        self.save_comparison_button.setFixedWidth(200)
        self.save_comparison_button.pressed.connect(self.save_comparison)

        self.bottom_settings_layout.addWidget(self.save_comparison_button)

        self.images_widget.setLayout(image_layout)

        self.status_bar = QStatusBar()
        self.version = QLabel("Image Comparer v0.2")
        self.resolution_status = QLabel("None")
        self.status_bar.addWidget(self.version)
        self.status_bar.addWidget(self.resolutiom
        self.addLayout(self.top_settings_layout)
        self.addWidget(self.images_widget)
        self.addLayout(self.bottom_settings_layout)

    def slider_sync(
        self,
        orientation,
        image_view,
        value,
    ):
        if image_view == "image1":
            if orientation == "horizontal":
                self.image_view2.horizontalScrollBar().setValue(value)
            else:
                self.image_view2.verticalScrollBar().setValue(value)

        else:
            if orientation == "horizontal":
                self.image_view1.horizontalScrollBar().setValue(value)
            else:
                self.image_view1.verticalScrollBar().setValue(value)

    def set_resolution(self, resolution):
        resolution = resolution.split("x")
        if self.image_view1.scene().items():
            self.image_view1.scene().items()[0].setPixmap(
                self.image_view1.original_image
                .scaled(int(resolution[0]), int(resolution[1]))
            )
        if self.image_view2.scene().items():
            self.image_view2.scene().items()[0].setPixmap(
                self.image_view2.original_image
                .scaled(int(resolution[0]), int(resolution[1]))
            )
        self.image_view1.setSceneRect(0, 0, int(resolution[0]), int(resolution[1]))
        self.image_view2.setSceneRect(0, 0, int(resolution[0]), int(resolution[1]))
        self.resolution_status.setText("x".join(resolution))
        self.resolution_status.setStyleSheet("color: lime")

    def add_resolution(self, width, height):
        resolution = f"{width}x{height}"
        if resolution not in [
            self.resolution_combo.itemText(i)
            for i in range(self.resolution_combo.count())
        ]:
            self.resolution_combo.addItem(resolution)

        if self.resolution_combo.currentText():
            self.set_resolution(self.resolution_combo.currentText())

    def save_comparison(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("JPEG Image Files (*.jpg)")

        file_path, _ = file_dialog.getSaveFileName(None, "Save Comparison Screenshot", "", "JPEG Image Files (*.jpg)")

        if file_path:
            screenshot = self.images_widget.grab()
            screenshot.save(file_path, 'jpg')
            print(f'Saved screenshot as {file_path}')