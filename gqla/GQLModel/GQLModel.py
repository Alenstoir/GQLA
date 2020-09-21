from gqla.abstracts import GQBaseModel, GQBase


class GQModel(GQBaseModel):

    def __init__(self):
        self._items = {}

    @property
    def items(self):
        return self._items

    def add_item(self, object_inst: GQBase):
        if object_inst is not None:
            self._items[object_inst.name] = object_inst
