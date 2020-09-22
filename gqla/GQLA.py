import asyncio
import json

import logging
import logging.config
import os.path

from gqla.Executor import BasicExecutor
from gqla.GQLModel import GQModel
from gqla.GQLStorage import TypeFactory
from gqla.GQQStorage import BasicStorage
from gqla.statics import INTROSPECTION


class GQLA:
    __slots__ = ('_url', '_port', 'name', '_ignore', '_model', '_queries', '_subpid', 'usefolder', 'recursive_depth',
                 '_depth', 'qStorage', 'executor', '_folder', '_pretty')

    def __init__(self, name, url=None, port=None, ignore=None, usefolder=False, recursive_depth=5):
        self._subpid = 0
        self._model = None
        self._ignore = ignore
        self.name = name
        self._url = url
        self._port = port
        self._pretty = False
        self.usefolder = usefolder
        self.recursive_depth = recursive_depth
        self.qStorage = None
        self.executor = BasicExecutor(url, port, self.qStorage)

        logging.info(' '.join(['CREATED', 'CLASS', str(self.__class__)]))

        if self.usefolder:
            self._folder = os.path.join('', self.name)
            if not os.path.exists(self._folder):
                os.mkdir(self._folder)

    def set_ignore(self, ignore_):
        self._ignore = ignore_

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value
        self.executor.url = self._url

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        self.executor.port = self._port

    async def query_one(self, query_name, usefolder=False, **kwargs):
        query = query_name
        if isinstance(query_name, dict):
            query_name = query_name['query'].split('{')[0].strip(' \n').split(' ')[1]
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
        self._model = GQModel()
        for item in data:
            obj = TypeFactory(item)
            if obj is not None:
                self._model.add_item(obj.parse(item))

    def generate_queries(self):
        self.qStorage = BasicStorage()
        if 'Query' in self._model.items:
            queries = self._model.items['Query'].fields
        elif 'Queries' in self._model.items:
            queries = self._model.items['Queries'].fields
        else:
            raise NotImplementedError

        for query in queries:
            self.qStorage.create(query, queries[query], self._model, self._ignore, self.recursive_depth)
        self.executor._storage = self.qStorage


async def asynchronous():  # Пример работы
    ignore = ['pageInfo', 'deprecationReason', 'isDeprecated', 'cursor', 'parent1']

    helper = GQLA('solar', url='localhost', port='8080', usefolder=True, ignore=ignore)
    await helper.introspection()
    result = await helper.query_one('allStellar', usefolder=True, first='5')

    for query in helper.qStorage.storage:
        print(helper.qStorage.storage[query].query)
    print(result)



if __name__ == "__main__":
    from gqla.settings import LOGGING_BASE_CONFIG

    logging.getLogger(__name__)
    logging.config.dictConfig(LOGGING_BASE_CONFIG)
    loop_ = asyncio.get_event_loop()
    loop_.run_until_complete(asynchronous())

    loop_.close()
    pass
