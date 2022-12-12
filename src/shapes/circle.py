from .shape import Shape


### CLASS CIRCLE ###=====
class Circle(Shape):
    def draw(self, painter):
        painter.drawEllipse(self._rect)

    def isSelected(self, point):
        d = self._rect.center() - point
        return (d.x() ** 2 + d.y() ** 2) <= ((self._rect.width() // 2) ** 2)
