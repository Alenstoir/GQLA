from abc import ABC, abstractmethod


class AbstractExecutor(ABC):

    @abstractmethod
    def execute(self, *args):
        """Execute method"""


class AbstractRunner(ABC):

    @abstractmethod
    def run(self, *args):
        """Runner"""

    @abstractmethod
    def set_url(self, url):
        """Url setter"""

    @abstractmethod
    def _can_query(self):
        """Checker"""
