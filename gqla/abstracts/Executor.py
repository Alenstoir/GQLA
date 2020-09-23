from abc import ABC, abstractmethod


class AbstractExecutor(ABC):

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute method"""


class AbstractRunner(ABC):

    @abstractmethod
    def run(self, *args):
        """Runner"""

    @abstractmethod
    def _can_query(self):
        """Checker"""
