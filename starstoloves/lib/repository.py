class RepositoryItem(object):

    def __init__(self, **kwargs):
        if 'repository' in kwargs:
            self.repository = kwargs['repository']
