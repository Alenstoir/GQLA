import asyncio
import json

import aiohttp
import logging
import logging.config

from settings import LOGGING_BASE_CONFIG

logging.getLogger(__name__)
logging.config.dictConfig(LOGGING_BASE_CONFIG)


class GQLA:
    __slots__ = ('url', 'port', 'name', '_ignore', '_model', '_queries', '_subpid')

    URL_TEMPLATE = "http://{}:{}/graphql"

    QUERY_RAW = """
                    query {{
                        {query} {fields}
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

    def __init__(self, name, url=None, port=None, ignore=None):
        self._subpid = 0
        self._model = None
        self._queries = {}
        self._ignore = ignore
        self.name = name
        self.url = url
        self.port = port

        logging.info(' '.join(['CREATED', 'CLASS', str(self.__class__)]))

    def set_ignore(self, ignore_):
        self._ignore = ignore_

    def can_query(self):
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
        self.can_query()
        logging.info(' '.join(['QUERRYING', query_name, 'WITH PARAMS', str(kwargs)]))
        if len(kwargs) > 0:
            params = "(" + str(kwargs).replace("'", '').replace('{', '').replace('}', '') + ")"
        else:
            params = ''
        query = {
            'query': self.QUERY_RAW.format(query='{}{}'.format(query_name, params), fields=self._queries[query_name])}

        futures = [self.fetch_async(self._subpid, self.URL_TEMPLATE.format(self.url, self.port), query=query)]
        self._subpid += 1

        done, pending = await asyncio.wait(futures)
        result = done.pop().result()
        if to_file:
            filename = str(self.name) + '_' + query_name + '.json'
            logging.info(' '.join(['WRITING', query_name, 'RESULT TO', filename]))
            with open(filename, 'w') as ofs:
                ofs.write(json.dumps(result, indent=4))
        return result

    async def introspection(self):
        self.can_query()

        logging.info(' '.join(['QUERRYING', self.name, 'INTROSPECTION']))

        futures = [self.fetch_async(self._subpid, self.URL_TEMPLATE.format(self.url, self.port), self.INTROSPECTION)]
        self._subpid += 1

        done, pending = await asyncio.wait(futures)
        result = done.pop().result()

        queries = result['data']['__schema']['types']

        with open(str(self.name) + '.json', 'w') as ofs:
            ofs.write(json.dumps(queries, indent=4))

        self.create_data(queries)
        self.generate_queries()

    def create_data(self, data):
        self._model = GQModel()
        for item in data:
            if item['kind'] == 'ENUM':
                self._model.add_enum(parse_enum(item))
            elif item['kind'] == 'SCALAR':
                self._model.add_scalar(parse_scalar(item))
            elif item['kind'] == 'OBJECT':
                obj = parse_object(item)
                self._model.add_object(obj)

    def generate_queries(self, specific=False):
        if 'Query' in self._model.objects:
            queries = self._model.objects['Query'].fields
        elif 'Queries' in self._model.objects:
            queries = self._model.objects['Queries'].fields
        else:
            raise NotImplementedError
        query_str = {}
        for query in queries:
            if queries[query].kind == 'OBJECT':
                subquery_val = self.subquery(self._model.objects[queries[query].name])
                query_str[query] = ' {' + ' '.join(subquery_val) + '}'
        self._queries = query_str

    def subquery(self, item):
        query = []
        for field in item.fields:
            if item.fields[field].kind == "OBJECT":
                if field in self._ignore:
                    continue
                subquery_val = item.fields[field].name
                subquery_val = self._model.objects[subquery_val]
                subquery_val = self.subquery(subquery_val)
                query.append((str(field) + ' {' + ' '.join(subquery_val) + '}'))
            else:
                if field in self._ignore:
                    continue
                query.append(field)
        return query


class GQBase:
    __slots__ = ('name', 'kind')

    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

    def __repr__(self):
        answer = ','.join(['kind: ' + self.kind, ' name: ' + self.name])
        return answer


class GQEnum(GQBase):
    __slots__ = ('name', 'kind', 'values')

    def __init__(self, name, kind, values=None):
        super().__init__(name, kind)
        self.values = values

    def __repr__(self):
        answer = ','.join(['name: ' + self.name, ' kind:' + self.kind, ' values:' + str(self.values)])
        return answer


class GQScalar(GQBase):
    __slots__ = ('name', 'kind')

    def __init__(self, name, kind):
        super().__init__(name, kind)

    def __repr__(self):
        answer = ','.join(['name: ' + self.name, ' kind:' + self.kind])
        return answer


class GQObject(GQBase):
    __slots__ = ('name', 'kind', 'fields', 'nested')

    def __init__(self, kind, name):
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


class GQModel:
    __slots__ = ('_scalars', 'queries', 'objects', '_enums', '_ignore')

    def __init__(self):
        self._scalars = {}
        self.queries = ''
        self.objects = {}
        self._enums = {}

    def add_object(self, object_inst: GQObject):
        self.objects[object_inst.name] = object_inst

    def add_scalar(self, scalar: GQScalar):
        self._scalars[scalar.name] = scalar

    def add_enum(self, enum: GQEnum):
        self._scalars[enum.name] = enum

    def set_queries(self, filename: str):
        self.queries = filename


def parse_enum(item):
    values = []
    if 'enumValues' in item:
        for enum in item['enumValues']:
            values.append(enum['name'])
    enum = GQEnum(item['name'], item['kind'], values)
    return enum


def parse_scalar(item):
    scalar = GQScalar(item['name'], item['kind'])
    return scalar


def parse_nested_object(item):
    object_instance = GQObject(item['kind'], item['name'])
    return object_instance


def parse_object(item):
    object_instance = GQObject(item['kind'], item['name'])

    if 'fields' in item:
        for field in item['fields']:
            kind = field['type']
            while True:
                if kind['name'] is None:
                    kind = kind['ofType']
                else:
                    if kind['kind'] == 'OBJECT':
                        obj = parse_nested_object(kind)
                        object_instance.add_field(field['name'], obj)
                    if kind['kind'] == 'ENUM':
                        object_instance.add_field(field['name'], parse_enum(kind))
                    elif kind['kind'] == 'SCALAR':
                        object_instance.add_field(field['name'], parse_scalar(kind))
                    break
    return object_instance


async def asynchronous():
    helper = GQLA('ship')
    helper.url = '10.10.127.19'
    helper.port = '8086'

    ignore = ['pageInfo', 'deprecationReason', 'isDeprecated', 'cursor']

    helper.set_ignore(ignore)

    await helper.introspection()

    logging.info(' '.join(['QUERRY vesselTypes RESULT:', str(await helper.query_one('vesselTypes', to_file=True))]))
    logging.info(' '.join(['QUERRY vesselTypes RESULT:', str(await helper.query_one('civilVesselsData', to_file=True, onlyIdentified='false', first=1))]))
    logging.info(' '.join(['QUERRY vesselTypes RESULT:', str(await helper.query_one('shipData', to_file=True, onlyIdentified='false', first=20))]))


if __name__ == "__main__":
    loop_ = asyncio.get_event_loop()
    loop_.run_until_complete(asynchronous())

    loop_.close()
    pass

# URL_DEVEL = "http://10.10.127.19:8088/graphql"
# MAX_CLIENTS = 1


# SUBQUERY = "{subquery_name} {{ {subquery_fields} }}"
# FLAG = SUBQUERY.format(subquery_name='flag', subquery_fields='ksm shortName name alfa2 alfa3')
# COUNTRY = SUBQUERY.format(subquery_name='country', subquery_fields='ksm shortName name alfa2 alfa3')
# VESSEL_TYPE = SUBQUERY.format(subquery_name='vesselType', subquery_fields='vesselTypeEn vesselTypeRu')
# FLEET = SUBQUERY.format(subquery_name='fleet', subquery_fields='fcUuid abbreviation name region')
# KEUZ = SUBQUERY.format(subquery_name='keuzClassifier', subquery_fields='clsfObjId relationTypeId kodKeuz')
# PROJECT = SUBQUERY.format(subquery_name='project', subquery_fields='fc_Uuid TKPrjtthCode TKPrjtthKodprj TKPrjtthName TKPrjtthVmfcl TKPrjtthIgcl TKPrjtthDl TKPrjtthSh TKPrjtthOs TKPrjtthVistd TKPrjtthVipln TKPrjtthVin TKPrjtthVip TKPrjtthGrp TKPrjtthSpn TKPrjtthSpp TKPrjtthDaln TKPrjtthDalp TKPrjtthGl TKPrjtthCh TKPrjtthAvt TKPrjtthVoor TKPrjtthRgav  TKPrjtthDes TKPrjtthPrim TKPrjtthBegda TKPrjtthEndda TKPrjtthPr')
# MODEL3D = SUBQUERY.format(subquery_name='model3d', subquery_fields='urlImg urlModel urlWaterlineModel urlWaterlineImg swiftUrlModel swiftUrlWaterlineModel swiftUrlImg swiftUrlWaterlineImg fileModel fileWaterlineModel fileImg fileWaterlineImg')
# QUERY_RAW = """
#                 query {{
#                     {query} {{
#                         {fields}
#                         {subquery}
#                     }}
#                 }}
#             """
#
# CIVIL_FIELDS = ['imo',
#                 'mmsi',
#                 'name',
#                 'formerNames',
#                 'operatingStatus',
#                 'grossTonnage',
#                 'deadweight',
#                 'length',
#                 'breadth',
#                 'length',
#                 'engineType',
#                 'engineModel',
#                 'enginePower',
#                 'yearOfBuild',
#                 'builder',
#                 'classificationSociety',
#                 'homePort',
#                 'owner',
#                 'manager',
#                 'vesselTypeId',
#                 'ksm',
#                 'captain',
#                 VESSEL_TYPE,
#                 FLAG]
# MILITARY_FIELDS = ['fc_Uuid',
#                    'TKKplvmfCode',
#                    'TKKplvmfName',
#                    'TKKplvmfNamec',
#                    'TKKplvmfNom',
#                    'TKKplvmfPpb',
#                    'TKKplvmfDatvv',
#                    'TKKplvmfSost',
#                    'TKKplvmfBegda',
#                    'TKKplvmfEndda',
#                    'TKKplvmfPr',
#                    'TKKplvmfFl',
#                    'TKKpligKsm',
#                    'TKKpligNameclat',
#                    'TKKpligCodealt',
#                    'TKKplvmfInd',
#                    'TKPrjtthCode',
#                    'TKPrjtthVmfcl',
#                    'commonClassifierId',
#                    'relationTypeId',
#                    'nameShort',
#                    'abbreviation',
#                    'serviceTime',
#                    'technicalReadinessName',
#                    'technicalReadinessEvent',
#                    'alertName',
#                    'alertWhoseOrder',
#                    'alertOrderNum',
#                    'alertOrderDate',
#                    FLEET,
#                    COUNTRY,
#                    PROJECT,
#                    KEUZ,
#                    MODEL3D]

# def civil_query():
#     civil_fields = (' '.join(CIVIL_FIELDS))
#     civil_node = SUBQUERY.format(subquery_name='node', subquery_fields=civil_fields)
#     civil_edge = SUBQUERY.format(subquery_name='edges', subquery_fields=civil_node)
#     return {'query': QUERY_RAW.format(query=' civilVesselsData(onlyIdentified: false)',
#                                       fields='', subquery=civil_edge)}


# def military_query():
#     military_fields = (' '.join(MILITARY_FIELDS))
#     military_node = SUBQUERY.format(subquery_name='node', subquery_fields=military_fields)
#     military_edge = SUBQUERY.format(subquery_name='edges', subquery_fields=military_node)
#     return {'query': QUERY_RAW.format(query=' shipData(onlyIdentified: false)',
#                                       fields='', subquery=military_edge)}


# async def introspection(url, ignore):
#     queries = []
#     futures = [fetch_async(0, url, INTROSPECTION)]
#     done, pending = await asyncio.wait(futures)
#     result = done.pop().result()
#     queries = result['data']['__schema']['types']
#     # print(result)
#     with open('query.json', 'w') as ofs:
#         ofs.write(json.dumps(queries, indent=4))
#     # for item in queries:
#     #     print(item)
#     model = create_data(queries, ignore)
#     generate_queries(model)
#     return queries

# def subquery(item, vault, ignore):
#     query = []
#     for field in item.fields:
#         if item.fields[field].kind == "OBJECT":
#             if field in ignore:
#                 continue
#             subquery_val = item.fields[field].name
#             subquery_val = vault.objects[subquery_val]
#             subquery_val = subquery(subquery_val, vault, ignore)
#             query.append((str(field) + ' {' + ' '.join(subquery_val) + '}'))
#         else:
#             query.append(field)
#     return query


# def generate_queries(model, specific=False):
#     ignore = model._ignore
#     if 'Query' in model.objects:
#         queries = model.objects['Query'].fields
#     elif 'Queries' in model.objects:
#         queries = model.objects['Queries'].fields
#     else:
#         raise NotImplementedError
#     query_str = {}
#     for query in queries:
#         if queries[query].kind == 'OBJECT':
#             subquery_val = subquery(model.objects[queries[query].name], model, ignore)
#             query_str[query] = ' {' + ' '.join(subquery_val) + '}'
#             # print(model.objects[queries[query].name])
#             # print(query, queries[query])
#     for entry in query_str:
#         print(entry, query_str[entry])


# def create_data(data, ignore):
#     # print(data)
#     model = GQModel()
#     model.set_ignore(ignore)
#     for item in data:
#         if item['kind'] == 'ENUM':
#             model.add_enum(parse_enum(item))
#         elif item['kind'] == 'SCALAR':
#             model.add_scalar(parse_scalar(item))
#         elif item['kind'] == 'OBJECT':
#             obj = parse_object(item)
#             # print(repr(obj))
#             model.add_object(obj)
#     return model


# args = []
# subqueries = []
# print(query['name'])
# for item in query['args']:
#     args.append([item['name'], item['type']])
# for item in query['type']:
#     subqueries.append(item)
# print(query)


# async def create_query(query):
#     print(json.dumps(query, indent=4))
#     args = []
#     subqueries = []
#     print(query['name'])
#     for item in query['args']:
#         args.append([item['name'], item['type']])
#     for item in query['type']:
#         subqueries.append(item)
#     print(query)


# async def fetch_async(pid, url, query):
#     print('Fetch async process {} started'.format(pid))
#     async with aiohttp.request('POST', url, json=query) as resp:
#         response = await resp.text()
#     return json.loads(response)


# async def asynchronous(type_):
#     civil_string = civil_query()
#     military_string = military_query()
#     results = []
#     futures = [fetch_async(i, URL_DEVEL, civil_string if type_ == 'civ' else military_string) for i in
#                range(1, MAX_CLIENTS + 1)]
#     done, pending = await asyncio.wait(futures)
#     for i in range(1, MAX_CLIENTS + 1):
#         results.append(done.pop().result())
#     print(results)
#     return results
