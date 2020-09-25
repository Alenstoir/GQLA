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

    def run(self, item, only_fields=False, depth=0, force=False):
        query = []
        for field in item.fields:
            if field in self._properties.ignore:
                continue
            if only_fields:
                if field not in self._properties.only:
                    continue
            if item.fields[field].kind in ["OBJECT", "UNION"]:
                if force or depth <= self._properties.recursive_depth:
                    depth += 1
                    subquery_val = item.fields[field].name
                    subquery_val = self._properties.model.items[subquery_val]
                    subquery_val = self.run(subquery_val, only_fields, depth)
                    depth -= 1
                    if subquery_val is None:
                        continue
                    if item.fields[field].kind == 'UNION':
                        for i in range(len(subquery_val)):
                            subquery_val[i] = '... on ' + subquery_val[i]
                    query.append((str(field) + ' {' + ' '.join(subquery_val) + '}'))
            else:
                if not force:
                    query.append(field)
        if not query:
            return self.run(item, only_fields, depth, force=True)
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

    def generate(self, item, only_fields=False):
        if item.kind == 'OBJECT':
            try:
                subquery_val = self.recursive.run(self._properties.model.items[item.name], only_fields)
            except RecursionError:
                raise
            return ' {' + ' '.join(subquery_val) + '}'
        else:
            return self.normal.run(self._properties.model.items[item])
