from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QWidget


class ScalingImage(QWidget):
    """
    Image that scaling with parent, keeping aspect ratio
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.pix_map = QPixmap()

    def setPixmap(self, pix_map):
        self.pix_map = pix_map
        self.update()

    def paintEvent(self, event):
        if not self.pix_map.isNull():
            painter = QPainter(self)
            width, height = self.width(), self.height()

            size = self.pix_map.size()
            size.scale(self.size(), Qt.KeepAspectRatio)
            scaled = self.pix_map.scaled(size, Qt.KeepAspectRatio,
                                         Qt.SmoothTransformation)
            image_width = scaled.width()
            image_height = scaled.height()
            painter.drawPixmap(
                QPoint((width - image_width) // 2,
                       (height - image_height) // 2),
                scaled
            )
