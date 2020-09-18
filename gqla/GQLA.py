import asyncio
import json

import aiohttp
import logging
import logging.config
import os.path

from gqla.GQLModel.GQLModel import GQModel
from gqla.GQLStorage.GQLStorage import TypeFactory
from gqla.GQQStorage.GQQStorage import BasicStorage


class GQLA:
    __slots__ = ('url', 'port', 'name', '_ignore', '_model', '_queries', '_subpid', 'usefolder', 'recursive_depth',
                 '_depth', 'qStorage')

    URL_TEMPLATE = "http://{}:{}/graphql"

    QUERY_RAW = """
                    query {{
                        {query}
                    }}
                """

    INTROSPECTION = {
        'query': '\n    query IntrospectionQuery {\n      __schema {\n        queryType { name }\n        '
                 'mutationType { name }\n        subscriptionType { name }\n        types {\n          ...FullType\n  '
                 '      }\n        directives {\n          name\n          description\n          locations\n         '
                 ' args {\n            ...InputValue\n          }\n        }\n      }\n    }\n\n    fragment FullType '
                 'on __Type {\n      kind\n      name\n      description\n      fields(includeDeprecated: true) {\n   '
                 '     name\n        description\n        args {\n          ...InputValue\n        }\n        type {'
                 '\n          ...TypeRef\n        }\n        isDeprecated\n        deprecationReason\n      }\n      '
                 'inputFields {\n        ...InputValue\n      }\n      interfaces {\n        ...TypeRef\n      }\n    '
                 '  enumValues(includeDeprecated: true) {\n        name\n        description\n        isDeprecated\n  '
                 '      deprecationReason\n      }\n      possibleTypes {\n        ...TypeRef\n      }\n    }\n\n    '
                 'fragment InputValue on __InputValue {\n      name\n      description\n      type { ...TypeRef }\n   '
                 '   defaultValue\n    }\n\n    fragment TypeRef on __Type {\n      kind\n      name\n      ofType {'
                 '\n        kind\n        name\n        ofType {\n          kind\n          name\n          ofType {'
                 '\n            kind\n            name\n            ofType {\n              kind\n              '
                 'name\n              ofType {\n                kind\n                name\n                ofType {'
                 '\n                  kind\n                  name\n                  ofType {\n                    '
                 'kind\n                    name\n                  }\n                }\n              }\n           '
                 ' }\n          }\n        }\n      }\n    }\n  ',
        'variables': {}, 'operationName': None}

    def __init__(self, name, url=None, port=None, ignore=None, usefolder=False, recursive_depth=5):
        self._subpid = 0
        self._model = None
        self._ignore = ignore
        self.name = name
        self.url = url
        self.port = port
        self.usefolder = usefolder
        self.recursive_depth = recursive_depth
        self.qStorage = None

        logging.info(' '.join(['CREATED', 'CLASS', str(self.__class__)]))

    def set_ignore(self, ignore_):
        self._ignore = ignore_

    def _can_query(self):
        if self.url is None or self.port is None or self.name is None:
            raise AttributeError

    @staticmethod
    async def fetch_async(pid, url, query):
        logging.info('Fetch async process {} started'.format(pid))
        async with aiohttp.request('POST', url, json=query) as resp:
            response = await resp.text()
        logging.info('Fetch async process {} ended'.format(pid))
        return json.loads(response)

    async def query_one(self, query_name, to_file=False, **kwargs):
        instance = self.qStorage.storage[query_name]
        self._can_query()
        logging.info(' '.join(['QUERRYING', query_name, 'WITH PARAMS', str(kwargs)]))
        if len(kwargs) > 0:
            params = "(" + str(kwargs).replace("'", '').replace('{', '').replace('}', '') + ")"
        else:
            params = ''
        instance.args(params)
        query = {
            'query': self.QUERY_RAW.format(query=instance.query)
        }
        logging.info(query)

        futures = [self.fetch_async(self._subpid, self.URL_TEMPLATE.format(self.url, self.port), query=query)]
        self._subpid += 1

        done, pending = await asyncio.wait(futures)
        result = done.pop().result()
        if self.usefolder:
            if to_file:
                folder = os.path.join('', self.name)
                filename = os.path.join(folder, '_' + query_name + '.json')
                logging.info(' '.join(['WRITING', query_name, 'RESULT TO', filename]))
                if not os.path.exists(folder):
                    os.mkdir(folder)
                with open(filename, 'w') as ofs:
                    ofs.write(json.dumps(result, indent=4))
        return result

    async def introspection(self):
        self._can_query()

        logging.info(' '.join(['QUERRYING', self.name, 'INTROSPECTION']))

        futures = [self.fetch_async(self._subpid, self.URL_TEMPLATE.format(self.url, self.port), self.INTROSPECTION)]
        self._subpid += 1

        done, pending = await asyncio.wait(futures)
        result = done.pop().result()

        queries = result['data']['__schema']['types']

        if self.usefolder:
            folder = os.path.join('', self.name)
            if not os.path.exists(folder):
                os.mkdir(folder)
            with open(os.path.join(folder, 'model.json'), 'w') as ofs:
                ofs.write(json.dumps(queries, indent=4))

        self.create_data(queries)
        self.generate_queries()

    def create_data(self, data):
        self._model = GQModel()
        for item in data:
            obj = TypeFactory(item)
            if obj is not None:
                self._model.add_item(obj.parse(item))

    def generate_queries(self, specific=False):
        self.qStorage = BasicStorage()
        if 'Query' in self._model.items:
            queries = self._model.items['Query'].fields
        elif 'Queries' in self._model.items:
            queries = self._model.items['Queries'].fields
        else:
            raise NotImplementedError

        for query in queries:
            self.qStorage.create(query, queries[query], self._model, self._ignore, self.recursive_depth)


async def asynchronous():  # Пример работы
    helper = GQLA('solar', usefolder=True)
    helper.url = 'localhost'
    helper.port = '8080'

    ignore = ['pageInfo', 'deprecationReason', 'isDeprecated', 'cursor', 'parent1']

    helper.set_ignore(ignore)

    await helper.introspection()

    for query in helper.qStorage.storage:
        print(helper.qStorage.storage[query].query)
    result = await helper.query_one('allPlanets')
    print(result)


if __name__ == "__main__":
    from gqla.settings import LOGGING_BASE_CONFIG

    logging.getLogger(__name__)
    logging.config.dictConfig(LOGGING_BASE_CONFIG)
    loop_ = asyncio.get_event_loop()
    loop_.run_until_complete(asynchronous())

    loop_.close()
    pass
