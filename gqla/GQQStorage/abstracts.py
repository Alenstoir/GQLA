from abc import ABC, abstractmethod


class AbstractStorage(ABC):
    @property
    @abstractmethod
    def storage(self):
        """Query to return from storage"""

    @abstractmethod
    def add(self, *args):
        """Add to storage"""

    @abstractmethod
    def create(self, *args):
        """Set query value"""

