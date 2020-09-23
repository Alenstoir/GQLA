from gqla.abstracts import AbstractRule, AbstractGenerator


class NormalRule(AbstractRule):
    def __init__(self):
        super().__init__()
        self._properties = None

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value

    def run(self, item, **kwargs):
        return ""


class RecursiveRule(AbstractRule):
    def __init__(self):
        super().__init__()
        self._properties = None

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value

    def run(self, item, depth=0):
        query = []
        for field in item.fields:
            if item.fields[field].kind == "OBJECT":
                if field in self._properties.ignore:
                    continue
                depth += 1
                subquery_val = item.fields[field].name
                subquery_val = self._properties.model.items[subquery_val]
                subquery_val = self.run(subquery_val, depth)
                depth -= 1
                if subquery_val is None:
                    continue
                query.append((str(field) + ' {' + ' '.join(subquery_val) + '}'))
            else:
                if field in self._properties.ignore:
                    continue
                query.append(field)
                if depth >= self._properties.recursive_depth:
                    return query
        return query


class BasicQueryGenerator(AbstractGenerator):
    def __init__(self, normal: AbstractRule, recursive: AbstractRule, properties=None):
        super().__init__(normal, recursive)
        self._properties = properties
        self.recursive.properties = properties
        self.normal.properties = properties

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value
        self.recursive.properties = value
        self.normal.properties = value

    @property
    def normal(self):
        return self._normal

    @property
    def recursive(self):
        return self._recursive

    def generate(self, item):
        if item.kind == 'OBJECT':
            try:
                subquery_val = self.recursive.run(self._properties.model.items[item.name])
            except RecursionError:
                raise
            return ' {' + ' '.join(subquery_val) + '}'
        else:
            return self.normal.run(self._properties.model.items[item])
