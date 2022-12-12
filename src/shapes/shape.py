from abc import ABCMeta, abstractmethod
from PyQt5.QtCore import QRect, Qt, QMargins
from PyQt5.QtGui import QColor, QPen, QBrush
import xml.etree.ElementTree as ET

from ..storage_object import StorageObject

INITIAL_SIZE = 50
COLOR_SELECTED = QColor(Qt.red)
COLOR_BORDER = QColor(Qt.gray)


class Shape(StorageObject, metaclass=ABCMeta):
    _linked_widget = None
    _is_current = False
    _subclasses = {}

    @classmethod
    def load_subclasses(cls) -> None:
        for subclass in cls.__subclasses__():
            cls._subclasses[subclass.__name__] = subclass
            subclass.load_subclasses()

    def __init__(self, point, color, length=INITIAL_SIZE, activate=False, width=None, height=None, _id=None):
        if not hasattr(self.__class__, '_counter'):
            self.__class__._counter = 0
        if _id is None:
            self.__class__._counter += 1
            self._id = self.__class__._counter
        else:
            self._id = _id
        super().__init__()
        width = length if width is None else width
        height = length if height is None else height
        self._rect = QRect(0, 0, width, height)
        self._rect.moveCenter(point)
        self._activate = activate
        self._color = color

    def getName(self) -> str:
        return f'{self.__class__.__name__} {self._id}'

    @property
    def rect(self) -> QRect:
        return self._rect

    @classmethod
    def get_linked_widget(cls):
        return cls._linked_widget

    @classmethod
    def set_linked_widget(cls, widget)  -> None:
        cls._linked_widget = widget
        widget.clicked.connect(lambda: widget.window().selectShape(cls))

    @classmethod
    def set_is_current(cls, status) -> None:
        if cls.get_linked_widget():
            color = 'yellow' if status else 'none'
            cls.get_linked_widget().setStyleSheet("background-color: " + color)

    @property
    def color(self) -> QColor:
        return COLOR_SELECTED if self.getStatus() else self._color

    @color.setter
    def color(self, color: QColor) -> None:
        self._color = color

    @abstractmethod
    def draw(self, painter) -> None:
        pass

    def paint(self, painter) -> None:
        if not painter.isActive():
            return
        painter.save()
        painter.setPen(QPen(COLOR_BORDER, 0, Qt.SolidLine))
        painter.setBrush(QBrush(self.color, Qt.SolidPattern))
        self.draw(painter)
        painter.restore()

    def changeFlag(self) -> None:
        self._activate = not self._activate
        self.notifyObservers()

    def getStatus(self) -> bool:
        return self._activate

    def setStatus(self, status: bool) -> None:
        self._activate = status
        self.notifyObservers()

    def deactivate(self) -> None:
        self._activate = False
        self.notifyObservers()

    @abstractmethod
    def isSelected(self, point) -> bool:
        pass

    def is_inner_canvas(self, canvas: QRect) -> bool:
        return self._rect.united(canvas) == canvas

    @staticmethod
    def addMargins(size_margins) -> QMargins:
        return QMargins(*((size_margins,) * 4))

    @staticmethod
    def is_valid_size(shape_copy: QRect) -> bool:
        return shape_copy.width() >= 10 and shape_copy.height() >= 10

    def move_inplace(self, canvas: QRect, dx, dy) -> bool:
        old_rect = self._rect
        self._rect = self._rect.translated(dx, dy)
        if not self.is_inner_canvas(canvas):
            self._rect = old_rect
            return False
        self.notifyObservers()
        return True

    def change_size(self, canvas: QRect, dsize) -> bool:
        old_rect = self._rect
        self._rect = self._rect + self.addMargins(dsize)
        if not (self.is_inner_canvas(canvas) and self.is_valid_size(self._rect)):
            self._rect = old_rect
            return False
        self.notifyObservers()
        return True

    def save(self) -> ET:
        element = ET.Element(self.__class__.__name__)
        element.set('color', self.color.name())
        element.set('id', str(self._id))
        rect = ET.SubElement(element, 'rect')
        rect.set('left', str(self.rect.x()))
        rect.set('top', str(self.rect.y()))
        rect.set('width', str(self.rect.width()))
        rect.set('height', str(self.rect.height()))
        return element

    @classmethod
    def load(cls, element: ET) -> 'Shape':
        if not cls._subclasses:
            cls.load_subclasses()
        if element.tag in cls._subclasses:
            return cls._subclasses[element.tag]._factory_load(element)

    @classmethod
    def _factory_load(cls, element: ET) -> 'Shape':
        rect = element.find('rect')
        rect = QRect(*map(int, (rect.get(s, 0) for s in
                                ['left', 'top', 'width', 'height']
                                )))
        point = rect.center()
        color = QColor(element.get('color', Qt.black))
        width = rect.width()
        height = rect.height()
        _id = int(element.get('id', 0))
        return cls(point, color, width=width, height=height, _id=_id)
