from gqla.GQQuery import BasicQuery
from gqla.GQQuery import BasicQueryGenerator, NormalRule, RecursiveRule
from gqla.abstracts import AbstractQuery, AbstractStorage


class BasicStorage(AbstractStorage):

    def __init__(self, properties=None, generator=BasicQueryGenerator(NormalRule(), RecursiveRule())):
        super().__init__()
        self._query = {}
        self.generator = generator
        self._properties = properties
        self.generator.properties = properties

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value
        self.generator.properties = value

    @property
    def storage(self):
        return self._query

    def add(self, name: str, query: AbstractQuery):
        self._query[name] = query

    def create(self, alias, name, item, recursive_depth, only_fields=False):
        query = BasicQuery(name, self.generator, item)
        query.regenerate(only_fields)
        self.add(alias, query)
