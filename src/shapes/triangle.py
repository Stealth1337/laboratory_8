import math
from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import QPolygon
import xml.etree.ElementTree as ET

from .shape import Shape


### CLASS TRIANGLE ###
class Triangle(Shape):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rect.setHeight(int(round(self._rect.width() * math.sqrt(3) / 2)))
        self._polygon = QPolygon([
            QPoint(self._rect.center().x(), self._rect.top()),
            self._rect.bottomRight(),
            self._rect.bottomLeft()
        ])

    def draw(self, painter) -> None:
        painter.drawPolygon(self._polygon)

    def isSelected(self, point) -> bool:
        return self._polygon.containsPoint(point, Qt.WindingFill)

    def move_inplace(self, canvas, dx, dy) -> bool:
        if super().move_inplace(canvas, dx, dy):
            self._polygon.translate(dx, dy)

    def change_size(self, canvas: QRect, dsize) -> bool:
        result = super().change_size(canvas, dsize)
        if result:
            self._polygon = QPolygon([
                QPoint(self._rect.center().x(), self._rect.top()),
                self._rect.bottomRight(),
                self._rect.bottomLeft()
            ])
        return result

    def save(self) -> ET:
        element = super().save()
        polygon = ET.SubElement(element, 'polygon')
        points = ET.SubElement(polygon, 'points')
        points.set('count_points', '3')
        for point in self._polygon:
            el_point = ET.SubElement(points, 'point')
            el_point.set('x', str(point.x()))
            el_point.set('y', str(point.y()))
        return element
