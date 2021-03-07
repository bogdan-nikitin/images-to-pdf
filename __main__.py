import sys
from dataclasses import dataclass

from PIL import ImageQt, Image, UnidentifiedImageError
from PyQt5.QtCore import QMutex
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox
)

from mainwindow import Ui_MainWindow


@dataclass
class DataItem:
    img: Image.Image
    # Maybe I should use something from pathlib instead of str
    path: str


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.data_items = []

        # Connecting callbacks to signals
        self.addBtn.clicked.connect(self.image_dialog)
        self.imagesListWidget.doubleClicked.connect(
            self.images_list_double_clicked
        )
        self.indexBox.valueEdited.connect(self.index_changed)
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
        self.saveBtn.clicked.connect(self.save_dialog)
        self.actionSave.triggered.connect(self.save_dialog)
        self.actionAddImage.triggered.connect(self.image_dialog)
        self.transpose_image_mutex = QMutex()

    def transpose_image(self, index, method):
        self.data_items[index].img = self.data_items[index].img.transpose(
            method
        )

    def rotate_btn_clicked(self, method):
        def slot():
            # If there is no mutex and you press the rotate button many times
            # and the image is large, then the app may crash
            if self.transpose_image_mutex.tryLock():
                if self.imagesListWidget.count() != 0:
                    self.transpose_image(self.indexBox.value() - 1, method)
                    self.update_image(self.indexBox.value() - 1)
                self.transpose_image_mutex.unlock()

        return slot

    def remove_btn_clicked(self):
        if self.imagesListWidget.count() != 0:
            index = self.indexBox.value() - 1
            self.remove_image(index)

    def set_enabled_action_buttons(self, enabled):
        self.removeBtn.setEnabled(enabled)
        self.rotateLeftBtn.setEnabled(enabled)
        self.rotateRightBtn.setEnabled(enabled)
        self.saveBtn.setEnabled(enabled)
        self.actionSave.setEnabled(enabled)

    def remove_image(self, index):
        self.imagesListWidget.takeItem(index)
        self.data_items.pop(index)
        self.indexBox.setMaximum(self.imagesListWidget.count())
        self.pagesCountLabel.setText(str(self.imagesListWidget.count()))
        if self.imagesListWidget.count() == 0:
            self.indexBox.setMinimum(0)
            self.indexBox.setValue(0)
            self.imageWidget.setPixmap(QPixmap())
            self.fileNameLabel.setText('')
            self.set_enabled_action_buttons(False)
        else:
            self.set_current_item(min(index, self.imagesListWidget.count() - 1))

    def to_left_btn_clicked(self):
        if self.indexBox.value() > 1:
            self.set_current_item(self.indexBox.value() - 2)

    def to_right_btn_clicked(self):
        if self.indexBox.value() < self.imagesListWidget.count():
            self.set_current_item(self.indexBox.value())

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
            # self.imagesListWidget.setCurrentRow(index - 1)

    def image_dialog(self):
        images = QFileDialog.getOpenFileNames(self, 'Select image', '')[0]
        for image in images:
            self.add_image(image)

    def add_image(self, img_path):
        try:
            im = Image.open(img_path).convert('RGBA')
        except UnidentifiedImageError:
            QMessageBox.critical(self, 'Error', f'{img_path} is not an image')
            return False
        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'When opening a file {img_path} an unknown error occurred. '
                f'Error text: {e}'
            )
            return False
        self.data_items.append(DataItem(im, img_path))
        self.imagesListWidget.addItem(img_path)
        self.indexBox.setMaximum(self.imagesListWidget.count())
        self.indexBox.setMinimum(1)
        self.pagesCountLabel.setText(str(self.imagesListWidget.count()))
        self.set_current_item(self.imagesListWidget.count() - 1)
        self.set_enabled_action_buttons(True)
        return True

    def switch_arrows(self, index):
        self.toLeftBtn.setEnabled(index > 0)
        self.toRightBtn.setEnabled(index < self.imagesListWidget.count() - 1)

    def images_list_double_clicked(self, _):
        index = self.imagesListWidget.currentRow()
        self.set_current_item(index)

    def update_image(self, index):
        data_item = self.data_items[index]
        pix_map = QPixmap.fromImage(ImageQt.ImageQt(data_item.img))
        # Scaling icon for better performance
        icon = QIcon(pix_map.scaledToWidth(32))
        self.imageWidget.setPixmap(pix_map)
        self.imagesListWidget.item(index).setIcon(icon)

    def set_current_item(self, index):
        self.update_image(index)
        self.fileNameLabel.setText(self.data_items[index].path)
        self.switch_arrows(index)
        self.indexBox.setValue(index + 1)
        self.imagesListWidget.setCurrentRow(index)

    def save_dialog(self):
        output_file_name, _ = QFileDialog.getSaveFileName(
            self, 'Save PDF', '', 'PDF (*.pdf)'
        )
        if output_file_name:
            self.save_as_pdf(output_file_name)

    def save_as_pdf(self, output_file_name):
        if not self.data_items:
            return
        try:
            data_items = [item.img.convert('RGB') for item in self.data_items]
            data_items[0].save(
                output_file_name, save_all=True,
                append_images=data_items[1:]
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                'Error',
                f'An unknown error occurred while saving. '
                f'Error text: {e}'
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
