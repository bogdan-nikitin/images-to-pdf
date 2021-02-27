from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import QRect, Qt, QPoint
from PyQt5.QtWidgets import QWidget


class ScalingImage(QWidget):
    """Изображение, которое масштабируется вместе с родительским объектом,
    сохраняя пропорции."""
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.pix_map = QPixmap()

    def setPixmap(self, pix_map):
        """Задать картинку."""
        self.pix_map = pix_map
        self.update()

    def paintEvent(self, event):
        """Метод отвечает за отрисовку картинки."""
        if not self.pix_map.isNull():
            painter = QPainter(self)
            # painter.setRenderHint(QPainter.SmoothPixmapTransform)
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
