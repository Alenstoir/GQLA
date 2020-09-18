from abc import ABC, abstractmethod


class AbstractQuery(ABC):
    @abstractmethod
    def __init__(self):
        self._name = None
        self._body = None
        self._args = []

    @property
    @abstractmethod
    def body(self):
        """Define body"""

    @property
    @abstractmethod
    def name(self):
        """Define name"""

    @abstractmethod
    def set(self, *args):
        """Define setter"""

    @property
    @abstractmethod
    def generator(self):
        """Generator"""

    @property
    @abstractmethod
    def query(self):
        """Define getter"""
