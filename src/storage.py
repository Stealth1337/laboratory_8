from typing import Generator
import xml.etree.ElementTree as ET

from .shapes import Shape
from .storage_object import StorageObject


### MY STORAGE ###
class Storage:
    arr = []

    def __len__(self):
        return len(self.arr)

    def __getitem__(self, item) -> StorageObject:
        return self.arr[item]

    def addItem(self, item: StorageObject):
        if item is not None:
            self.arr.append(item)

    def deact_all(self):
        for i in self.arr:
            i.deactivate()

    def deleteAllActive(self):
        for i in range(len(self.arr) - 1, -1, -1):
            if self.arr[i].getStatus():
                self.arr.remove(self.arr[i])

    def getActiveItems(self) -> Generator[StorageObject, None, None]:
        for i in self.arr:
            if i.getStatus():
                yield i

    def save(self, filename: str):
        root = ET.Element('storage')
        items = ET.SubElement(root, 'items')
        for elem in self:
            items.append(elem.save())
        items.set('count_elements', str(len(self)))
        ET.indent(root, space='  ')
        result = ET.tostring(root, encoding='utf-8')
        with open(filename, 'wb') as f:
            f.write(result)

    def clear(self):
        self.arr.clear()

    def load(self, filename):
        self.arr.clear()
        root = ET.parse(filename).getroot()
        assert root.tag == 'storage'
        items = root.find('items')
        for item in items:
            self.addItem(Shape.load(item))
