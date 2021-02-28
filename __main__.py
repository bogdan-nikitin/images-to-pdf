# TODO: Change spinbox to custom class with custom valueEdited signal


import sys
from dataclasses import dataclass

from PIL import ImageQt, Image
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

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

        # Connecting callbacks to signals
        self.addBtn.clicked.connect(self.image_dialog)
        self.imagesListWidget.doubleClicked.connect(
            self.images_list_double_clicked
        )
        self.indexBox.valueChanged.connect(self.index_changed)
        self.imagesListWidget.model().rowsMoved.connect(self.items_moved)
        self.toLeftBtn.clicked.connect(self.to_left_btn_clicked)
        self.toRightBtn.clicked.connect(self.to_right_btn_clicked)
        self.removeBtn.clicked.connect(self.remove_btn_clicked)
        self.rotateLeftBtn.clicked.connect(
            self.rotate_btn_clicked(Image.ROTATE_90)
        )
        self.rotateRightBtn.clicked.connect(
            self.rotate_btn_clicked(Image.ROTATE_270)
        )

    def transpose_image(self, index, method):
        self.data_items[index].img = self.data_items[index].img.transpose(
            method
        )

    def rotate_btn_clicked(self, method):

        def signal():
            if self.imagesListWidget.count() != 0:
                self.transpose_image(self.indexBox.value() - 1, method)
                self.update_image(self.indexBox.value() - 1)

        return signal

    def remove_btn_clicked(self):
        if self.imagesListWidget.count() != 0:
            index = self.indexBox.value() - 1
            self.remove_image(index)

    def remove_image(self, index):
        self.imagesListWidget.takeItem(index)
        self.data_items.pop(index)
        if self.imagesListWidget.count() == 0:
            self.indexBox.setMinimum(0)

    def to_left_btn_clicked(self):
        if self.indexBox.value() > 1:
            self.indexBox.setValue(self.indexBox.value() - 1)

    def to_right_btn_clicked(self):
        if self.indexBox.value() < self.imagesListWidget.count():
            self.indexBox.setValue(self.indexBox.value() + 1)

    def items_moved(self, _, start, end, __, destination):
        cur_item = self.data_items[self.indexBox.value() - 1]
        end += 1
        moving = self.data_items[start:end]
        if destination > end:
            x = destination - end + start
            self.data_items[start:x] = self.data_items[end:destination]
            self.data_items[x:destination] = moving
        elif end > destination:
            x = destination + end - start
            self.data_items[x:end] = self.data_items[destination:start]
            self.data_items[destination:x] = moving
        self.indexBox.setValue(self.data_items.index(cur_item) + 1)

    def index_changed(self, index):
        if self.imagesListWidget.count() != 0:
            self.set_current_item(index - 1)
            self.imagesListWidget.setCurrentRow(index - 1)
        # self.is_image_added = False

    def image_dialog(self):
        images = QFileDialog.getOpenFileNames(self, 'Select image', '')[0]
        for image in images:
            self.add_image(image)

    def add_image(self, img_path):
        im = Image.open(img_path).convert('RGBA')
        self.data_items.append(DataItem(im, img_path))

        # Scaling icon for better performance
        self.imagesListWidget.addItem(img_path)
        # self.is_image_added = True

        # self.imageWidget.setPixmap(pix_map)
        # self.fileNameLabel.setText(img_path)
        self.indexBox.setMinimum(1)
        self.indexBox.setMaximum(self.imagesListWidget.count())
        self.indexBox.setValue(self.imagesListWidget.count())
        self.pagesCountLabel.setText(str(self.imagesListWidget.count()))

    def switch_arrows(self, index):
        self.toLeftBtn.setEnabled(index > 0)
        self.toRightBtn.setEnabled(index < self.imagesListWidget.count() - 1)

    def images_list_double_clicked(self, _):
        index = self.imagesListWidget.currentRow()
        self.indexBox.setValue(index + 1)

    def update_image(self, index):
        data_item = self.data_items[index]
        pix_map = QPixmap.fromImage(ImageQt.ImageQt(data_item.img))
        icon = QIcon(pix_map.scaledToWidth(32))
        self.imageWidget.setPixmap(pix_map)
        self.imagesListWidget.item(index).setIcon(icon)

    def set_current_item(self, index):
        self.update_image(index)
        self.fileNameLabel.setText(self.data_items[index].path)
        self.switch_arrows(index)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
