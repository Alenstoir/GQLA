from gqla.abstracts import AbstractRule, AbstractGenerator


class NormalRule(AbstractRule):
    def run(self, item):
        return ""


class RecursiveRule(AbstractRule):
    def run(self, item, vault=None, ignore=None, recursive_depth=5, depth=0):
        query = []
        for field in item.fields:
            if item.fields[field].kind == "OBJECT":
                if field in ignore:
                    continue
                depth += 1
                subquery_val = item.fields[field].name
                subquery_val = vault.items[subquery_val]
                subquery_val = self.run(subquery_val, vault, ignore, depth, recursive_depth)
                depth -= 1
                if subquery_val is None:
                    continue
                query.append((str(field) + ' {' + ' '.join(subquery_val) + '}'))
            else:
                if field in ignore:
                    continue
                query.append(field)
                if depth >= recursive_depth:
                    return query
        return query


class BasicQueryGenerator(AbstractGenerator):
    def __init__(self, normal: AbstractRule, recursive: AbstractRule, vault, ignore, recursive_depth):
        super().__init__(normal, recursive)
        self.vault = vault
        self.ignore = ignore
        self.recursive_depth = recursive_depth

    @property
    def normal(self):
        return self._normal

    @property
    def recursive(self):
        return self._recursive

    def generate(self, item):
        if item.kind == 'OBJECT':
            try:
                subquery_val = self.recursive.run(self.vault.items[item.name], self.vault, self.ignore, self.recursive_depth)
            except RecursionError:
                raise
            return ' {' + ' '.join(subquery_val) + '}'
        else:
            return self.normal.run(self.vault.items[item])
