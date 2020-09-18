from gqla.GQQuery.Generator.Generator import BasicQueryGenerator
from gqla.GQQuery.abstracts import AbstractQuery


class BasicQuery(AbstractQuery):
    def __init__(self, name=None, generator=None, item=None):
        super().__init__()
        self._body_raw = None
        self._generator = generator
        self._name = name
        self._item = item

    @property
    def body(self):
        return self._body

    @property
    def name(self):
        return self._name

    def set(self, name):
        self._name = name
        self._body = self.generator.generate(self._item)

    @property
    def generator(self):
        return self._generator

    @generator.setter
    def generator(self, value: BasicQueryGenerator):
        self._generator = value

    def args(self, args: list):
        self._args = args

    def regenerate(self):
        self._body = self.generator.generate(self._item)

    @property
    def query(self):
        return self.name + ('(' + str(','.join(self._args)) + ')' if len(self._args) > 0 else "") + self.body
