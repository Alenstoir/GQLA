from abc import ABC, abstractmethod


class GQBase(ABC):

    @property
    @abstractmethod
    def name(self):
        """Name of stored object"""

    @property
    @abstractmethod
    def kind(self):
        """Kind of object stored"""

    @abstractmethod
    def __init__(self, name, kind):
        self._name = name
        self._kind = kind
        """Initialization with base params"""

    @abstractmethod
    def __repr__(self):
        """Representation of object"""

    @abstractmethod
    def parse(self, item):
        """Parsing an object"""
