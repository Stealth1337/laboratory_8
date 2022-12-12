from weakref import WeakSet
from uuid import uuid4


class Observer:
    def __init__(self):
        self._observers = WeakSet()
        self.uuid = None

    def addObserver(self, observer):
        self._observers.add(observer)

    def removeObserver(self, observer):
        self._observers.discard(observer)

    def notifyObservers(self, *args, **kwargs):
        self.uuid = uuid4()
        for observer in self._observers:
            observer.update(self, self.uuid, *args, **kwargs)
        self.uuid = None

    def update(self, uuid, *args, **kwargs):
        if uuid != self.uuid:
            self._update(*args, **kwargs)

    def _update(self, *args, **kwargs):
        pass
