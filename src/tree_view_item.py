import weakref

from PyQt5 import QtCore
from PyQt5.QtGui import QStandardItem, QColor
from PyQt5.QtCore import Qt
from .observer import Observer


class TreeViewItem(QStandardItem, Observer):
    def __init__(self, storage_object):
        super().__init__(storage_object.getName())
        self._parent = None
        self._storage_object = weakref.ref(storage_object)
        self.addObserver(storage_object)
        storage_object.addObserver(self)
        self.setCheckable(True)
        self.setEditable(False)

    @property
    def storage_object(self):
        try:
            return self._storage_object()
        except RuntimeError:
            return None

    def setCheckState(self, checkState: bool) -> None:
        super().setCheckState(checkState)
        if self.hasChildren():
            for row in range(self.rowCount()):
                for column in range(self.columnCount()):
                    self.child(row, column).setCheckState(self.checkState())

    def clone(self) -> 'QStandardItem':
        new_clone = TreeViewItem(self.storage_object)
        new_clone._observers = self._observers.copy()
        for row in range(self.rowCount()):
            for column in range(self.columnCount()):
                new_clone.setChild(row, column, self.child(row, column).clone())
        return new_clone

    def remove(self):
        if self._parent:
            self._parent.removeRow(self.row())

    def parent(self) -> 'QStandardItem':
        return self._parent

    def setParent(self, parent):
        if self.parent():
            new_clone = self.clone()
            new_clone.setParent(parent)
            self.storage_object.set_tree_view_item(new_clone)
            new_clone.setCheckable(False)
            self.remove()
        else:
            parent.appendRow(self)
            self._parent = parent

    def __hash__(self):
        return hash(self.storage_object) << 8

    def _update(self, *args, **kwargs):
        try:
            self.setCheckState(Qt.Checked if self.storage_object.getStatus() else Qt.Unchecked)
            if self.storage_object.getStatus():
                self.setForeground(QColor(Qt.black))
            else:
                self.setForeground(self.storage_object._color)
            if 'new_child' in kwargs:
                new_child = kwargs['new_child']
                new_child.get_item().setParent(self)
            self.setText(self.storage_object.getName())
        except RuntimeError:
            del self
