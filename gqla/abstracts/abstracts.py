from abc import ABC, abstractmethod


class AbstractExecutor(ABC):

    @abstractmethod
    def execute(self, *args):
        """Execute method"""


class AbstractRunner(ABC):

    @abstractmethod
    def run(self, *args):
        """Runner"""

    @abstractmethod
    def set_url(self, url):
        """Url setter"""

    @abstractmethod
    def _can_query(self):
        """Checker"""


class GQBase(ABC):

    @property
    @abstractmethod
    def name(self):
        """Name of stored object"""

    @property
    @abstractmethod
    def kind(self):
        """Kind of object stored"""

    @abstractmethod
    def __init__(self, name, kind):
        self._name = name
        self._kind = kind
        """Initialization with base params"""

    @abstractmethod
    def __repr__(self):
        """Representation of object"""

    @abstractmethod
    def parse(self, item):
        """Parsing an object"""


class GQBaseModel(ABC):

    @property
    @abstractmethod
    def items(self):
        """Item storage"""

    @abstractmethod
    def add_item(self, object_inst: GQBase):
        """Add item to storage"""


class AbstractStorage(ABC):
    @property
    @abstractmethod
    def storage(self):
        """Query to return from storage"""

    @abstractmethod
    def add(self, *args):
        """Add to storage"""

    @abstractmethod
    def create(self, *args):
        """Set query value"""


class AbstractGenerator(ABC):

    @abstractmethod
    def __init__(self, normal, recursive):
        self._normal = normal
        self._recursive = recursive

    @property
    @abstractmethod
    def normal(self):
        """Normal rule"""

    @property
    @abstractmethod
    def recursive(self):
        """Recursive rule"""

    @abstractmethod
    def generate(self, *args):
        """Generate statement"""


class AbstractRule(ABC):

    @abstractmethod
    def run(self, *args):
        """Rule runner"""


class AbstractQuery(ABC):
    @abstractmethod
    def __init__(self):
        self._name = None
        self._body = None
        self._args = []

    @property
    @abstractmethod
    def body(self):
        """Define body"""

    @property
    @abstractmethod
    def name(self):
        """Define name"""

    @abstractmethod
    def set(self, *args):
        """Define setter"""

    @property
    @abstractmethod
    def generator(self):
        """Generator"""

    @property
    @abstractmethod
    def query(self):
        """Define getter"""
