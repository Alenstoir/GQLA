from gqla.GQQuery.Generator.Generator import BasicQueryGenerator, NormalRule, RecursiveRule
from gqla.GQQuery.GQQueriy import BasicQuery
from gqla.GQQuery.abstracts import AbstractQuery
from gqla.GQQStorage.abstracts import AbstractStorage


class BasicStorage(AbstractStorage):

    def __init__(self):
        self._query = {}

    def add(self, name: str, query: AbstractQuery):
        self._query[name] = query

    @property
    def storage(self):
        return self._query

    def create(self, name, item, model, ignore, recursive_depth):
        generator = BasicQueryGenerator(NormalRule(), RecursiveRule(), model, ignore, recursive_depth)
        query = BasicQuery(name, generator, item)
        query.regenerate()
        self.add(name, query)



