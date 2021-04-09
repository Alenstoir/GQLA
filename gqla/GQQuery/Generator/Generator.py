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
        deprecated = False
        for field in item.fields:
            if item.fields[field].is_deprecated:
                deprecated = item.fields[field].is_deprecated
            if field in self._properties.ignore:
                continue
            if only_fields:
                if field not in self._properties.only:
                    continue
            if item.fields[field].type.kind in ["OBJECT", "UNION"]:
                if force or depth <= self._properties.recursive_depth:
                    depth += 1
                    subquery_val = item.fields[field].type.name
                    subquery_val = self._properties.model.items[subquery_val]
                    subquery_val, deprecated_deep = self.run(subquery_val, only_fields, depth)
                    if deprecated_deep:
                        deprecated = deprecated_deep
                    depth -= 1
                    if subquery_val is None:
                        continue
                    if item.fields[field].type.kind == 'UNION':
                        for i in range(len(subquery_val)):
                            subquery_val[i] = '... on ' + subquery_val[i]
                    query.append((str(field) + ' {' + ' '.join(subquery_val) + '}'))
            else:
                if not force:
                    query.append(field)
        if not query:
            return self.run(item, only_fields, depth, force=True)
        return query, deprecated


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
        args_deprecated = False
        for entry in item.args.values():
            args_deprecated = args_deprecated or args_tree_walk_for_deprecations(entry)
        if item.is_deprecated:
            args_deprecated = True
        if item.type.kind == 'OBJECT':
            try:
                subquery_val, deprecated = self.recursive.run(self._properties.model.items[item.type.name], only_fields)
                args_deprecated = args_deprecated or deprecated
            except RecursionError:
                raise
            return ' {' + ' '.join(subquery_val) + '}', args_deprecated
        else:
            return self.normal.run(self._properties.model.items[item.type.name]), args_deprecated


def args_tree_walk_for_deprecations(entry, depth=0):
    depth += 1
    if depth >= 4:
        return False
    deprecated = False
    if hasattr(entry, 'description'):
        description = entry.description
    elif hasattr(entry, '_description'):
        description = entry._description
    else:
        description = None
    if 'deprecated' in str(description).lower():
        return True
    if hasattr(entry, 'fields'):
        deprecates = []
        for name, field in entry.fields.items():
            if 'deprecated' in str(field.description).lower():
                return True
            deprecates.append(args_tree_walk_for_deprecations(field.type, depth))
        deprecated = deprecated or any(deprecates)
    return deprecated
