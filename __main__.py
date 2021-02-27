import sys
from dataclasses import dataclass

from PIL import ImageQt, Image
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog,
                             QListWidgetItem)

from mainwindow import Ui_MainWindow


@dataclass
class DataItem:
    img: Image.Image
    path: str


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.data_items = []
        # self.is_image_added = False
        self.addBtn.clicked.connect(self.image_dialog)
        self.imagesListWidget.doubleClicked.connect(self.on_double_click)
        self.indexBox.valueChanged.connect(self.index_changed)
        self.imagesListWidget.model().rowsMoved.connect(self.items_moved)

    def items_moved(self, _, start, end, __, destination):
        previous = self.data_items[destination:destination + end + 1 - start:]
        self.data_items[
            destination:destination + end + 1 - start
        ] = self.data_items[start:end + 1]
        self.data_items[start:end + 1] = previous

    def index_changed(self, index):
        if self.imagesListWidget.count() != 0:
            self.set_current_item(index - 1)
        # self.is_image_added = False

    def image_dialog(self):
        images = QFileDialog.getOpenFileNames(self, 'Select image', '')[0]
        for image in images:
            self.add_image(image)

    def add_image(self, img_path):
        im = Image.open(img_path).convert('RGBA')
        self.data_items.append(DataItem(im, img_path))
        pix_map = QPixmap.fromImage(ImageQt.ImageQt(im))
        # Scaling icon for better performance
        icon = QIcon(pix_map.scaledToWidth(32))
        item = QListWidgetItem(icon, img_path)
        self.imagesListWidget.addItem(item)
        # self.is_image_added = True

        # self.imageWidget.setPixmap(pix_map)
        # self.fileNameLabel.setText(img_path)
        self.indexBox.setMinimum(1)
        self.indexBox.setMaximum(self.imagesListWidget.count())
        self.indexBox.setValue(self.imagesListWidget.count())
        self.pagesCountLabel.setText(str(self.imagesListWidget.count()))

    def on_double_click(self, _):
        index = self.imagesListWidget.currentRow()
        self.indexBox.setValue(index + 1)

    def set_current_item(self, index):
        data_item = self.data_items[index]
        pix_map = QPixmap.fromImage(ImageQt.ImageQt(data_item.img))
        self.imageWidget.setPixmap(pix_map)
        self.fileNameLabel.setText(data_item.path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
