from abc import ABC, abstractmethod


class AbstractGenerator(ABC):

    @abstractmethod
    def __init__(self, normal, recursive):
        self._normal = normal
        self._recursive = recursive

    @property
    @abstractmethod
    def normal(self):
        """Normal rule"""

    @property
    @abstractmethod
    def recursive(self):
        """Recursive rule"""

    @abstractmethod
    def generate(self, *args):
        """Generate statement"""


class AbstractRule(ABC):

    @abstractmethod
    def run(self, *args):
        """Rule runner"""
