from celery.result import AsyncResult
from celery.task.control import revoke

from .result import LastfmResultParser


class LastfmQuery(object):

    def __init__(self, id):
        self.id = id
        self.async_result = AsyncResult(id)
        self.parser = LastfmResultParser()

    @property
    def status(self):
        return self.async_result.status

    @property
    def response_data(self):
        if self.async_result.ready():
            return self.async_result.info

    @property
    def results(self):
        if self.response_data:
            parsed = self.parser.parse(self.response_data)
            return parsed

    def stop(self):
        revoke(self.id)
