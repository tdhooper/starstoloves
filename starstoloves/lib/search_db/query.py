from celery.result import AsyncResult
from celery.task.control import revoke


class LastfmQuery(object):

    def __init__(self, id, parser):
        self.id = id
        self.async_result = AsyncResult(id)
        self.parser = parser

    @property
    def status(self):
        return self.async_result.status

    @property
    def results(self):
        if self.async_result.ready():
            data = self.async_result.info
            parsed = self.parser.parse(data)
            return parsed

    def stop(self):
        revoke(self.id)
