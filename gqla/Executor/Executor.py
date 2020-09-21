import asyncio
import json
import logging

import aiohttp
import requests

from gqla.abstracts.abstracts import AbstractExecutor, AbstractRunner


class AsyncRunner(AbstractRunner):

    def __init__(self):
        self.url = None

    def set_url(self, url):
        self.url = url

    def _can_query(self):
        if self.url is None:
            raise AttributeError

    async def run(self, pid, query):
        self._can_query()
        logging.info('Fetch async process {} started'.format(pid))
        async with aiohttp.request('POST', self.url, json=query) as resp:
            response = await resp.text()
        logging.info('Fetch async process {} ended'.format(pid))
        return json.loads(response)


class SyncRunner(AbstractRunner):

    def _can_query(self):
        if self.url is None:
            raise AttributeError

    def __init__(self):
        self.url = None

    def set_url(self, url):
        self.url = url

    def run(self, pid, query):
        self._can_query()
        logging.info('Fetch sync process {} started'.format(pid))
        response = requests.post(self.url, json=query)
        logging.info('Fetch async process {} ended'.format(pid))
        return json.loads(response.text)


class BasicExecutor(AbstractExecutor):

    def __init__(self, url, port, storage, raw="query {{ {query} }}", template="http://{}:{}/graphql", runner=AsyncRunner()):
        self.url = url
        self.port = port
        self._storage = storage
        self.storage = storage.storage if storage is not None else None
        self.QUERY_RAW = raw
        self.URL_TEMPLATE = template
        self.runner = runner
        runner.set_url(self.URL_TEMPLATE.format(self.url, self.port))

    async def execute(self, pid='N/A', query=None, **kwargs):
        if self._storage is not None:
            self.storage = self._storage.storage
        if query is None:
            raise AttributeError
        if len(kwargs) > 0:
            params = "(" + str(kwargs).replace("'", '').replace('{', '').replace('}', '') + ")"
        else:
            params = ''
        if self.storage is not None:
            if query in self.storage:
                instance = self.storage[query]
                instance.args(params)
                query = instance.query
                logging.debug(query)

                query = {
                    'query': self.QUERY_RAW.format(query=query)
                }
        futures = [self.runner.run(pid, query=query)]
        done, pending = await asyncio.wait(futures)
        result = done.pop().result()
        return result




