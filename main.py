import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QColorDialog, QFileDialog, QMessageBox
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt
from forms.main_form import Ui_MainWindow
import logging

from src.shapes import *
from src.tree_view_storage import TreeViewStorage

STEP_CHANGE_SIZE = 10 // 2


class Window(QMainWindow):
    MOVE_KEYS = [Qt.Key_W, Qt.Key_A, Qt.Key_S, Qt.Key_D]
    CHANGE_SIZE_KEYS = [Qt.Key_Equal, Qt.Key_Minus]
    STEP_MOVE = 5
    MINIMUM_WIDTH = 750
    MINIMUM_HEIGHT = 200
    INITIAL_COLOR = QColor(Qt.black)

    def __init__(self):
        super().__init__()
        self._currentColor = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.window_width = self.size().width()
        self.window_height = self.size().height()
        self.ui.splitter.setSizes([200, self.window_width - 200])
        self.storage = TreeViewStorage(parent=self.ui.treeView)
        self.ui.treeView.setModel(self.storage)
        Circle.set_linked_widget(self.ui.circlebutton)
        Rectangle.set_linked_widget(self.ui.rectanlebutton)
        Triangle.set_linked_widget(self.ui.trianglebutton)
        self.ui.colorButton.clicked.connect(self.changeColor)
        self.ui.saveButton.clicked.connect(self.saveToFile)
        self.ui.loadButton.clicked.connect(self.loadFromFile)
        self.active_figure_class = Circle
        self.active_figure_class.set_is_current(True)
        self.currentColor = self.INITIAL_COLOR
        self.ui.groupButton.clicked.connect(self.groupElements)
        self.mouse_pos = None

    @property
    def currentColor(self):
        return self._currentColor

    @currentColor.setter
    def currentColor(self, color: QColor):
        if color != self._currentColor:
            for elem in self.storage.getActiveItems():
                elem.color = color
            self.storage.deact_all()
            self._currentColor = color
            self.ui.colorButton.setStyleSheet(f'background: {color.name()}')

    def resizeEvent(self, a0):
        minimal_height = self.MINIMUM_HEIGHT
        minimal_width = self.MINIMUM_WIDTH
        for elem in self.storage:
            minimal_height = max(minimal_height, elem.rect.bottomRight().y())
            minimal_width = max(minimal_width, elem.rect.bottomRight().x())
        self.setMinimumSize(minimal_width, minimal_height)

    @property
    def canvasrect(self):
        rect = self.ui.canvas.geometry()
        widget = self.ui.canvas
        while (widget := widget.parent()) is not self:
            rect = rect.translated(widget.geometry().topLeft())
        return rect

    def check(self, event):
        cntr_pressed = QApplication.keyboardModifiers() == Qt.ControlModifier
        point = event.pos()
        for elem in reversed(self.storage):
            if elem.isSelected(point):
                if not cntr_pressed and not elem.getStatus():
                    self.storage.deact_all()
                elem.changeFlag()
                break
        else:
            shape = self.active_figure_class(point, self.currentColor, activate=cntr_pressed)
            if shape.is_inner_canvas(self.canvasrect):
                self.storage.addItem(shape)
                if not cntr_pressed:
                    self.storage.deact_all()

    def changeColor(self):
        color = QColorDialog.getColor(self.currentColor, self, 'Выберите цвет')
        if color.isValid():
            self.currentColor = color

    def selectShape(self, shape):
        if shape is not self.active_figure_class:
            self.active_figure_class.set_is_current(False)
            self.active_figure_class = shape
            self.active_figure_class.set_is_current(True)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for shapes in self.storage:
            shapes.paint(painter)

    def update(self) -> None:
        super().update()
        self.ui.treeView.update()
        self.ui.groupButton.setEnabled(sum(1 for _ in self.storage.getActiveItems()) > 1)

    def mouseReleaseEvent(self, event):
        self.mouse_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.check(event)
        self.mouse_pos = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        if self.mouse_pos is not None:
            diff = event.pos() - self.mouse_pos
            for elem in self.storage.getActiveItems():
                elem.move_inplace(self.canvasrect, diff.x(), diff.y())
            self.mouse_pos = event.pos()
            self.update()

    def wheelEvent(self, event):
        for shape in self.storage.getActiveItems():
            shape.change_size(self.canvasrect, event.angleDelta().y() // 120)
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.storage.deleteAllActive()
        elif event.key() in self.MOVE_KEYS:
            dx, dy = [
                (0, -self.STEP_MOVE),  # Qt.Key_W
                (-self.STEP_MOVE, 0),  # Qt.Key_A
                (0, self.STEP_MOVE),  # Qt.Key_S
                (self.STEP_MOVE, 0)  # Qt.Key_D
            ][self.MOVE_KEYS.index(event.key())]
            for shape in self.storage.getActiveItems():
                shape.move_inplace(self.canvasrect, dx, dy)
        elif event.key() in self.CHANGE_SIZE_KEYS:
            dsize = [STEP_CHANGE_SIZE, -STEP_CHANGE_SIZE][self.CHANGE_SIZE_KEYS.index(event.key())]
            for shape in self.storage.getActiveItems():
                shape.change_size(self.canvasrect, dsize)
        self.update()

    def groupElements(self):
        group = Group()
        for elem in self.storage:
            if elem.getStatus():
                group.addChild(elem)
        self.storage.deleteAllActive()
        self.storage.addItem(group)
        self.update()

    def saveToFile(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Сохранение фигур', filter='*.xml')
        if filename:
            msg = QMessageBox(self)
            msg.setWindowTitle("Сохранение файла")
            try:
                self.storage.save(filename)
            except BaseException as e:
                logger.error("Ошибка сохранения файла", e)
                msg.setText("Ошибка сохранения")
                msg.setIcon(QMessageBox.Critical)
            else:
                msg.setText(f"Файл '{filename}' успешно сохранен")
            finally:
                msg.exec_()

    def loadFromFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Сохранение фигур', filter='*.xml')
        if filename:
            try:
                self.storage.load(filename)
                self.update()
            except BaseException as e:
                msg = QMessageBox(self)
                msg.setWindowTitle("открытие файла")
                logger.error("Ошибка открытия файла", e)
                msg.setText("Ошибка открытия файла")
                msg.setIcon(QMessageBox.Critical)
                msg.exec_()


def my_excepthook(type, value, tback):
    QtWidgets.QMessageBox.critical(
        Window, "CRITICAL ERROR", str(value),
        QtWidgets.QMessageBox.Cancel
    )
    sys.__excepthook__(type, value, tback)


sys.excepthook = my_excepthook

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    App = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())
