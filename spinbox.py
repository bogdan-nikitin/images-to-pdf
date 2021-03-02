import functools

from PyQt5 import QtCore, QtWidgets


class SpinBox(QtWidgets.QSpinBox):
    valueEdited = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__value_set = False

        # If someone call SpinBox.disconnect(), then SpinBox.valueEdited will
        # stop working, and this is a bug

        self.valueChanged.connect(self.__emit_value_edited)

        self.setValue = self.__value_set_decorator(self.setValue)
        self.setMinimum = self.__value_set_decorator(self.setMinimum)
        self.setMaximum = self.__value_set_decorator(self.setMaximum)

        # Maybe I should add textEdited signal...

    def __value_set_decorator(self, method):
        @functools.wraps(method)
        def decorated(*args, **kwargs):
            self.__value_set = True
            result = getattr(
                super(self.__class__, self), method.__name__
            )(*args, **kwargs)
            self.__value_set = False
            return result

        return decorated

    def __emit_value_edited(self, value):
        if not self.__value_set:
            self.valueEdited.emit(value)
