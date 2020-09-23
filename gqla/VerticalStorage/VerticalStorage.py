class VerticalGeneratorProperties:
    def __init__(self):
        self._ignore = None
        self._only = None
        self._model = None
        self._recursive_depth = None

    @property
    def recursive_depth(self):
        return self._recursive_depth

    @recursive_depth.setter
    def recursive_depth(self, value):
        self._recursive_depth = value

    @property
    def ignore(self):
        return self._ignore

    @ignore.setter
    def ignore(self, value):
        self._ignore = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def only(self):
        return self._only

    @only.setter
    def only(self, value):
        self._only = value


class VerticalUrlProperties:
    def __init__(self):
        self._url = None
        self._port = None
        self._raw_query = None
        self._template = None
        self._introspection = None

    @property
    def url_string(self):
        return self.template.format(self.url, self.port)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        self._template = value

    @property
    def raw_query(self):
        return self._raw_query

    @raw_query.setter
    def raw_query(self, value):
        self._raw_query = value

    @property
    def introspection(self):
        return self._introspection

    @introspection.setter
    def introspection(self, value):
        self._introspection = value
