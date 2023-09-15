from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMessageBox, QTextEdit
from PySide6.QtGui import (
    QImageReader,
    QPixmap,
    QDragEnterEvent,
    QDropEvent,
    QPainter,
    QTransform,
)
from PySide6.QtCore import Signal


class ImageView(QGraphicsView):
    tranformChanged = Signal(QTransform)
    multipleUrls = Signal(list)
    photoAdded = Signal(int, int)

    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setAcceptDrops(True)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.zoom_factor = 0
        self.original_image = None
        self.url = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            file_path = mime_data.urls()[0].toLocalFile()
            if len(mime_data.urls()) > 1:
                self.multipleUrls.emit(mime_data.urls())
            else:
                self.loadImage(file_path)

    def dragMoveEvent(self, event):
        event.accept()

    def wheelEvent(self, event):
        zoom_in = event.angleDelta().y() > 0
        zoom_factor = 1.1 if zoom_in else 1 / 1.1

        self.zoom_factor *= zoom_factor
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale(zoom_factor, zoom_factor)

        self.tranformChanged.emit(
            self.transform(),
        )

    def loadImage(self, file_path):
        image_reader = QImageReader(file_path)
        pixmap = QPixmap.fromImageReader(image_reader)
        if pixmap.width() == 0:
            QMessageBox.critical(
                self, "Error", "Unable to load the image.", QMessageBox.Ok
            )
            return

        if self.scene().items():
            self.scene().removeItem(self.scene().items()[0])

        self.original_image = pixmap
        self.scene().addPixmap(pixmap)
        self.photoAdded.emit(pixmap.width(), pixmap.height())
        self.url = file_path

    def set_transform(self, transform):
        horz_blocked = self.horizontalScrollBar().blockSignals(True)
        vert_blocked = self.verticalScrollBar().blockSignals(True)

        self.setTransform(transform)
        self.horizontalScrollBar().blockSignals(horz_blocked)
        self.verticalScrollBar().blockSignals(vert_blocked)
