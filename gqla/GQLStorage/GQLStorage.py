import logging

from gqla.GQLStorage.abstracts import GQBase


class GQENUM(GQBase):

    def __init__(self, name, kind, values=None):
        super().__init__(name, kind)
        self.values = values

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

    def __repr__(self):
        answer = ','.join(['name: ' + self.name, ' kind:' + self.kind, ' values:' + str(self.values)])
        return answer

    def parse(self, item):
        values = []
        if 'enumValues' in item:
            for enum in item['enumValues']:
                values.append(enum['name'])
        self.values = values
        # enum = GQENUM(item['name'], item['kind'], values)
        return self


class GQJSON(GQBase):

    def __init__(self, name, kind):
        super().__init__(name, kind)

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

    def __repr__(self):
        pass

    def parse(self, item):
        return self


class GQSCALAR(GQBase):

    def __init__(self, name, kind):
        super().__init__(name, kind)

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

    def __repr__(self):
        answer = ','.join(['name: ' + self.name, ' kind:' + self.kind])
        return answer

    def parse(self, item):
        return self


class GQOBJECT(GQBase):

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

    def __init__(self, name, kind):
        super().__init__(name, kind)
        self.fields = {}

    def add_field(self, name, field: GQBase):
        self.fields[name] = field

    def __repr__(self):
        answer = ','.join(['name: ' + self.name, ' kind:' + self.kind, ' fields:['])
        for field in self.fields:
            answer += '{' + str(self.fields[field]) + '},'
        answer = answer.strip(',') + ']'
        return answer

    def parse(self, item):
        # def parse_nested_object(subitem):
        #     sub_object_instance = TypeFactory(subitem)
        #     return sub_object_instance
        if 'fields' in item:
            for field in item['fields']:
                kind = field['type']
                while True:
                    if kind['name'] is None:
                        kind = kind['ofType']
                    else:
                        obj = TypeFactory(kind)
                        if obj is not None:
                            self.add_field(field['name'], obj.parse(kind))
                        # if kind['kind'] == 'OBJECT':
                        #     object_instance.add_field(field['name'], parse_nested_object(kind))
                        # if kind['kind'] == 'ENUM':
                        #     object_instance.add_field(field['name'], parse_enum(kind))
                        # elif kind['kind'] == 'SCALAR':
                        #     object_instance.add_field(field['name'], parse_scalar(kind))
                        break
        return self


def TypeFactory(kind): # noqa
    # print(kind)
    class_name = kind['kind']  # set by the command line options
    possibles = globals().copy()
    possibles.update(locals())
    class_instance = possibles.get('GQ' + class_name)
    if not class_instance:
        # logging.error(NotImplementedError("Class %s not implemented" % class_name))
        # raise NotImplementedError("Class %s not implemented" % class_name)
        return None
    obj = class_instance(kind['name'], kind['kind'])
    return obj
