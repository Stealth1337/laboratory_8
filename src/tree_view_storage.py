import typing
from typing import Generator

from PyQt5.QtGui import QStandardItemModel

from .storage import Storage
from .storage_object import StorageObject


class TreeViewStorage(Storage, QStandardItemModel):
    def __init__(self, parent=None, *args, **kwargs, ):
        super().__init__(*args, **kwargs)
        self.setHorizontalHeaderLabels(['Shapes'])
        if parent:
            self.setParent(parent)
        self.dataChanged.connect(self._data_changed)

    def addItem(self, item: StorageObject):
        super().addItem(item)
        item.get_item().setParent(self.invisibleRootItem())

    def _data_changed(self, *args, **kwargs):
        for item in self:
            tv_item = item.get_item()
            if tv_item.checkState() != item.getStatus():
                item.setStatus(tv_item.checkState())
                if tv_item.hasChildren():
                    for row in range(tv_item.rowCount()):
                        for column in range(tv_item.columnCount()):
                            tv_item.child(row, column).setCheckState(tv_item.checkState())
        self.parent().window().update()
