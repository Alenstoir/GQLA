from abc import ABC, abstractmethod
from gqla.abstracts.GQLStorage import GQBase


class GQBaseModel(ABC):

    @property
    @abstractmethod
    def items(self):
        """Item storage"""

    @abstractmethod
    def add_item(self, object_inst: GQBase):
        """Add item to storage"""
