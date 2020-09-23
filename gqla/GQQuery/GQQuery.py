from gqla.abstracts import AbstractQuery, AbstractGenerator


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
    def generator(self, value: AbstractGenerator):
        self._generator = value

    def args(self, args: list):
        self._args = args

    def regenerate(self, only_fields):
        self._body = self.generator.generate(self._item, only_fields)

    @property
    def query(self):
        return self.name + (str(self._args) if len(self._args) > 0 else "") + self.body
