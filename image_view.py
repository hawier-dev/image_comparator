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
    tranformChanged = Signal(int, int, QTransform, int)
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

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls() and len(mime_data.urls()) == 1:
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls() and len(mime_data.urls()) == 1:
            file_path = mime_data.urls()[0].toLocalFile()
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
            self.horizontalScrollBar().value(),
            self.verticalScrollBar().value(),
            self.transform(),
            self.zoom_factor,
        )

    def loadImage(self, file_path):
        image_reader = QImageReader(file_path)
        pixmap = QPixmap.fromImageReader(image_reader)
        if pixmap.width() == 0:
            QMessageBox.critical(self, 'Error', 'Unable to load the image.', QMessageBox.Ok)

        if self.scene().items():
            self.scene().removeItem(self.scene().items()[0])

        self.scene().addPixmap(pixmap)
        self.photoAdded.emit(pixmap.width(), pixmap.height())

    def set_transform(self, horz_scroll, vert_scroll, transform, zoom):
        # temporary block signals from scroll bars to prevent interference
        horz_blocked = self.horizontalScrollBar().blockSignals(True)
        vert_blocked = self.verticalScrollBar().blockSignals(True)
        self._zoom = zoom
        self.setTransform(transform)
        dx = horz_scroll - self.horizontalScrollBar().value()
        dy = vert_scroll - self.verticalScrollBar().value()
        self.horizontalScrollBar().setValue(dx)
        self.verticalScrollBar().setValue(dy)
        self.horizontalScrollBar().blockSignals(horz_blocked)
        self.verticalScrollBar().blockSignals(vert_blocked)
