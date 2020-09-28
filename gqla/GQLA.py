import asyncio
import json
import logging
import logging.config
import os.path

from gqla.Executor import BasicExecutor, AsyncRunner
from gqla.GQLModel import GQModel
from gqla.GQLStorage import TypeFactory
from gqla.GQQStorage import BasicStorage
from gqla.GQQuery import NormalRule, RecursiveRule, BasicQueryGenerator
from gqla.VerticalStorage import VerticalGeneratorProperties, VerticalUrlProperties
from gqla.abstracts import AbstractStorage, AbstractExecutor
from gqla.statics import INTROSPECTION, BASE_TEMPLATE, RAW


class GQLA:
    __slots__ = ('name', '_subpid', 'usefolder', '_depth', '_folder', '_pretty', '_qStorage', '_executor',
                 '_gen_properties', '_url_properties', '_default_normal_rule', '_default_recursive_rule',
                 '_default_gen', '_basic_runner')

    def __init__(self, name, url=None, port=None, ignore=None, only=None, usefolder=False, recursive_depth=5):
        super().__init__()

        self._executor = None
        self._qStorage = None

        self._basic_runner = AsyncRunner()
        self._gen_properties = VerticalGeneratorProperties()
        self._url_properties = VerticalUrlProperties()
        self._default_normal_rule = NormalRule()
        self._default_recursive_rule = RecursiveRule()
        self._default_gen = BasicQueryGenerator(self._default_normal_rule, self._default_recursive_rule)
        self.qStorage = BasicStorage(self._gen_properties, self._default_gen)
        self.executor = BasicExecutor(self._url_properties, storage=self.qStorage, runner=self._basic_runner)

        self._gen_properties.model = GQModel()
        self._gen_properties.ignore = ignore
        self._gen_properties.only = only
        self._gen_properties.recursive_depth = recursive_depth

        self._url_properties.url = url
        self._url_properties.port = port
        self._url_properties.template = BASE_TEMPLATE
        self._url_properties.introspection = INTROSPECTION
        self._url_properties.raw_query = RAW

        self.usefolder = usefolder
        self._pretty = False
        self.name = name
        self._subpid = 0

        logging.info(' '.join(['CREATED', 'CLASS', str(self.__class__)]))

        if self.usefolder:
            self._folder = os.path.join('', self.name)
            if not os.path.exists(self._folder):
                os.mkdir(self._folder)

    # Getters\Setters

    @property
    def executor(self):
        return self._executor

    @executor.setter
    def executor(self, value: AbstractExecutor):
        self._executor = value

    @property
    def url(self):
        return self._url_properties.url

    @url.setter
    def url(self, value):
        self._url_properties.url = value

    @property
    def port(self):
        return self._url_properties.port

    @port.setter
    def port(self, value):
        self._url_properties.port = value

    @property
    def qStorage(self):
        return self._qStorage

    @qStorage.setter
    def qStorage(self, value: AbstractStorage):
        self._qStorage = value
        if self.executor is not None:
            self.executor.storage = value

    @property
    def ignore(self):
        return self._gen_properties.ignore

    @ignore.setter
    def ignore(self, value):
        self._gen_properties.ignore = value

    @property
    def only(self):
        return self._gen_properties.only

    @only.setter
    def only(self, value):
        self._gen_properties.only = value

    @property
    def recursive_depth(self):
        return self._gen_properties.recursive_depth

    @recursive_depth.setter
    def recursive_depth(self, value):
        self._gen_properties.recursive_depth = value

    @property
    def model(self):
        return self._gen_properties.model

    @model.setter
    def model(self, value):
        self._gen_properties.model = value

    # Getters\Setters

    async def query_one(self, query_name, only_fields=False, usefolder=False, **kwargs):
        query = query_name
        if isinstance(query_name, dict):
            query_name = query_name['query'].split('{')[0].strip(' \n').split(' ')[1]
        if only_fields:
            self.generate_queries(specific=query_name, only_fields=only_fields)
            query_name = query = "only_" + query_name
        logging.info("FETCHING " + query_name + " WITH ARGS " + str(kwargs))
        result = await self.executor.execute(self._subpid, query, **kwargs)
        self._subpid += 1

        if self.usefolder:
            if usefolder:
                filename = os.path.join(self._folder, query_name + '.json')
                logging.info(' '.join(['WRITING', query_name, 'RESULT TO', filename]))
                with open(filename, 'w') as ofs:
                    if self._pretty:
                        indent = 4
                    else:
                        indent = None
                    ofs.write(json.dumps(result, indent=indent))
        return result

    async def introspection(self):
        logging.info(' '.join(['QUERRYING', self.name, 'INTROSPECTION']))
        result = await self.query_one(INTROSPECTION, usefolder=True)
        queries = result['data']['__schema']['types']

        self.create_data(queries)
        self.generate_queries()

    def create_data(self, data):
        for item in data:
            obj = TypeFactory(item)
            if obj is not None:
                self.model.add_item(obj.parse(item))

    def generate_queries(self, specific=False, only_fields=False):
        if 'Query' in self.model.items:
            queries = self.model.items['Query'].fields
        elif 'Queries' in self.model.items:
            queries = self.model.items['Queries'].fields
        else:
            raise NotImplementedError
        if not specific:
            for query in queries:
                self.qStorage.create(query, query, queries[query], self.recursive_depth)
        else:
            for query in queries:
                if query == specific:
                    query_name = query if not only_fields else "only_" + query
                    self.qStorage.create(query_name, query, queries[query], self.recursive_depth, only_fields)

        self.executor._storage = self.qStorage


"""
This file defines main class which is used to generate and query GraphQL queries
All what lies bellow is standalone support 
"""


async def asynchronous():  # Пример работы
    ignore = ['pageInfo', 'deprecationReason', 'isDeprecated', 'cursor', 'parent1', 'id']
    only = ['edges', 'node', 'code', 'name', 'StarObject', 'PlanetObject', 'orbitals']

    helper = GQLA('solar', url='localhost', port='8080', usefolder=True, ignore=ignore, recursive_depth=5)
    helper.only = only
    helper._pretty = True
    await helper.introspection()
    
    result = await helper.query_one('allStellar', usefolder=True, filters={'not': {'objectType': 'planet'}}, first='5')
    print(result)

    result = await helper.query_one('allStellar', usefolder=False, only_fields=True, first='1')
    print(result)

if __name__ == "__main__":
    from gqla.settings import LOGGING_BASE_CONFIG

    logging.getLogger(__name__)
    logging.config.dictConfig(LOGGING_BASE_CONFIG)
    loop_ = asyncio.get_event_loop()
    loop_.run_until_complete(asynchronous())

    loop_.close()
    pass
