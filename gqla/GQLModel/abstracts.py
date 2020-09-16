from abc import abstractmethod, ABC

from gqla.GQLStorage.abstracts import GQBase


class GQBaseModel(ABC):

    @property
    @abstractmethod
    def items(self):
        """Item storage"""

    @abstractmethod
    def add_item(self, object_inst: GQBase):
        """Add item to storage"""
