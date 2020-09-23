import asyncio
import json
import logging

import aiohttp
import requests

from gqla.abstracts import AbstractExecutor, AbstractRunner


class AsyncRunner(AbstractRunner):

    def __init__(self, properties=None):
        super().__init__()
        self._properties = properties

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value

    def _can_query(self):
        if self._properties.url is None:
            raise AttributeError

    async def run(self, pid, query):
        self._can_query()
        logging.info('Fetch async process {} started'.format(pid))
        async with aiohttp.request('POST', self._properties.url_string, json=query) as resp:
            response = await resp.text()
        logging.info('Fetch async process {} ended'.format(pid))
        return json.loads(response)


class SyncRunner(AbstractRunner):

    def __init__(self, properties=None):
        super().__init__()
        self._properties = properties

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value

    def _can_query(self):
        if self._properties.url is None:
            raise AttributeError

    def run(self, pid, query):
        self._can_query()
        logging.info('Fetch sync process {} started'.format(pid))
        response = requests.post(self._properties.url_string, json=query)
        logging.info('Fetch async process {} ended'.format(pid))
        return json.loads(response.text)


class BasicExecutor(AbstractExecutor):

    def __init__(self, properties=None, storage=None, runner=AsyncRunner()):
        super().__init__()
        self._properties = properties
        self._storage = storage
        self.runner = runner
        runner.properties = properties

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, value):
        self._properties = value
        self.runner.properties = value

    @property
    def storage(self):
        return self._storage.storage if self._storage is not None else None

    @storage.setter
    def storage(self, value):
        self._storage = value

    async def execute(self, pid='N/A', query=None, **kwargs):
        if self._storage is None:
            raise AttributeError
        if query is None:
            raise AttributeError
        if len(kwargs) > 0:
            params = "(" + str(kwargs).replace("'", '').replace('{', '').replace('}', '') + ")"
        else:
            params = ''
        if self.storage is not None:
            if str(query) in self.storage:
                instance = self.storage[query]
                instance.args(params)
                query = instance.query

                query = {
                    'query': self._properties.raw_query.format(query=query)
                }
        futures = [self.runner.run(pid, query=query)]
        done, pending = await asyncio.wait(futures)
        result = done.pop().result()
        return result
