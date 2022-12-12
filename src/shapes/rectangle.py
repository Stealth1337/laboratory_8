from .shape import Shape


### CLASS RECTANGLE ###
class Rectangle(Shape):
    def draw(self, painter) -> None:
        painter.drawRect(self._rect)

    def isSelected(self, point) -> bool:
        return self._rect.contains(point)
