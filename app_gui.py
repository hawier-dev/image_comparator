from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLabel,
    QPushButton,
    QWidget,
    QFileDialog,
    QStatusBar,
    QMessageBox,
)

from graphics_view import GraphicsView
from image_view import ImageView


class AppGui(QVBoxLayout):
    def __init__(self, parent=None):
        super(AppGui, self).__init__(parent)
        self.main_window = parent

        self.image_views = []

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

        self.image_views_layout = QHBoxLayout()
        self.image_views_layout.setSpacing(0)

        self.add_image_view()
        self.add_image_view()

        # Layout with remove and add button
        self.add_remove_image_layout = QHBoxLayout()
        self.remove_button = QPushButton()
        self.remove_button.setText("-")
        self.remove_button.setFixedSize(30, 30)
        self.remove_button.pressed.connect(self.remove_image_view)
        self.add_button = QPushButton()
        self.add_button.setText("+")
        self.add_button.setFixedSize(30, 30)
        self.add_button.pressed.connect(self.add_image_view)

        self.add_remove_image_layout.addStretch()
        self.add_remove_image_layout.addWidget(self.remove_button)
        self.add_remove_image_layout.addWidget(self.add_button)
        self.add_remove_image_layout.addStretch()

        # Bottom bar
        self.bottom_settings_layout = QHBoxLayout()

        self.save_comparison_button = QPushButton()
        self.save_comparison_button.setText("Save comparison")
        self.save_comparison_button.setFixedWidth(200)
        self.save_comparison_button.pressed.connect(self.save_comparison)

        self.bottom_settings_layout.addWidget(self.save_comparison_button)

        self.images_widget.setLayout(self.image_views_layout)

        self.status_bar = QStatusBar()
        self.version = QLabel("Image Comparer v0.3")
        self.resolution_status = QLabel("None")
        self.status_bar.addWidget(self.version)
        self.status_bar.addWidget(self.resolution_status)

        self.main_window.setStatusBar(self.status_bar)

        self.addLayout(self.top_settings_layout)
        self.addWidget(self.images_widget)
        self.addLayout(self.add_remove_image_layout)
        self.addLayout(self.bottom_settings_layout)

    def add_image_view(self):
        graphics_view = GraphicsView()
        graphics_view.image_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        graphics_view.image_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        graphics_view.image_view.horizontalScrollBar().valueChanged.connect(
            partial(self.slider_sync, "horizontal")
        )
        graphics_view.image_view.verticalScrollBar().valueChanged.connect(
            partial(self.slider_sync, "vertical")
        )
        graphics_view.image_view.photoAdded.connect(self.add_resolution)
        graphics_view.image_view.tranformChanged.connect(self.set_transform)
        graphics_view.image_view.multipleUrls.connect(self.load_multiple_images)

        self.image_views_layout.addLayout(graphics_view)
        self.image_views.append(graphics_view)

    def load_multiple_images(self, urls):
        dialog = QMessageBox()
        dialog.setWindowTitle("Multiple files")
        dialog.setText("Do you want to load multiple files?")
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = dialog.exec_()
        urls = urls

        if result == QMessageBox.Yes:
            for item in self.image_views:
                if not item.image_view.url:
                    item.image_view.url = urls[0]
                    urls.remove(urls[0])

            for item in self.image_views:
                item.image_view.loadImage(item.image_view.url.toLocalFile())

        elif result == QMessageBox.No:
            return

    def remove_image_view(self):
        if len(self.image_views) > 2:
            self.image_views_layout.removeItem(self.image_views[-1])
            self.image_views[-1].deleteLater()
            self.image_views[-1].image_view.deleteLater()
            self.image_views[-1].text_view.deleteLater()
            self.image_views.remove(self.image_views[-1])

    def set_transform(self, *args):
        for item in self.image_views:
            item.image_view.set_transform(*args)

    def slider_sync(
        self,
        orientation,
        value,
    ):
        for item in self.image_views:
            if orientation == "horizontal":
                item.image_view.horizontalScrollBar().setValue(value)
            else:
                item.image_view.verticalScrollBar().setValue(value)

    def set_resolution(self, resolution):
        resolution = resolution.split("x")
        for item in self.image_views:
            if item.image_view.scene().items():
                item.image_view.scene().items()[0].setPixmap(
                    item.image_view.original_image.scaled(
                        int(resolution[0]), int(resolution[1])
                    )
                )
            item.image_view.setSceneRect(0, 0, int(resolution[0]), int(resolution[1]))
            item.image_view.setSceneRect(0, 0, int(resolution[0]), int(resolution[1]))
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

        file_path, _ = file_dialog.getSaveFileName(
            None, "Save Comparison Screenshot", "", "JPEG Image Files (*.jpg)"
        )

        if file_path:
            screenshot = self.images_widget.grab()
            screenshot.save(file_path, "jpg")
            print(f"Saved screenshot as {file_path}")
