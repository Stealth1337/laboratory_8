from abc import ABCMeta
from .tree_view_item import TreeViewItem
from .observer import Observer


class StorageObject(Observer, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self.set_tree_view_item(TreeViewItem(self))

    def set_tree_view_item(self, tree_view_item):
        self.tree_view_item = tree_view_item

    def get_item(self):
        return self.tree_view_item

    def __del__(self):
        self.tree_view_item.remove()
