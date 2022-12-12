from PyQt5.QtCore import QPoint, Qt, QRect
from PyQt5.QtGui import QColor, QPen, QBrush
import xml.etree.ElementTree as ET

from .shape import Shape, INITIAL_SIZE, COLOR_SELECTED


### CLASS GROUP ###
class Group(Shape):
    def __init__(self, point=None, color=None, length=INITIAL_SIZE, activate=False, width=None, height=None, _id=None):
        if point is None:
            point = QPoint(0, 0)
        if color is None:
            color = QColor(Qt.black)
        self._children = []
        super().__init__(point, color, length=length, activate=activate, width=width, height=height, _id=_id)

    def __len__(self) -> int:
        return len(self._children)

    def __getitem__(self, item) -> Shape:
        return self._children[item]

    def _updateRect(self) -> None:
        self._rect = QRect()
        if self._children:
            self._rect = QRect(self._children[0].rect)
            for child in self:
                self._rect = child.rect.united(self._rect)

    def draw(self, painter) -> None:
        brush_style = Qt.Dense6Pattern if self.getStatus() else Qt.NoBrush
        pen_color = COLOR_SELECTED if self.getStatus() else QColor(Qt.black)
        painter.save()
        painter.setPen(QPen(pen_color, 0, Qt.DashLine))
        painter.setBrush(QBrush(self.color, brush_style))
        painter.drawRect(self._rect)
        painter.restore()
        for elem in self:
            elem.draw(painter)

    def changeFlag(self) -> None:
        super().changeFlag()
        for elem in self:
            elem.changeFlag()

    def deactivate(self) -> None:
        super().deactivate()
        for elem in self:
            elem.deactivate()

    def addChild(self, child) -> None:
        self._children.append(child)
        self._updateRect()
        self.notifyObservers(new_child=child)

    def isSelected(self, point) -> bool:
        for elem in self:
            if elem.isSelected(point):
                return True
        return False

    def move_inplace(self, canvas: QRect, dx, dy) -> bool:
        if super().move_inplace(canvas, dx, dy):
            for elem in self:
                elem.move_inplace(canvas, dx, dy)

    def change_size(self, canvas: QRect, dsize) -> bool:
        if super().change_size(canvas, dsize * len(self)):
            for i, elem in enumerate(self):
                if not elem.change_size(canvas, dsize):
                    for j in range(i):
                        self[j].change_size(canvas, -dsize)
                    super().change_size(canvas, - dsize * len(self))
                    break
            else:
                self._updateRect()
                return True
        return False

    def save(self) -> ET:
        element = super().save()
        items = ET.SubElement(element, 'items')
        for elem in self:
            items.append(elem.save())
        items.set('count_elements', str(len(self)))
        return element

    @classmethod
    def _factory_load(cls, element: ET) -> 'Group':
        group = super()._factory_load(element)
        items = element.find('items')
        for item in items:
            group.addChild(Shape.load(item))
        return group
