from gqla.abstracts import GQBase


class GQField:
    def __init__(self, type_, is_deprecated=False, deprecation_reason=None, description=False, args=None):
        if args is None:
            args = {}
        self.type = type_
        self.is_deprecated = is_deprecated
        self.deprecation_reason = deprecation_reason
        self.description = description
        self.args = {}
        for arg in args:
            self.args[arg.name] = arg


class GQENUM(GQBase):

    def __init__(self, name, kind, description=None, values=None):
        super().__init__(name, kind, description)
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

    def update(self, item, *args):
        values = []
        if 'enumValues' in item:
            for enum in item['enumValues']:
                if enum['name'] not in self.values:
                    values.append(enum['name'])
        self.values = values
        return self

    def parse(self, item, model=None):
        values = []
        if 'enumValues' in item:
            for enum in item['enumValues']:
                values.append(enum['name'])
        self.values = values
        return self


class GQUNION(GQBase):

    def __init__(self, name, kind, description=None):
        super().__init__(name, kind, description)
        self._fields = {}

    def add_field(self, name, field: GQField):
        self._fields[name] = field

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

    @property
    def fields(self):
        return self._fields

    def __repr__(self):
        answer = ','.join(['name: ' + self.name, ' kind:' + self.kind, ' fields:['])
        for field in self.fields.values():
            answer += '... on ' + field.type.name + ' {' + str(field.type) + '},'
        answer = answer.strip(',') + ']'
        return answer
        pass

    def update(self, item, model=None):
        if 'possibleTypes' in item:
            for object_ in item['possibleTypes']:
                if object_['name'] in self.fields:
                    self.fields[object_['name']].type.update(object_, model)
                else:
                    obj = TypeFactory(object_, model)
                    self.add_field(object_['name'], GQField(obj.parse(object_, model)))
        return self

    def parse(self, item, model=None):
        if 'possibleTypes' in item:
            for object_ in item['possibleTypes']:
                obj = TypeFactory(object_, model)
                self.add_field(object_['name'], GQField(obj.parse(object_, model), object_['isDeprecated'],
                                                        object_['deprecationReason']))
        return self


class GQJSON(GQBase):

    def __init__(self, name, kind, description=None):
        super().__init__(name, kind, description)

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

    def __repr__(self):
        pass

    def update(self, item, model=None):
        return self

    def parse(self, item, model=None):
        return self


class GQSCALAR(GQBase):

    def __init__(self, name, kind, description=None):
        super().__init__(name, kind, description)

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

    def __repr__(self):
        answer = ','.join(['name: ' + self.name, ' kind:' + self.kind])
        return answer

    def update(self, item, model=None):
        self._description = item.get('description')
        return self

    def parse(self, item, model=None):
        return self


class GQOBJECT(GQBase):

    @property
    def name(self):
        return self._name

    @property
    def kind(self):
        return self._kind

    def __init__(self, name, kind, description=None):
        super().__init__(name, kind, description)
        self._fields = {}

    @property
    def fields(self):
        return self._fields

    def add_field(self, name, field: GQField):
        self._fields[name] = field

    def __repr__(self):
        answer = ','.join(['name: ' + self.name, ' kind:' + self.kind, ' fields:['])
        for field in self.fields.values():
            answer += '{' + str(field) + '},'
        answer = answer.strip(',') + ']'
        return answer
        pass

    def update(self, item, model=None):
        if 'fields' in item:
            for field in item['fields']:
                obj = TypeFactory(field, model)
                if obj is not None:
                    if field['args']:
                        args = [TypeFactory(arg, model) for arg in field['args']]
                    else:
                        args = {}
                    if field['name'] not in self.fields:
                        self.add_field(field['name'], GQField(obj, field['isDeprecated'], field['deprecationReason'],
                                                              field['description'], args))
                    else:
                        self.fields[field['name']].type.update(field, model)
        return self

    def parse(self, item, model=None):
        if 'fields' in item:
            for field in item['fields']:
                obj = TypeFactory(field, model)
                if obj is not None:
                    if field['args']:
                        args = [TypeFactory(arg, model) for arg in field['args']]
                    else:
                        args = {}
                    self.add_field(field['name'],
                                   GQField(obj, field['isDeprecated'], field['deprecationReason'], field['description'],
                                           args))
        return self


class GQINPUT_OBJECT(GQOBJECT):
    def update(self, item, model=None):
        if 'inputFields' in item:
            for field in item['inputFields']:
                obj = TypeFactory(field, model)
                if obj is not None:
                    if field['name'] not in self.fields:
                        self.add_field(field['name'], GQField(obj, description=field['description']))
                    else:
                        self.fields[field['name']].type.update(field, model)
        return self

    def parse(self, item, model=None):
        if 'inputFields' in item:
            for field in item['inputFields']:
                obj = TypeFactory(field, model)
                if obj is not None:
                    self.add_field(field['name'], GQField(obj, description=field['description']))
        return self


def TypeFactory(kind, model=None):  # noqa
    if 'type' in kind:
        item = kind['type']
    else:
        item = kind
    while True:
        if item['name'] is None:
            item = item['ofType']
        else:
            class_name = item['kind']
            item_name = item['name']
            break
    possibles = globals().copy()
    possibles.update(locals())
    class_instance = possibles.get('GQ' + class_name)
    if not class_instance:
        return None
    if item_name not in model.items:
        obj = class_instance(item_name, class_name, kind.get('description'))
        model.add_item(obj.parse(kind, model))
    else:
        obj = model.items[item_name]
        if kind.get('kind', '') != 'SCALAR' and kind['name'] != item_name:
            return obj
        obj.update(kind, model)
    return obj
